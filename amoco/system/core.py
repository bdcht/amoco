# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2007-2013 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license


from amoco.logger import Log
logger = Log(__name__)

from bisect import bisect_left

from amoco.cas.expressions import exp,top

#------------------------------------------------------------------------------
# datadiv provides the API for manipulating data values extracted from memory.
# These values are either considered as 'raw' (byte strings) or can be any
# abstractions (or symbolic expressions)
# The datadiv.val required API is:
#   .__len__ => byte length
#   .size => bit length
#   .__getitem__ => extraction of bit slices.
#   .__setitem__ => overwrite given bit slice.
class datadiv(object):
    __slot__ = ['val']

    def __init__(self,data):
        self.val = data

    @property
    def _is_raw(self):
        #return isinstance(self.val,str)
        return not hasattr(self.val,'_is_def')

    def __len__(self):
        return len(self.val)

    def __repr__(self):
        s = repr(self.val)
        if len(s)>32:
            s=s[:32]+"..."
            if isinstance(self.val,str): s+="'"
        return '<datadiv:%s>'%s

    def __str__(self):
        return repr(self.val) if self._is_raw else str(self.val)

    def cut(self,l):
        if self._is_raw:
            self.val = self.val[l:]
        else:
            self.val = self.val.bytes(l)

    # returns (result, counter) where result is a part of val of length l
    # located at offset o, and counter is the number of bytes that still
    # need to be read from another div.
    def getpart(self,o,l):
        try:
            assert o>=0 and l>=0
            if not self._is_raw:
                s = self.val.size
                assert s%8==0
        except AssertionError:
            logger.error("invalid fetch (o=%s,l=%s) in %s"%(o,l,repr(self)))
            raise ValueError
        lv = len(self)
        if o==0 and l==lv: return (self.val,0)
        if self._is_raw:
            res = self.val[o:o+l]
            return (res,l-len(res))
        if o>=lv: return (None,l)
        res = self.val.bytes(o,o+l)
        return (res,l-res.length)

    # returns a list of (contiguous) datadiv objects resulting from
    # overwriting self with data at offset o, possibly extending self.
    def setpart(self,o,data):
        assert 0<=o<=len(self)
        P = [datadiv(data)]
        olv = o+len(data)
        endl = len(self)-olv
        if endl>0:
            P.append(datadiv(self.getpart(olv,endl)[0]))
        if o>0:
            P.insert(0,datadiv(self.getpart(0,o)[0]))
        # now merge contiguous parts if they have same type:
        return mergeparts(P)

def mergeparts(P):
    parts = [P.pop(0)]
    while len(P)>0:
        p = P.pop(0)
        if parts[-1]._is_raw and p._is_raw:
            try:
                parts[-1].val += p.val
            except TypeError:
                parts.append(p)
        else:
            parts.append(p)
    return parts

#------------------------------------------------------------------------------
# mo are abstractions for 'memory objects'. Such obj is located at a virtual
# address in Memory. Data contained in the obj is stored as datadiv object.
class mo(object):
    __slot__ = ['vaddr','data']

    def __init__(self,vaddr,data):
        self.vaddr=vaddr
        self.data=datadiv(data)

    @property
    def end(self):
        return self.vaddr+len(self.data)

    def __contains__(self,vaddr):
        return self.vaddr<=vaddr<self.end

    def __repr__(self):
        data = str(self.data)
        if len(data)>32:
            data=data[:32]+"..."
            if self.data._is_raw: data+="'"
        return '<mo [%08x,%08x] data:%s>'%(self.vaddr,self.end,data)

    # change current obj to start at provided vaddr
    def trim(self,vaddr):
        if vaddr in self:
            l = vaddr-self.vaddr
            if l>0: self.data.cut(l)
            self.vaddr = vaddr

    # provide list of datadivs resulting from reading l bytes starting at vaddr
    def read(self,vaddr,l):
        if vaddr in self:
            return self.data.getpart(vaddr-self.vaddr,l)
        else:
            return (None,l)

    # update current obj resulting from writing datadiv at vaddr, returning the
    # list of possibly additional objs to insert in the map
    def write(self,vaddr,data):
        if vaddr in self or vaddr==self.end:
            parts = self.data.setpart(vaddr-self.vaddr,data)
            self.data = parts[0]
            O = []
            vaddr = self.end
            for p in parts[1:]:
                O.append(mo(vaddr,p.val))
                vaddr += len(p)
            return O
        else:
            return [mo(vaddr,data)]

