# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2023 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import DataIO

from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")

from amoco.system.structs import StructDefine, StructFactory, StructureError
from amoco.system.structs import StructFormatter, token_bytes_fmt
import xml.etree.ElementTree as ET


# GDB trace file format.
# ------------------------------------------------------------------------------

class GDBTrace(object):
    def __init__(self, f):
        self.dataio = data = DataIO(f)
        eof = data.size()
        offset = 0
        self.header = GDBTraceHeader(data,offset)
        offset += len(self.header)
        self.descr = GDBTraceDescr(data,offset)
        offset += self.descr.size()
        self.frames = []
        if (n:=self.descr.status.traceframe_count()) > 0:
            for _ in range(n):
                self.frames.append(GDBTraceFrame(data,offset))
                # use len(...) not .size() because a GDBTraceFrame is
                # a variable length structure so we actually want the
                # effective unpacked length rather than the class-level
                # infinite length.
                offset += len(self.frames[-1])

    def get_register_block_struct(self):
        conv = {8:'B',16:'H',32:'I',64:'Q',80:'B*10',128:'Q*2'}
        regs = [r for r in self.descr.target.iter("reg")]
        fmt = ["%s : %s"%(conv[int(r.attrib['bitsize'])],r.attrib['name']) for r in regs]
        if len(fmt)>0:
            return StructFactory("Registers","\n".join(fmt),packed=True)
        else:
            return None

    def get_code_ptr(self):
        code_ptr = [r for r in self.descr.target.iter("reg") if r.attrib['type']=='code_ptr']
        assert len(code_ptr)==1
        return code_ptr[0]

    def get_tracepoint_frame_by_address(self,address):
        code_ptr = self.get_code_ptr()
        name = code_ptr.attrib['name']
        struct_R = self.get_register_block_struct()
        if struct_R is not None:
            for tp in self.descr.tp:
                for fr in self.frames:
                    if fr.frame_type==b'R' and fr.number==tp.number:
                        if not hasattr(fr,'regs'):
                            fr.regs = struct_R().unpack(data=fr.raw,offset=1)
                        if address==fr.regs[name]:
                            return (tp,fr)
        return (None,None)

    def get_collected_registers(self,tpnum,frame=None,*args):
        struct_R = self.get_register_block_struct()
        if struct_R is not None:
            for tp in self.descr.tp:
                if tp.number != tpnum:
                    continue
                col = []
                found = frame is None
                for fr in self.frames:
                    if not found and (fr is frame):
                        found = True
                    if found and fr.frame_type==b'R' and fr.number==tp.number:
                        if not hasattr(fr,'regs'):
                            fr.regs = struct_R().unpack(data=fr.raw,offset=1)
                        D = {}
                        for r in args:
                            D[r] = fr.regs[r]
                        col.append(D)
                return col
        return None




