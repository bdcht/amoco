# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2015 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.logger import Log
logger = Log(__name__)

from .expressions import *
from amoco.cas.mapper import mapper

try:
    import z3
except ImportError:
    logger.info('z3 package not found => solve() method is not implemented')
    class solver(object):
        def __init__(self,eqns=None):
            raise NotImplementedError
    has_solver = False
else:
    logger.info('z3 package imported')
    class solver(object):
        def __init__(self,eqns=None):
            self.eqns = []
            self.locs = []
            self.solver = z3.Solver()
            if eqns: self.add(eqns)
            self._ctr = 0

        def add(self,eqns):
            for e in eqns:
                self.eqns.append(e)
                self.locs.extend(locations_of(e))

                if e._is_eqn:
                    self.solver.add(e.to_smtlib(solver=self))
                else:  # reduced to "0x0" or "0x1"
                    self.solver.add(bool(e))

        def check(self):
            logger.verbose('z3 check...')
            return self.solver.check()

        def get_model(self,eqns=None):
            if eqns is not None: self.add(eqns)
            if self.check() == z3.sat:
                r = self.solver.model()
                return r

        def get_mapper(self,eqns=None):
            r = self.get_model(eqns)
            if r is not None:
                return model_to_mapper(r,self.locs)

        @property
        def ctr(self):
            ctr = self._ctr
            self._ctr+=1
            return ctr

    has_solver = True

def newvar(pfx,e,solver):
    s = '' if solver is None else '%d'%solver.ctr
    return z3.BitVec("%s%s"%(pfx,s),e.size)

def top_to_z3(e,solver=None):
    return newvar('_top',e,solver)

def cst_to_z3(e,solver=None):
    return z3.BitVecVal(e.v,e.size)

def cfp_to_z3(e,solver=None):
    return z3.RealVal(e.v)

def reg_to_z3(e,solver=None):
    return z3.BitVec(e.ref,e.size)

def comp_to_z3(e,solver=None):
    e.simplify()
    parts = [x.to_smtlib() for x in e]
    parts.reverse()
    if len(parts)>1:
        return z3.Concat(*parts)
    else:
        return parts[0]

def slc_to_z3(e,solver=None):
    x = e.x.to_smtlib()
    return z3.Extract(int(e.pos+e.size-1),int(e.pos),x)

def ptr_to_z3(e,solver=None):
    return e.base.to_smtlib()+e.disp

def mem_to_z3(e,solver=None):
    e.simplify()
    M = z3.Array('M',z3.BitVecSort(e.a.size),z3.BitVecSort(8))
    p = e.a.to_smtlib()
    b = []
    for i in range(0,e.length):
        b.insert(0,M[p+i])
    if e._endian==-1: b.reverse() # big-endian case
    if len(b) > 1: return z3.Concat(*b)
    return b[0]

def cast_z3_bool(x):
    b = x.to_smtlib()
    if not z3.is_bool(b):
        assert b.size()==1
        b = (b==z3.BitVecVal(1,1))
    return b

def tst_to_z3(e,solver=None):
    e.simplify()
    z3t = cast_z3_bool(e.tst)
    return z3.If( z3t , e.l.to_smtlib(), e.r.to_smtlib())

def tst_verify(e,env):
    t = e.tst.eval(env).simplify()
    zt = cast_z3_bool(t)
    s = z3.Solver()
    for c in env.conds:
        s.add(cast_z3_bool(c))
    s.push()
    s.add(zt)
    rtrue = (s.check()==z3.sat)
    s.pop()
    s.add(z3.Not(zt))
    rfalse = (s.check()==z3.sat)
    if rtrue and rfalse: return t
    if rtrue: return bit1
    if rfalse: return bit0
    # mapper conds are unsatisfiable:
    raise ValueError(e)

def op_to_z3(e,solver=None):
    e.simplify()
    l,r = e.l,e.r
    op = e.op
    if   op.symbol == '>>' : op = z3.LShR
    elif op.symbol == '//' : op = operator.rshift
    elif op.symbol == '>>>': op = z3.RotateRight
    elif op.symbol == '<<<': op = z3.RotateLeft
    z3l = l.to_smtlib()
    z3r = r.to_smtlib()
    if z3.is_bool(z3l):
        z3l = _bool2bv1(z3l)
    if z3.is_bool(z3r):
        z3r = _bool2bv1(z3r)
    if z3l.size() != z3r.size():
        greatest = max(z3l.size(), z3r.size())
        z3l = z3.ZeroExt(greatest - z3l.size(), z3l)
        z3r = z3.ZeroExt(greatest - z3r.size(), z3r)
    return op(z3l,z3r)

def uop_to_z3(e,solver=None):
    e.simplify()
    r = e.r
    op = e.op
    z3r = r.to_smtlib()
    if z3.is_bool(z3r):
        z3r = _bool2bv1(z3r)
    return op(z3r)

def vec_to_z3(e,solver=None):
    e.simplify()
    beqs = []
    for x in e.l:
        zx = x.to_smtlib()
        beqs.append(zx)
    if len(beqs)==0: return exp(e.size)
    if solver is None:
        if all([z3.is_bool(x) for x in beqs]):
            if len(beqs)==1: return beqs[0]
            return z3.Or(*beqs)
        else:
            return top_to_z3(top(e.size))
    else:
        var = newvar('_var',e,solver)
        solver.add(z3.Or([var==x for x in beqs]))
    return var

def _bool2bv1(z):
    return z3.If(z,z3.BitVecVal(1,1),z3.BitVecVal(0,1))

if has_solver:
    top.to_smtlib  = top_to_z3
    cst.to_smtlib  = cst_to_z3
    cfp.to_smtlib  = cfp_to_z3
    reg.to_smtlib  = reg_to_z3
    comp.to_smtlib = comp_to_z3
    slc.to_smtlib  = slc_to_z3
    ptr.to_smtlib  = ptr_to_z3
    mem.to_smtlib  = mem_to_z3
    tst.to_smtlib  = tst_to_z3
    tst.verify     = tst_verify
    op.to_smtlib   = op_to_z3
    uop.to_smtlib   = uop_to_z3
    vec.to_smtlib  = vec_to_z3

def to_smtlib(e):
    return e.to_smtlib()

def model_to_mapper(r,locs):
    m = mapper()
    mlocs = []
    for l in locs:
        if l._is_mem:
            mlocs.append(l)
        else:
            m[l] = cst(r.eval(l.to_smtlib()).as_long(),l.size)
    for l in mlocs:
        m[l] = cst(r.eval(l.to_smtlib()).as_long(),l.size)
    return m
