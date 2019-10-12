# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2007-2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/core.py
==============

This module defines all task/process core classes related to binary format and
execution inherited by all system specific execution classes of
the :mod:`amoco.system` package.

"""

from io import BytesIO

from amoco.system.memory import *

from amoco.logger import Log
logger = Log(__name__)
logger.debug('loading module')

#------------------------------------------------------------------------------

class CoreExec(object):
    """The Task class implements the base class for a memory mapped binary
    executable program, providing the generic instruction or data fetchers and
    the mandatory API used by :mod:`amoco.san` analysis classes.
    Most of the :mod:`amoco.system` modules use this base class and redefine
    the :meth:`initenv`, :meth`load_binary` and helpers methods according to
    a dedicated system and architecture (Linux/x86, Win32/x86, etc).

    Attributes:
        bin: the program executable format object. Currently supported formats
             are provided in :mod:`system.elf` (Elf32/64), :mod:`system.pe` (PE)
             and :mod:`system.utils` (HEX/SREC). 

        cpu: the architecture cpu module, which implements the disassembler and
             provides all registers.

        state: the :class:`mapper` instance that represents the current state
             of the executable program, including mapping of registers as well
             as the :class:`MemoryMap` instance that represents the virtual
             memory of the program.


    """
    __slots__ = ['bin','cpu','OS','state']

    def __init__(self,p,cpu=None):
        self.bin = p
        self.cpu = cpu
        self.OS = None
        self.state = self.initstate()

    def initstate(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        return m

    def read_data(self,vaddr,size):
        'fetch size data bytes at virtual address vaddr'
        return self.state.mmap.read(vaddr,size)

    def read_instruction(self,vaddr,**kargs):
        'fetch instruction at virtual address vaddr'
        if self.cpu is None:
            logger.error('no cpu imported')
            raise ValueError
        maxlen = self.cpu.disassemble.maxlen
        try:
            istr = self.state.mmap.read(vaddr,maxlen)
        except MemoryError as e:
            logger.verbose("vaddr %s is not mapped"%vaddr)
            raise MemoryError(e)
        else:
            if len(istr)<=0 or not isinstance(istr[0],bytes):
                logger.verbose("failed to read instruction at %s"%vaddr)
                return None
        i = self.cpu.disassemble(istr[0],**kargs)
        if i is None:
            logger.warning("disassemble failed at vaddr %s"%vaddr)
            return None
        else:
            if i.address is None: i.address = vaddr
            xsz = i.misc['xsz'] or 0
            if xsz>0:
                xdata = self.state.mmap.read(vaddr+i.length,xsz)
                i.xdata(i,xdata)
            return i

    def getx(self,loc,size=8,sign=False):
        if isinstance(loc,str):
            x = getattr(self.cpu,loc)
        elif isinstance(loc,int):
            endian = self.cpu.get_data_endian()
            psz = self.cpu.PC().size
            addr = self.cpu.cst(loc,psz)
            x = self.cpu.mem(addr,size,endian=endian)
        else:
            raise ValueError('provided location should be a register name (str) or memory address (int)')
        r = self.state(x)
        r.sf = sign
        return r.value() if r._is_cst else r

    def setx(self,loc,val,size=8):
        if isinstance(loc,str):
            x = getattr(self.cpu,loc)
            size = x.size
        elif isinstance(loc,int):
            endian = self.cpu.get_data_endian()
            psz = self.cpu.PC().size
            x = self.cpu.mem(self.cpu.cst(addr,psz),size,endian=endian)
        else:
            x = loc
        if isinstance(val,bytes):
            if x._is_reg: raise ValueError('register location should be set to an integer value')
            x.size = len(val)
            self.state._Mem_write(x.a,val)
        elif isinstance(val,IntType):
            self.state[x] = self.cpu.cst(val,size)
        else:
            self.state[x] = val

    def get_uint64(self,loc):
        return self.getx(loc,size=64,sign=True)
    def get_int64(self,loc):
        return self.getx(loc,size=64)
    def get_uint32(self,loc):
        return self.getx(loc,size=32,sign=True)
    def get_int32(self,loc):
        return self.getx(loc,size=32)
    def get_uint16(self,loc):
        return self.getx(loc,size=16,sign=True)
    def get_int16(self,loc):
        return self.getx(loc,size=16)
    def get_uint8(self,loc):
        return self.getx(loc,sign=True)
    def get_int8(self,loc):
        return self.getx(loc)

#------------------------------------------------------------------------------

# decorator to define a stub:
class DefineStub(object):
    def __init__(self,obj,refname,default=False):
        self.obj = obj
        self.ref = refname
        self.default = default
    def __call__(self,f):
        if self.default:
            self.obj.stub_default = f
        else:
            self.obj.stubs[self.ref] = f
        return f

#------------------------------------------------------------------------------

class BinFormat(object):
    is_ELF    = False
    is_PE     = False
    basemap   = None
    symtab    = None
    strtab    = None
    reltab    = None
    functions = None
    variables = None

    @property
    def entrypoints(self):
        raise NotImplementedError

    @property
    def filename(self):
        raise NotImplementedError

    def loadsegment(self,S,pagesize=None,raw=None):
        raise NotImplementedError


class DataIO(BinFormat):
    """This class wraps a binary file or a string of bytes and provides both
    the file and bytes API.
    """

    def __init__(self, f):
        if isinstance(f,bytes):
            self.f=BytesIO(f)
        else:
            self.f=f

    def __getitem__(self,i):
        stay = self.f.tell()
        sta = i.start or stay
        self.f.seek(sta,0)
        if i.stop is None:
            data = self.f.read()
        else:
            data = self.f.read(i.stop-sta)
        self.f.seek(stay,0)
        return data

    def read(self,size=-1):
        return self.f.read(size)

    def readline(self,size=-1):
        return self.f.readline(size)

    def readlines(self,size=-1):
        return self.f.readlines(size)

    def xreadlines(self,size=-1):
        return self.f.xreadlines(size)

    def write(self,s):
        return self.f.write(s)

    def writelines(self,l):
        return self.f.writelines(l)

    def seek(self,offset,whence=0):
        return self.f.seek(offset,whence)

    def tell(self):
        return self.f.tell()

    def flush(self):
        return self.f.flush()

    def fileno(self):
        return self.f.fileno()

    def isatty(self):
        return self.f.isatty()

    def next(self):
        return self.f.next()

    def truncate(self,size=0):
        return self.f.truncate(size)

    def close(self):
        return self.f.close()

    @property
    def closed(self):
        return self.f.closed

    @property
    def encoding(self):
        return self.f.encoding

    @property
    def errors(self):
        return self.f.errors

    @property
    def mode(self):
        return self.f.mode

    @property
    def name(self):
        try:
            return self.f.name
        except AttributeError:
            try:
                from builtins import bytes
            except ImportError:
                pass
            s = bytes(self.f.getvalue())
            return '(sc-%s...)'%(''.join(["%02x"%x for x in s])[:8])

    filename = name

    @property
    def newlines(self):
        return self.f.newlines

    @property
    def softspace(self):
        return self.f.softspace

#------------------------------------------------------------------------------
def read_program(filename):
    '''
    Identifies the program header (ELF/PE) and returns an ELF, PE or DataIO
    instance.

    Args:
        filename (str): the program to read.

    Returns:
        an instance of currently supported program format (ELF, PE)

    '''

    try:
        data = open(filename,'rb')
    except (TypeError,IOError):
        data = bytes(filename)

    f = DataIO(data)

    try:
        from amoco.system import elf
        # open file as a ELF object:
        p = elf.Elf(f)
        logger.info("ELF format detected")
        return p
    except elf.ElfError:
        f.seek(0)
        logger.debug('ElfError raised for %s'%f.name)

    try:
        from amoco.system import pe
        # open file as a PE object:
        p = pe.PE(f)
        logger.info("PE format detected")
        return p
    except pe.PEError:
        f.seek(0)
        logger.debug('PEError raised for %s'%f.name)

    try:
        from amoco.system import utils
        # open file as a HEX object:
        p = utils.HEX(f)
        logger.info("HEX format detected")
        return p
    except utils.FormatError:
        f.seek(0)
        logger.debug(' HEX FormatError raised for %s'%f.name)

    try:
        # open file as a SREC object:
        p = utils.SREC(f)
        logger.info("SREC format detected")
        return p
    except utils.FormatError:
        f.seek(0)
        logger.debug(' SREC FormatError raised for %s'%f.name)

    logger.warning('unknown format')
    return f

#------------------------------------------------------------------------------
# decorator that allows to "register" all loaders on-the-fly:

class DefineLoader(object):
    LOADERS = {
    }
    def __init__(self,name):
        self.name = name
        if not self.name in self.LOADERS:
            self.LOADERS[self.name] = None
    def __call__(self,loader):
        logger.verbose('DefineLoader %s:%s'%(self.name,loader))
        self.LOADERS[self.name] = loader
        return loader