@StructDefine(
"""
B  : magic
c*5: kind
c  : version
c  : eol
"""
)
class GDBTraceHeader(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.func_formatter(magic=token_bytes_fmt)
        if data is not None:
            self.unpack(data,offset)
            if self.magic != 0x7f or self.kind != b'TRACE':
                    raise StructureError("not a gdb trace file ?")

class GDBTraceDescr(object):
    def __init__(self, data=None, offset=0):
        begpos = offset
        done = False
        descr = b''
        data.seek(offset)
        while not done:
            l = data.readline()
            if len(l)==1:
                descr += l
                done = True
            else:
                descr += l
        self._descr = descr
        # now make sense of this descr:
        self.reg_blk_sz = None
        self.status = None
        self.tp = []
        self.tsv = []
        tdesc = b''
        for l in self._descr.split(b'\n'):
            if l.startswith(b'R '):
                if self.reg_blk_sz is None:
                    self.reg_blk_sz = int(l[2:],16)
                else:
                    logger.warn("gdb trace register block is already defined")
            elif l.startswith(b'status '):
                if self.status is None:
                    self.status = qTStatus(l,7)
                else:
                    logger.warn("gdb trace status is already defined")
            elif l.startswith(b'tp '):
                self.tracepoint(l,3)
            elif l.startswith(b'tsv '):
                self.tsv.append(TraceStateVariable(l[4:]))
            elif l.startswith(b'tdesc '):
                tdesc += l[6:]
        self.tdesc = tdesc
        self.target = ET.fromstring(tdesc)

    def tracepoint(self,l,offset):
        l = l[offset:]
        if l.startswith(b'T'):
            self.tp.append(TracePoint(l))
        else:
            self.tp[-1].define(l)

    def __len__(self):
        return len(self._descr)

    def size(self):
        return len(self)

class qTStatus(object):
    def __init__(self, data=None, offset=0):
        self.data = data[offset:]
        self.running = self.data[0]==b'1'
        opt = {}
        for o in self.data[2:].split(b";"):
            try:
                x = o.index(b":")
                v = o[x+1:]
                n = o[:x]
                if len(v)>0:
                    v = int(v,16)
                opt[n] = v
            except ValueError:
                continue
        self.options = opt

    def option(self,opt):
        return self.options.get(opt,None)

    def traceframe_count(self):
        return self.option(b"tframes") or -1
    def traceframes_created(self):
        return self.option(b"tcreated") or 1
    def buffer_free(self):
        return self.option(b"tfree") or -1
    def buffer_size(self):
        return self.option(b"tsize") or -1
    def disconnected_tracing(self):
        return self.option(b"disconn")
    def circular_buffer(self):
        return self.option(b"circular")
    def start_time(self):
        return self.option(b"starttime")/1.e6
    def stop_time(self):
        return self.option(b"stoptime")/1.e6
    def user_name(self):
        return self.option(b"username")


class TraceStateVariable(object):
    def __init__(self,l=None,offset=0):
        if l is not None:
            O = l[offset:].split(b':')
            self.number = int(O[0],16)
            self.initial_value = O[1]
            self.builtin = int(O[2],16)
            self.name = O[3]


class TracePoint(object):
    def __init__(self,l):
        if l.startswith(b'T'):
            O = l[1:].split(b':')
            self.number  = int(O[0],16)
            self.address = O[1]
            self.enabled = O[2]==b'E'
            self.step    = int(O[3],16)
            self.nbpass  = int(O[4],16)
            self.fast    = None
            self.cond    = None
            for o in O[5:]:
                if o.startswith(b'F'):
                    self.fast = int(o[1:],16)
                elif o.startswith(b'X'):
                    self.cond = o[1:].split(b',')
            self.act = []
            self.step_act = []
            self.src = []
            self.step_src = []
            self.hit_count = None
            self.traceframe_usage = None

    def getO(self,l):
        O = l[1:].split(b':')
        n = int(O[0],16)
        if n!=self.number:
            logger.error("unknown tracepoint number ?")
            raise ValueError(n)
        a = O[1]
        if a!=self.address:
            logger.error("unknown tracepoint address ?")
            raise ValueError(a)
        return O

    def define(self,l):
        O = self.getO(l)
        if l.startswith(b'A'):
            self.act.append(O[2])
        elif l.startswith(b'S'):
            self.step_act.append(O[2])
        elif l.startswith(b'Z'):
            s = self.decode_source(O[2:])
            if len(self.step_act)>0:
                self.step_src.append(s)
            else:
                self.src.append(s)
        elif l.startswith(b'V'):
            self.hit_count = int(O[2],16)
            self.traceframe_usage = O[3]

    def decode_source(self,O):
        src_type = O[0]
        src_len = int(O[2],16)
        to_src = lambda x: bytes.fromhex(x.decode('utf-8'))
        src_def = to_src(O[3])
        assert src_len == len(src_def)
        return (src_type,src_def)

    def __str__(self):
        s  = "tracepoint %d at address '%s'"%(self.number,self.address)
        if len(self.step_src)>0:
            s += ":"
        s += "\n"
        for l in self.step_src:
            if l[0]==b'cmd':
                s += "  %s\n"%l[1]
        return s


@StructDefine(
"""
H       : number
c*~I    : raw
""", packed = True
)
class GDBTraceFrame(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.frame_type = None
        if data:
            self.unpack(data,offset)
            if len(self.raw)>0:
                self.frame_type = self.raw[0:1]


# ------------------------------------------------------------------------------

