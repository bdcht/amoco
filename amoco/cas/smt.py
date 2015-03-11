# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2015 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.logger import Log
logger = Log(__name__)

from .expressions import *
from .mapper import mapper

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
        def add(self,eqns):
            for e in eqns:
                assert e._is_eqn
                self.eqns.append(e)
                self.solver.add(e.to_smtlib())
                self.locs.extend(locations_of(e))
        def check(self):
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
    has_solver = True

def cst_to_z3(e):
    return z3.BitVecVal(e.v,e.size)

def cfp_to_z3(e):
    return z3.RealVal(e.v)

def reg_to_z3(e):
    return z3.BitVec(e.ref,e.size)

def comp_to_z3(e):
    e.simplify()
    parts = [x.to_smtlib() for x in e]
    parts.reverse()
    return z3.Concat(*parts)

def slc_to_z3(e):
    x = e.x.to_smtlib()
    return z3.Extract(e.pos+e.size-1,e.pos,x)

def ptr_to_z3(e):
    return e.base.to_smtlib()+e.disp

def mem_to_z3(e):
    e.simplify()
    M = z3.Array('M',z3.BitVecSort(e.a.size),z3.BitVecSort(8))
    p = e.a.to_smtlib()
    b = []
    for i in range(0,e.length):
        b.insert(0,M[p+i])
    if e._endian==-1: b.reverse() # big-endian case
    return z3.Concat(*b)

def tst_to_z3(e):
    e.simplify()
    return z3.If(e.tst.to_smtlib(), e.l.to_smtlib(), e.r.to_smtlib())

def op_to_z3(e):
    e.simplify()
    l,r = e.l,e.r
    op = e.op
    if   op.symbol == '>>' : op = z3.LShR
    elif op.symbol == '//' : op = operator.rshift
    elif op.symbol == '>>>': op = z3.RotateRight
    elif op.symbol == '<<<': op = z3.RotateLeft
    z3l = l.to_smtlib()
    if r is None: return op(z3l)
    z3r = r.to_smtlib()
    if z3l.size() != z3r.size():
        greatest = max(z3l.size(), z3r.size())
        z3l = z3.ZeroExt(greatest - z3l.size(), z3l)
        z3r = z3.ZeroExt(greatest - z3r.size(), z3r)
    return op(z3l,z3r)

cst.to_smtlib  = cst_to_z3
cfp.to_smtlib  = cfp_to_z3
reg.to_smtlib  = reg_to_z3
comp.to_smtlib = comp_to_z3
slc.to_smtlib  = slc_to_z3
ptr.to_smtlib  = ptr_to_z3
mem.to_smtlib  = mem_to_z3
tst.to_smtlib  = tst_to_z3
op.to_smtlib   = op_to_z3

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
