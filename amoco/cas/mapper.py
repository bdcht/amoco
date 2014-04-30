# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

from amoco.logger import Log
logger = Log(__name__)

from .expressions import reg,cst,mem,comp,top
from amoco.cas.tracker import generation

class mapper(object):

    __slots__ = ['__map']

    # a mapper is inited with a list of instructions 
    # provided by a disassembler (see x86)
    def __init__(self,instrlist=None):
        self.__map  = generation()
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

    def __str__(self):
        return '\n'.join(["%s <- %s"%x for x in self])

    # list antecedent locations (used in the mapping)
    def inputs(self):
        pass

    # list image locations (modified in the mapping)
    def outputs(self):
        pass

    def clear(self):
        self.__map.clear()

    # compare self with mapper m:
    def __cmp__(self,m):
        d = cmp(self.__map.lastdict(),m.__map.lastdict())
        return d
        #if d<>0: return d
        #shall we compare also the order ?
        #return cmp(self.__order,m.__order)

    # iterate over ordered correspondances:
    def __iter__(self):
        for (loc,v) in self.__map.iteritems():
            yield (loc,v)

    # get a (plain) register value:
    def R(self,x):
        return self.__map.get(x,x)

    # get a memory location value (fetch) :
    def M(self,k):
        if k.a.base._is_ext: return k.a.base
        x = self.__map.get(k.a,k)
        if x.size<k.size:
            logger.warning('read memory out of bound')
            c = comp(k.size)
            c[0:x.size] = x
            c[x.size:k.size] = top(k.size-x.size)
            x = c
        return x[0:k.size]

    # just a convenient wrapper around M/R:
    def __getitem__(self,k):
        r = self.M(k) if k._is_mem else self.R(k)
        if k.size!=r.size: raise ValueError('size mismatch')
        return r[0:k.size]

    # define image v of antecedent k:
    def __setitem__(self,k,v):
        if k.size<>v.size: raise ValueError('size mismatch')
        try:
            loc = k.addr(self)
        except TypeError:
            logger.verbose('setitem ignored (invalid left-value expression)')
            return
        if k._is_mem:
            r = v
        else:
            r = self.R(loc)
            if r._is_reg:
                r = comp(loc.size)
                r[0:loc.size] = loc
            pos = 0 if k._is_reg else k.pos
            r[pos:pos+k.size] = v
        self.__map[loc] = r

    def update(self,instr):
        instr(self)

    # eval of x in this map:
    # note the difference between a mapper[mem(x)] and mapper(mem(x)):
    # in the call form, x is first evaluated so that it uses "x_out"
    # whereas the item form uses "x_in".
    def __call__(self,x):
        return x.eval(self)

    def restruct(self):
        pass

    def eval(self,m):
        mm = mapper()
        for loc,v in self:
            if loc._is_ptr: loc = m(mem(loc,v.size))
            mm[loc] = m(v)
        return mm

    def interact(self):
            pass

    def use(self,**kargs):
        m = mapper()
        for k,v in kargs.iteritems():
            m[reg(k)] = cst(v)
        return self.eval(m)
