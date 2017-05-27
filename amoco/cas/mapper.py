# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.logger import Log
logger = Log(__name__)

from .expressions import *
from amoco.cas.tracker import generation
from amoco.system.core import MemoryMap
from amoco.arch.core   import Bits
from amoco.ui.render   import vltable

# a mapper is a symbolic functional representation of the execution
# of a set of instructions.
# __map  : is an ordered list of mappings of expressions associated with a
# location (a register or a memory pointer). The order is relevant only
# to reflect the order of write-to-memory instructions.
# __Mem  : is a memory model where symbolic memory pointers are using
# individual separated zones.
# conds  : is the list of conditions that must be True for the mapper
# csi    : is the optional interface to a "concrete" state
class mapper(object):
    assume_no_aliasing = False

    __slots__ = ['__map','__Mem','conds', 'csi']

    # a mapper is inited with a list of instructions
    # provided by a disassembler
    def __init__(self,instrlist=None,csi=None):
        self.__map = generation()
        self.__map.lastw = 0
        self.__Mem = MemoryMap()
        self.conds = []
        self.csi = csi
        icache = []
        # if the __map needs to be inited before executing instructions
        # one solution is to prepend the instrlist with a function dedicated
        # to this init phase...
        for instr in instrlist or []:
            # call the instruction with this mapper:
            if not instr.misc['delayed']: instr(self)
            else: icache.append(instr)
        for instr in icache:
            instr(self)

    def __len__(self):
        return len(self.__map)

    def __str__(self):
        return u'\n'.join([u"%s <- %s"%x for x in self])

    def pp(self,**kargs):
        t = vltable()
        t.rowparams['sep'] = ' <- '
        for (l,v) in self:
            if l._is_reg: v = v[0:v.size]
            lv = (l.toks(**kargs)+
                  [(render.Token.Column,u'')]+
                  v.toks(**kargs))
            t.addrow(lv)
        if t.colsize[0]>18: t.colsize[0]=18
        if t.colsize[1]>58: t.colsize[1]=58
        return t.__str__()

    # list antecedent locations (used in the mapping)
    def inputs(self):
        r = []
        for l,v in iter(self.__map.items()):
            for lv in locations_of(v):
                if lv._is_reg and l._is_reg:
                    if (lv == l) or (lv.type==l.type==regtype.FLAGS):
                        continue
                r.append(lv)
        return r

    # list image locations (modified in the mapping)
    def outputs(self):
        L = []
        for l in sum([locations_of(e) for e in self.__map],[]):
            if l._is_reg and l.type in (regtype.PC,regtype.FLAGS): continue
            if l._is_ptr: l = mem(l,self.__map[l].size)
            if self.__map[l]==l: continue
            L.append(l)
        return L

    def has(self,loc):
        for l in self.__map.keys():
            if loc==l: return True
        return False

    def history(self,loc):
        return self.__map._generation__getall(loc)

    def rw(self):
        r = filter(lambda x:x._is_mem, self.inputs())
        w = filter(lambda x:x._is_mem, self.outputs())
        sr = [x.size for x in r]
        sw = [x.size for x in w]
        return (sr,sw)

    def clear(self):
        self.__map.clear()
        self.__Mem = MemoryMap()
        self.conds = []

    def memory(self):
        return self.__Mem
    def setmemory(self,mmap):
        self.__Mem = mmap

    def generation(self):
        return self.__map

    # compare self with mapper m:
    def __cmp__(self,m):
        d = cmp(self.__map.lastdict(),m.__map.lastdict())
        return d

    def __eq__(self,m):
        d = (self.__map.lastdict()==m.__map.lastdict())
        return d

    # iterate over ordered correspondances:
    def __iter__(self):
        for (loc,v) in iter(self.__map.items()):
            yield (loc,v)

    # get a (plain) register value:
    def R(self,x):
        if self.csi:
            return self.__map.get(x,self.csi(x))
        else:
            return self.__map.get(x,x)

    # get a memory location value (fetch) :
    # k must be mem expressions
    def M(self,k):
        if k.a.base._is_lab: return k
        if k.a.base._is_ext: return k.a.base
        n = self.aliasing(k)
        if n>0:
            f = lambda e:e[0]._is_ptr
            items = filter(f,list(self.__map.items())[0:n])
            res = mem(k.a,k.size,mods=list(items),endian=k.endian)
        else:
            res = self._Mem_read(k.a,k.length,k.endian)
            res.sf = k.sf
        return res

    def aliasing(self,k):
        if self.assume_no_aliasing: return 0
        K = list(self.__map.keys())
        n = self.__map.lastw
        try:
            i = K.index(k.a)
        except ValueError:
            # k has never been written to explicitly
            # but it is maybe in a zone that was written to
            i = -1
        for l in K[i+1:n]:
            if not l._is_ptr: continue
            if l.base==k.a.base: continue
            return n
        return 0

    # read MemoryMap and return the result as an expression:
    def _Mem_read(self,a,l,endian=1):
        try:
            res = self.__Mem.read(a,l)
        except MemoryError: # no zone for location a;
            res = [exp(l*8)]
        if endian==-1: res.reverse()
        P = []
        cur = 0
        for p in res:
            plen = len(p)
            if isinstance(p,exp) and (p._is_def is False):
                if self.csi:
                    p = self.csi(mem(a,p.size,disp=cur,endian=endian))
                else:
                    p = mem(a,p.size,disp=cur)
            if isinstance(p,bytes):
                p = cst(Bits(p[::endian],bitorder=1).int(),plen*8)
            P.append(p)
            cur += plen
        return composer(P)

    def _Mem_write(self,a,v,endian=1):
        if a.base._is_vec:
            locs = (ptr(l,a.seg,a.disp) for l in a.base.l)
        else:
            locs = (a,)
        iswide = not a.base._is_def
        for l in locs:
            self.__Mem.write(l,v,endian,deadzone=iswide)
            if (l in self.__map): del self.__map[l]

    # just a convenient wrapper around M/R:
    def __getitem__(self,k):
        r = self.M(k) if k._is_mem else self.R(k)
        if k.size!=r.size: raise ValueError('size mismatch')
        return r[0:k.size]

    # define image v of antecedent k:
    def __setitem__(self,k,v):
        if k._is_ptr:
            loc = k
        else:
            if k.size!=v.size:
                raise ValueError('size mismatch')
            try:
                loc = k.addr(self)
            except TypeError:
                logger.error('setitem ignored (invalid left-value expression)')
                return
        if k._is_slc and not loc._is_reg:
            raise ValueError('memory location slc is not supported')
        elif loc._is_ptr:
            r = v
            oldr = self.__map.get(loc,None)
            if oldr is not None and oldr.size>r.size:
                r = composer([r,oldr[r.size:oldr.size]])
            if k._is_mem:
                endian = k.endian
            else:
                endian = 1
            self._Mem_write(loc,r,endian)
            self.__map.lastw = len(self.__map)+1
        else:
            r = self.R(loc)
            if r._is_reg:
                r = comp(loc.size)
                r[0:loc.size] = loc
            pos = k.pos if k._is_slc else 0
            r[pos:pos+k.size] = v.simplify()
        self.__map[loc] = r

    def update(self,instr):
        instr(self)

    # eval of x in this map:
    # note the difference between a mapper[mem(p)] and mapper(mem(p)):
    # in the call form, p is first evaluated so that the target address
    # is the expression of p "after execution" whereas the indexing form
    # uses p as an input (i.e "before execution") expression.
    # example, suppose str(mapper) is:
    #   (esp)   <- eax
    #       esp <- { | [0:32]->(esp-0x4) | }
    #   (esp-4) <- ebx
    # then:
    # mapper[mem(esp)] returns eax (what is pointed by "esp before execution")
    # mapper(mem(esp)) returns ebx (what is pointed by "esp after execution")
    def __call__(self,x):
        if len(self)==0: return x
        return x.eval(self)

    def restruct(self):
        self.__Mem.restruct()

    # return a new mapper instance where all input locations have
    # been replaced by there corresponding values in m.
    # example:
    # in self: eax <- ebx
    # in m   : ebx <- 4
    #          edx <- (ecx+1)
    # =>
    # result : eax <- 4
    def eval(self,m):
        mm = mapper(csi=self.csi)
        for c in self.conds:
            cc = c.eval(m)
            if not cc._is_def: continue
            if cc==1: continue
            if cc==0:
                logger.verbose("invalid mapper eval: cond %s is false"%c)
                raise ValueError
            mm.conds.append(cc)
        for loc,v in self:
            if loc._is_ptr:
                loc = m(loc)
            mm[loc] = m(v)
        return mm

    # composition operator returns a new mapper
    # corresponding to function x -> self(m(x))
    def rcompose(self,m):
        mcopy = m.use()
        for c in self.conds:
            cc = c.eval(m)
            if not cc._is_def: continue
            if cc==1: continue
            if cc==0:
                logger.verbose("invalid mapper eval: cond %s is false"%c)
                raise ValueError
            mcopy.conds.append(cc)
        mm = mcopy.use()
        for loc,v in self:
            if loc._is_ptr:
                loc = mcopy(loc)
            mm[loc] = mcopy(v)
        return mm

    # self << m : composition (self(m))
    def __lshift__(self,m):
        return self.rcompose(m)

    # self >> m : composition (m(self))
    def __rshift__(self,m):
        return m.rcompose(self)

    def interact(self):
        raise NotImplementedError

    # return a mapper corresponding to the evaluation of the current mapper
    # where all key symbols found in kargs are replaced by their values in
    # all expressions. The kargs "size=value" allows for adjusting symbols/values
    # sizes for all arguments.
    # if kargs is empty, a copy of the result is just a copy of current mapper.
    def use(self,*args,**kargs):
        m = mapper(csi=self.csi)
        for loc,v in args:
            m[loc] = v
        if len(kargs)>0:
            argsz = kargs.get('size',32)
            for k,v in iter(kargs.items()):
                m[reg(k,argsz)] = cst(v,argsz)
        return self.eval(m)

    def usemmap(self,mmap):
        m = mapper()
        m.setmemory(mmap)
        for xx in set(self.inputs()):
            if xx._is_mem:
                v = m.M(xx)
                m[xx] = v
        return self.eval(m)

    # attach/apply conditions to the output mapper
    def assume(self,conds):
        m = mapper(csi=self.csi)
        if conds is None: conds=[]
        for c in conds:
            if not c._is_eqn: continue
            if c.op.symbol == OP_EQ and c.r._is_cst:
                if c.l._is_reg:
                    m[c.l] = c.r
        m.conds = conds
        mm = self.eval(m)
        mm.conds += conds
        return mm

from amoco.cas.smt import *

# union of two mappers:
def merge(m1,m2,widening=None):
    m1 = m1.assume(m1.conds)
    m2 = m2.assume(m2.conds)
    mm = mapper()
    for loc,v1 in m1:
        if loc._is_ptr:
            seg = loc.seg
            disp = loc.disp
            if loc.base._is_vec:
                v2 = vec([m2[mem(l,v1.size,seg,disp)] for l in loc.base.l])
            else:
                v2 = m2[mem(loc,v1.size)]
        else:
            v2 = m2[loc]
        vv = vec([v1,v2]).simplify(widening)
        mm[loc] = vv
    for loc,v2 in m2:
        if mm.has(loc): continue
        if loc._is_ptr:
            v1 = m1[mem(loc,v2.size)]
        else:
            v1 = m1[loc]
        vv = vec([v1,v2]).simplify(widening)
        mm[loc] = vv
    return mm
