# This code is part of Amoco
# Copyright (C) 2007-2013 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license


from amoco.logger import Log
logger = Log(__name__)

from bisect import bisect_left

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
        if len(s)>32: s=s[:32]+'...'
        return '<datadiv:%s>'%s

    def __str__(self):
        return repr(self.val) if self._is_raw else str(self.val)

    def cut(self,l):
        if self._is_raw:
            self.val = self.val[l:]
        else:
            self.val = self.val[8*l:]

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
        o,l = 8*o,8*l
        n,r = divmod(o+l,s)
        if n>0: return (self.val[o:s],r/8)
        return (self.val[o:o+l],0)

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
        if len(data)>32: data=data[:32]+'...'
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
            logger.warning('%s read out of bound (vaddr=%08x, l=%d)',repr(self),vaddr,l)
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
            logger.verbose('%s write out of bound (vaddr=%08x,data=%.32s)',repr(self),vaddr,repr(data))
            return [mo(vaddr,data)]

#------------------------------------------------------------------------------
class MemoryZone(object):
    __slot__ = ['rel','_map']

    def __init__(self,rel=None,D=None):
        self.rel = rel
        self._map = []
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

    # locate the index that contains the given address in the mmap:
    def locate(self,vaddr):
        p = [z.vaddr for z in self._map]
        if vaddr in p: return p.index(vaddr)
        i = bisect_left(p,vaddr)
        if i==0: return None
        else: return i-1

    # read l bytes starting at vaddr.
    # A MemoryError is raised if some bytes are not mapped.
    def read(self,vaddr,l):
        i = self.locate(vaddr)
        if i is None: raise MemoryError(l)
        ll = l
        res = []
        while ll>0:
            try:
                data,ll = self._map[i].read(vaddr,ll)
            except IndexError:
                data=None
            if data is None:
                raise MemoryError(ll)
            vaddr += len(data)
            res.append(data)
            i += 1
        assert ll==0
        return res

    # write data at address vaddr in map
    def write(self,vaddr,data,res=False):
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
            return
        if j==i:
            Z = self._map[i].write(z.vaddr,z.data.val)
            i += 1
            for newz in Z:
                self._map.insert(i,newz)
                i+=1
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

    def reference(self,address):
        if isinstance(address,(int,long)):
            return (None,address)
        elif isinstance(address,str):
            return (address,0)
        try:
            r,a = (address.base,address.disp)
            return (r,a)
        except AttributeError:
            if address._is_cst:
                return (None,address.v)
        raise MemoryError(address)

    def __len__(self):
        return self._zones[None].range()[1]

    def __str__(self):
        return '\n'.join(map(str,self._zones.values()))

    # getitem allows to use a MemoryMap object as if it was a string on which
    # some slice lookups are performed. This is typically the case of the API
    # required by arch/disasm "disassemble" and "getsequence" methods.
    def __getitem__(self,aslc):
        address,end = aslc.start,aslc.stop
        l = end-address
        r,o = self.reference(address)
        item = self._zones[r].read(o,l)[0]
        return item

    def read(self,address,l):
        r,o = self.reference(address)
        return self._zones[r].read(o,l)

    def write(self,address,expr):
        r,o = self.reference(address)
        self._zones[r].write(o,expr)

#------------------------------------------------------------------------------
class CoreExec(object):
    __slots__ = ['bin','cpu','mmap']

    def __init__(self,p,cpu=None):
        self.bin = p
        self.cpu = cpu
        self.mmap = MemoryMap()
        self.load_binary()
        cpu.ext.stubs = stubs

    def initenv(self):
        pass

    def load_binary(self):
        pass

    def read_data(self,vaddr,size):
        return self.mmap.read(vaddr,size)

    def read_instruction(self,vaddr,**kargs):
        maxlen = self.cpu.disassemble.maxlen
        try:
            istr = self.mmap.read(vaddr,maxlen)
        except MemoryError,e:
            ll = e.message
            l = maxlen-ll
            if l == 0:
                return None
            logger.warning("instruction fetch error: reducing fetch size (%d)"%l)
            istr = self.mmap.read(vaddr,l)
        if len(istr)>1:
            logger.warning("read_instruction: can't fetch vaddr %s"%vaddr)
            raise MemoryError
        i = self.cpu.disassemble(istr[0],**kargs)
        if i is None:
            logger.warning("disassemble failed at vaddr %s"%vaddr)
            return None
        else:
            i.address = vaddr
            return i

    # mandatory method PC (needs to be overloaded by each arch-dependent child class)
    def PC(self):
        logger.error("CoreExec PC not defined")
        raise ValueError

    # optional codehelper method allows platform-specific analysis of
    # either a (raw) list of instruction, a block/func object (see amoco.code)
    # the default helper is a no-op:
    def codehelper(self,seq=None,block=None,func=None):
        if seq is not None: return seq
        if block is not None: return block
        if func is not None: return func


#------------------------------------------------------------------------------
from collections import defaultdict

def default_hook(m):
    pass

stubs = defaultdict(lambda :default_hook)

# decorators for ext() stub definition:

def stub(f):
    stubs[f.__name__] = f
    return f

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

    def read(self,size=0):
        return self.f.read(size)

    def readline(self,size=0):
        return self.f.readline(size)

    def readlines(self,size=0):
        return self.f.readlines(size)

    def xreadlines(self,size=0):
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
        return self.f.name

    @property
    def newlines(self):
        return self.f.newlines

    @property
    def softspace(self):
        return self.f.softspace
