# -*- coding: utf-8 -*-

from .env import *
from amoco.arch.core import Formatter
from amoco.ui.render import Token, TokenListJoin

def mnemo(i):
    m = i.mnemonic
    return [(Token.Mnemonic,'%s'%(m.lower()).ljust(12))]

def mnemo_ldst(i):
    m,s = i.mnemonic[:-1],i.mnemonic[-1:]
    if s in ('B','H','W'):
        m = '%s.%s'%(m,s)
    else:
        m = '%s.%s'%(i.mnemonic[:-2],i.mnemonic[-2:])
    return [(Token.Mnemonic,'%s'%(m.lower()).ljust(12))]

def mnemo_cond(i):
    m = i.mnemonic
    c = CONDITION[i.cond]
    return [(Token.Mnemonic,'%s.%s'%(m.lower(),c).ljust(12))]

def opers(i,n=0):
    L = []
    for pos,o in enumerate(i.operands[n:]):
        if   o._is_reg: L.append(opreg(pos))
        elif o._is_cst: L.append(opcst(pos))
        elif o._is_mem: L.append(opmem(pos))
    return listjoin(*L)(i)

def listjoin(*args):
    def subf(i,L=args):
        X = []
        for l in L: X.extend(l(i))
        return TokenListJoin(', ',X)
    return subf

def cond_opers(i):
    L = [(Token.Literal,CONDITION[i.operands[0]])]
    for pos,o in enumerate(i.operands[1:]):
        if   o._is_reg: L.append(opreg(pos))
        elif o._is_cst: L.append(opcst(pos))
        elif o._is_mem: L.append(opmem(pos))
    return listjoin(*L)(i)

def opreg(pos):
    def subr(i,pos=pos):
        o = i.operands[pos]
        assert o._is_reg
        return [(Token.Register,'{0}'.format(o))]
    return subr

def oplist(pos):
    def subr(i,pos=pos):
        o = i.operands[pos]
        L = [(Token.Literal,'{')]
        L += TokenListJoin(', ',[(Token.Register,'{0}'.format(x)) for x in o])
        L += [(Token.Literal,'}')]
        return L
    return subr

def opcst(pos):
    def subc(i,pos=pos):
        o = i.operands[pos]
        assert o._is_cst
        if o.sf==False:
            return [(Token.Constant,'0x%x'%o)]
        return [(Token.Constant,'%+d'%o)]
    return subc

def opmem(pos):
    def deref(i,pos=pos):
        a = i.operands[pos].a
        disp = a.disp
        loc = '{0}'.format(disp)
        loc += '[{0}]'.format(a.base)
        return [(Token.Memory,loc)]
    return deref

def pcrel(pos):
    def subpc(i,pos=pos):
        npc = i.address
        if npc is None: npc=pc
        npc += i.length
        offset = i.operands[pos]
        tgt = npc + offset
        return [(Token.Address,'*'+str(tgt))]
    return subpc

def opadr(pos):
    def subabs(i,pos=pos):
        tgt = i.operands[pos]
        return [(Token.Address,'*'+str(tgt))]
    return subabs

def format_prepare(i):
    L = oplist(0)(i)
    l = opers(i,1)
    return L+[(Token.Literal,', ')]+l

v850_full_formats = {
    'v850_ld_st'   : [mnemo_ldst, opers],
    'v850_br_cond' : [mnemo_cond, opers],
    'v850_cccc'    : [mnemo, cond_opers],
    'v850_dispose' : [mnemo, listjoin(opmem(0),oplist(1))],
    'v850_prepare' : [mnemo, format_prepare],
    'v850_pcrel'   : [mnemo, pcrel(0)],
    'v850_call'    : [mnemo, opadr(0)],
}

v850_full = Formatter(v850_full_formats)
v850_full.default = [mnemo,opers]
