# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
cas/mapper.py
=============

The mapper module essentially implements the :class:`mapper` class
and the associated :func:`merge` function which allows to get a
symbolic representation of the *union* of two mappers.
"""

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

from .expressions import *

from amoco.cas.tracker import generation
from amoco.system.memory import MemoryMap
from amoco.arch.core import Bits
from amoco.ui.views import mapView


class mapper(object):
    """A mapper is a symbolic functional representation of the execution
    of a set of instructions.

    Args:
        instrlist (list[instruction]): a list of instructions that are
                  symbolically executed within the mapper.
        csi (Optional[object]): the optional csi attribute that provide
                  a *concrete* initial state

    Attributes:
        __map  : is an ordered list of mappings of expressions associated with a
                 location (register or memory pointer). The order is relevant
                 only to reflect the order of write-to-memory instructions in
                 case of pointer aliasing.
        __Mem  : is a memory model where symbolic memory pointers are addressing
                 separated memory zones. See MemoryMap and MemoryZone classes.
        conds  : is the list of conditions that must be True for the mapper
        csi    : is the optional interface to a *concrete* state
    """

    __slots__ = ["__map", "__Mem", "conds", "csi", "view"]

    def __init__(self, instrlist=None, csi=None):
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
            if not instr.misc["delayed"]:
                instr(self)
            else:
                icache.append(instr)
        for instr in icache:
            instr(self)
        self.view = mapView(self)

    def __len__(self):
        return len(self.__map)

    def __str__(self):
        return "\n".join(["%s <- %s" % x for x in self])

    def inputs(self):
        "list antecedent locations (used in the mapping)"
        r = []
        for l, v in iter(self.__map.items()):
            for lv in locations_of(v):
                if lv._is_reg and l._is_reg:
                    if (lv == l) or (lv.type == l.type == regtype.FLAGS):
                        continue
                r.append(lv)
        return r

    def outputs(self):
        "list image locations (modified in the mapping)"
        L = []
        for l in sum([locations_of(e) for e in self.__map], []):
            if l._is_reg and l.type in (regtype.PC, regtype.FLAGS):
                continue
            if l._is_ptr:
                l = mem(l, self.__map[l].size)
            if self[l] == l:
                continue
            L.append(l)
        return L

    def has(self, loc):
        "check if the given location expression is touched by the mapper"
        for l in self.__map.keys():
            if loc == l:
                return True
        return False

    def history(self, loc):
        return self.__map._generation__getall(loc)

    def rw(self):
        "get the read sizes and written sizes tuple"
        r = filter(lambda x: x._is_mem, self.inputs())
        w = filter(lambda x: x._is_mem, self.outputs())
        sr = [x.size for x in r]
        sw = [x.size for x in w]
        return (sr, sw)

    def clear(self):
        "clear the current mapper, reducing it to the identity transform"
        self.__map.clear()
        self.__Mem = MemoryMap()
        self.conds = []

    def getmemory(self):
        "get the local :class:`MemoryMap` associated to the mapper"
        return self.__Mem

    def setmemory(self, mmap):
        "set the local :class:`MemoryMap` associated to the mapper"
        self.__Mem = mmap

    mmap = property(getmemory, setmemory)

    def generation(self):
        return self.__map

    def __cmp__(self, m):
        d = cmp(self.__map.lastdict(), m.__map.lastdict())
        return d

    def __eq__(self, m):
        d = self.__map.lastdict() == m.__map.lastdict()
        return d

    # iterate over ordered correspondances:
    def __iter__(self):
        for (loc, v) in iter(self.__map.items()):
            yield (loc, v)

    def R(self, x):
        "get the expression of register x"
        if self.csi:
            return self.__map.get(x, self.csi(x))
        else:
            return self.__map.get(x, x)

    def M(self, k):
        """get the expression of a memory location expression k"""
        if k.a.base._is_lab:
            return k
        if k.a.base._is_ext:
            return k.a.base
        n = self.aliasing(k)
        if n > 0:
            f = lambda e: e[0]._is_ptr
            items = filter(f, list(self.__map.items())[0:n])
            res = mem(k.a, k.size, mods=list(items), endian=k.endian)
        else:
            res = self._Mem_read(k.a, k.length, k.endian)
            res.sf = k.sf
        return res

    def aliasing(self, k):
        """check if location k is possibly aliased by the mapper:
        i.e. the mapper writes to some other location expression
        after writing to k"""
        if conf.Cas.noaliasing:
            return 0
        K = list(self.__map.keys())
        n = self.__map.lastw
        try:
            i = K.index(k.a)
        except ValueError:
            # k has never been written to explicitly
            # but it is maybe in a zone that was written to
            i = -1
        for l in K[i + 1 : n]:
            if not l._is_ptr:
                continue
            if l.base == k.a.base:
                continue
            return n
        return 0

    def _Mem_read(self, a, l, endian=1):
        "read l bytes from memory address a and return an expression"
        try:
            res = self.__Mem.read(a, l)
        except MemoryError:  # no zone for location a;
            res = [exp(l * 8)]
        if endian == -1:
            res.reverse()
        P = []
        cur = 0
        for p in res:
            plen = len(p)
            if isinstance(p, exp) and (p._is_def is False):
                # p is "bottom":
                if self.csi:
                    p = self.csi(mem(a, p.size, disp=cur, endian=endian))
                else:
                    p = mem(a, p.size, disp=cur)
            if isinstance(p, bytes):
                p = cst(Bits(p[::endian], bitorder=1).int(), plen * 8)
            P.append(p)
            cur += plen
        return composer(P)

    def _Mem_write(self, a, v, endian=1):
        "write expression v at memory address a with given endianness"
        if a.base._is_vec:
            locs = (ptr(l, a.seg, a.disp) for l in a.base.l)
        else:
            locs = (a,)
        for l in locs:
            self.__Mem.write(l, v, endian)
            if l in self.__map:
                del self.__map[l]

    def __getitem__(self, k):
        "just a convenient wrapper around M/R"
        r = self.M(k) if k._is_mem else self.R(k)
        if k.size != r.size:
            raise ValueError("size mismatch")
        return r[0 : k.size]

    # define image v of antecedent k:
    def __setitem__(self, k, v):
        if k._is_ptr:
            loc = k
        else:
            if k.size != v.size:
                raise ValueError("size mismatch")
            try:
                loc = k.addr(self)
            except TypeError:
                logger.error("setitem ignored (invalid left-value expression: %s)" % k)
                return
        if k._is_slc and not loc._is_reg:
            raise ValueError("memory location slc is not supported")
        elif loc._is_ptr:
            r = v
            oldr = self.__map.get(loc, None)
            if oldr is not None and oldr.size > r.size:
                r = composer([r, oldr[r.size : oldr.size]])
            if k._is_mem:
                endian = k.endian
            else:
                endian = 1
            self._Mem_write(loc, r, endian)
            self.__map.lastw = len(self.__map) + 1
        else:
            r = self.R(loc)
            if r._is_reg:
                r = comp(loc.size)
                r[0 : loc.size] = loc
            pos = k.pos if k._is_slc else 0
            r[pos : pos + k.size] = v.simplify()
        self.__map[loc] = r

    def update(self, instr):
        "opportunistic update of the self mapper with instruction"
        instr(self)

    def safe_update(self, instr):
        "update of the self mapper with instruction *only* if no exception occurs"
        try:
            m = mapper()
            instr(m)
            _ = self >> m
        except Exception as e:
            logger.error("instruction @ %s raises exception %s" % (instr.address, e))
            raise e
        else:
            self.update(instr)

    def __call__(self, x):
        """evaluation of expression x in this map:
           note the difference between a mapper[mem(p)] and mapper(mem(p)):
           in the call form, p is first evaluated so that the target address
           is the expression of p "after execution" whereas the indexing form
           uses p as an input (i.e "before execution") expression.
        """
        if len(self) == 0:
            return x
        return x.eval(self)

    def restruct(self):
        self.__Mem.restruct()

    def eval(self, m):
        """return a new mapper instance where all input locations have
           been replaced by there corresponding values in m.
        """
        mm = mapper(csi=self.csi)
        mm.setmemory(self.mmap.copy())
        for c in self.conds:
            cc = c.eval(m)
            if not cc._is_def:
                continue
            if cc == 1:
                continue
            if cc == 0:
                logger.verbose("invalid mapper eval: cond %s is false" % c)
                raise ValueError
            mm.conds.append(cc)
        for loc, v in self:
            if loc._is_ptr:
                loc = m(loc)
            mm[loc] = m(v)
        return mm

    def rcompose(self, m):
        """composition operator returns a new mapper
           corresponding to function x -> self(m(x))
        """
        mm = m.use()
        for c in self.conds:
            cc = c.eval(m)
            if not cc._is_def:
                continue
            if cc == 1:
                continue
            if cc == 0:
                logger.verbose("invalid mapper eval: cond %s is false" % c)
                raise ValueError
            mm.conds.append(cc)
        for loc, v in self:
            if loc._is_ptr:
                loc = m(loc)
            mm[loc] = m(v)
        return mm

    def __lshift__(self, m):
        "self << m : composition (self(m))"
        return self.rcompose(m)

    def __rshift__(self, m):
        "self >> m : composition (m(self))"
        return m.rcompose(self)

    def interact(self):
        raise NotImplementedError

    def use(self, *args, **kargs):
        """return a new mapper corresponding to the evaluation of the current mapper
           where all key symbols found in kargs are replaced by their values in
           all expressions. The kargs "size=value" allows for adjusting symbols/values
           sizes for all arguments.
           if kargs is empty, a copy of the result is just a copy of current mapper.
        """
        m = mapper(csi=self.csi)
        for loc, v in args:
            m[loc] = v
        if len(kargs) > 0:
            argsz = kargs.get("size", 32)
            for k, v in iter(kargs.items()):
                m[reg(k, argsz)] = cst(v, argsz)
        return self.eval(m)

    def usemmap(self, mmap):
        """return a new mapper corresponding to the evaluation of the current mapper
           where all memory locations of the provided mmap are used by the current
           mapper."""
        m = mapper()
        m.setmemory(mmap)
        for xx in set(self.inputs()):
            if xx._is_mem:
                v = m.M(xx)
                m[xx] = v
        return self << m

    # attach/apply conditions to the output mapper
    def assume(self, conds):
        m = mapper(csi=self.csi)
        if conds is None:
            conds = []
        for c in conds:
            if not c._is_eqn:
                continue
            if c.op.symbol == OP_EQ and c.r._is_cst:
                if c.l._is_reg:
                    m[c.l] = c.r
        m.conds = conds
        mm = self.eval(m)
        mm.conds += conds
        return mm


from amoco.cas.smt import *


def merge(m1, m2, **kargs):
    "union of two mappers"
    m1 = m1.assume(m1.conds)
    m2 = m2.assume(m2.conds)
    mm = mapper()
    # "import" m2 values into m1 locations:
    for loc, v1 in m1:
        if loc._is_ptr:
            seg = loc.seg
            disp = loc.disp
            if loc.base._is_vec:
                v2 = vec([m2[mem(l, v1.size, seg, disp)] for l in loc.base.l])
                v2 = v2.simplify(**kargs)
            else:
                v2 = m2[mem(loc, v1.size)]
        else:
            if loc._is_reg and loc.type == regtype.FLAGS:
                v2 = top(loc.size)
            else:
                v2 = m2[loc]
        v1 = v1.simplify(**kargs)
        v2 = v2.simplify(**kargs)
        vv = vec([v1, v2]).simplify(**kargs)
        mm[loc] = vv
    # "import" m1 values into m2 locations:
    for loc, v2 in m2:
        if mm.has(loc):
            continue
        if loc._is_ptr:
            seg = loc.seg
            disp = loc.disp
            if loc.base._is_vec:
                v1 = vec([m1[mem(l, v2.size, seg, disp)] for l in loc.base.l])
                v1 = v1.simplify(**kargs)
            else:
                v1 = m1[mem(loc, v2.size)]
        else:
            if loc._is_reg and loc.type == regtype.FLAGS:
                v1 = top(loc.size)
            else:
                v1 = m1[loc]
        v2 = v2.simplify(**kargs)
        v1 = v1.simplify(**kargs)
        vv = vec([v1, v2]).simplify(**kargs)
        mm[loc] = vv
    return mm