#------------------------------------------------------------------------------
class MemoryZone(object):
    __slot__ = ['rel','_map','__cache','__dead']

    def __init__(self,rel=None,D=None):
        self.rel = rel
        self.__dead = False
        self._map = []
        self.__cache = [] # speedup locate method
        if D != None and isinstance(D,dict):
            for vaddr,data in D.iteritems():
                self.addtomap(mo(vaddr,data))

    def range(self):
        return (self._map[0].vaddr,self._map[-1].end)

    def __str__(self):
        l=['<MemoryZone rel=%s :'%str(self.rel)]
        #form = "%08x: " if not self.rel else "%+08d: "
        for z in self._map:
            l.append("\t %s"%str(z))
        return '\n'.join(l)+'>'

    def __update_cache(self):
        self.__cache = [z.vaddr for z in self._map]

    # locate the index that contains the given address in the mmap:
    def locate(self,vaddr):
        p = self.__cache
        if vaddr in p: return p.index(vaddr)
        i = bisect_left(p,vaddr)
        if i==0: return None
        else: return i-1

    # read l bytes starting at vaddr.
    # return value is a list of datadiv values, unmapped areas
    # are returned as 'void' expressions : top if zone is marked as 'dead'
    # or bottom otherwise.
    def read(self,vaddr,l):
        void = top if self.__dead else exp
        res = []
        i = self.locate(vaddr)
        if i is None:
            if len(self._map)==0: return [void(l*8L)]
            v0 = self._map[0].vaddr
            if (vaddr+l)<=v0: return [void(l*8L)]
            res.append(void((v0-vaddr)*8L))
            l = (vaddr+l)-v0
            vaddr = v0
            i = 0
        ll = l
        while ll>0:
            try:
                data,ll = self._map[i].read(vaddr,ll)
            except IndexError:
                res.append(void(ll*8L))
                ll=0L
                break
            if data is None:
                vi = self.__cache[i]
                if vaddr < vi:
                    l = min(vaddr+ll,vi)-vaddr
                    data = void(l*8L)
                    ll -= l
                    i -=1
            if data is not None:
                vaddr += len(data)
                res.append(data)
            i += 1
        assert ll==0
        return res

    # write data at address vaddr in map
    def write(self,vaddr,data,res=False,dead=False):
        if dead:
            self._map = []
            self._cache = []
            self.__dead = dead
        self.addtomap(mo(vaddr,data))
        if res is True: self.restruct()

    # add (possibly overlapping) object z to the map
    def addtomap(self,z):
        i = self.locate(z.vaddr)
        j = self.locate(z.end)
        assert j>=i
        if j is None:
            assert i is None
            self._map.insert(0,z)
            self.__update_cache()
            return
        if j==i:
            Z = self._map[i].write(z.vaddr,z.data.val)
            i += 1
            for newz in Z:
                self._map.insert(i,newz)
                i+=1
            self.__update_cache()
            return
        # i!=j cases:
        # delete & update every overwritten zones
        # by adjusting [i,j]:
        if z.end in self._map[j]:
            self._map[j].trim(z.end)
        else:
            j += 1
        Z = [z]
        if i is None:
            i=-1
        elif z.vaddr <= self._map[i].end:
            # overright data:
            Z = self._map[i].write(z.vaddr,z.data.val)
        i += 1
        del self._map[i:j]
        # insert new zones:
        for newz in Z:
            self._map.insert(i,newz)
            i+=1
        self.__update_cache()

    def restruct(self):
        if len(self._map)==0: return
        m = [self._map.pop(0)]
        for z in self._map:
            rawtype = (z.data._is_raw & m[-1].data._is_raw)
            if rawtype and (z.vaddr==m[-1].end):
                try:
                    m[-1].data.val += z.data.val
                except TypeError:
                    m.append(z)
            else:
                m.append(z)
        self._map = m
        self.__update_cache()

    def shift(self,offset):
        for z in self._map:
            z.vaddr += offset
        self.__update_cache()

    def grep(self,pattern):
        import re
        g = re.compile(pattern)
        res = []
        for z in self._map:
            if z.data._is_raw:
                off=0
                for s in g.findall(z.data.val):
                    off = z.data.val.index(s,off)
                    res.append(z.vaddr+off)
                    off += len(s)
        return res

#------------------------------------------------------------------------------
class MemoryMap(object):
    __slot__ = ['_zones','perms']

    def __init__(self,D=None):
        self._zones = {None:MemoryZone()}
        self.perms  = {}

    def newzone(self,label):
        z = MemoryZone()
        z.rel = label
        self._zones[label] = z
        return z

    def locate(self,address):
        r, a = self.reference(address)
        idx = self._zones[r].locate(a)
        return self._zones[r]._map[idx]

    def reference(self,address):
        if isinstance(address,(int,long)):
            return (None,address)
        elif isinstance(address,str):
            return (address,0)
        try:
            r,a = (address.base,address.disp)
            if r._is_cst:
                return (None,(r+a).v)
            return (r,a)
        except AttributeError:
            if address._is_cst:
                return (None,address.v)
        raise MemoryError(address)

    def __len__(self):
        return self._zones[None].range()[1]

    def __str__(self):
        return '\n'.join(map(str,self._zones.values()))

    def read(self,address,l):
        r,o = self.reference(address)
        if r in self._zones:
            return self._zones[r].read(o,l)
        else:
            raise MemoryError(address)

    def write(self,address,expr,deadzone=False):
        r,o = self.reference(address)
        if not r in self._zones:
            self.newzone(r)
        self._zones[r].write(o,expr,deadzone)

    def restruct(self):
        for z in self._zones.itervalues(): z.restruct()

    def grep(self,pattern):
        res = []
        for z in self._zones.values():
            zres = z.grep(pattern)
            if z.rel is not None: zres = [z.rel+r for r in zres]
            res.extend(zres)
        return res

#------------------------------------------------------------------------------
class CoreExec(object):
    __slots__ = ['bin','cpu','mmap']

    def __init__(self,p,cpu=None):
        self.bin = p
        self.cpu = cpu
        self.mmap = MemoryMap()
        self.load_binary()
        if cpu is not None:
            cpu.ext.stubs = stubs

    def initenv(self):
        return None

    def load_binary(self):
        pass

    def read_data(self,vaddr,size):
        return self.mmap.read(vaddr,size)

    def read_instruction(self,vaddr,**kargs):
        if self.cpu is None:
            logger.error('no cpu imported')
            raise ValueError
        maxlen = self.cpu.disassemble.maxlen
        try:
            istr = self.mmap.read(vaddr,maxlen)
        except MemoryError,e:
            logger.verbose("vaddr %s is not mapped"%vaddr)
            raise MemoryError(e)
        else:
            if len(istr)<=0 or not isinstance(istr[0],str):
                logger.verbose("failed to read instruction at %s"%vaddr)
                return None
        i = self.cpu.disassemble(istr[0],**kargs)
        if i is None:
            logger.warning("disassemble failed at vaddr %s"%vaddr)
            return None
        else:
            i.address = vaddr
            return i

    # optional codehelper method allows platform-specific analysis of
    # either a (raw) list of instruction, a block/func object (see amoco.code)
    # the default helper is a no-op:
    def codehelper(self,seq=None,block=None,func=None):
        if seq is not None: return seq
        if block is not None: return block
        if func is not None: return func


#------------------------------------------------------------------------------
from collections import defaultdict

# default stub:
def default_hook(m,**kargs):
    pass

stubs = defaultdict(lambda :default_hook)

# decorators for ext() stub definition:

# decorator to define a stub:
def stub(f):
    stubs[f.__name__] = f
    return f

# decorator to (re)define the default stub:
def stub_default(f):
    stubs.default_factory = lambda :f
    return f

#------------------------------------------------------------------------------
from cStringIO import StringIO

class DataIO(object):

    def __init__(self, f):
        if isinstance(f,file):
            self.f=f
        elif isinstance(f,str):
            self.f=StringIO(f)
        else:
            raise TypeError

    def __getitem__(self,i):
        self.f.seek(i.start,0)
        return self.f.read(i.stop-i.start)

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
            return self.f.getvalue()

    filename = name

    @property
    def newlines(self):
        return self.f.newlines

    @property
    def softspace(self):
        return self.f.softspace
