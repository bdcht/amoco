# -*- coding: utf-8 -*-

from .env import *
from amoco.arch.core import Formatter
from amoco.ui.render import Token, TokenListJoin

def mnemo(i):
    m = i.mnemonic
    return [(Token.Mnemonic,'%s'%(m.lower()).ljust(12))]

def opers(i):
    L = []
    for pos,o in enumerate(i.operands):
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

def opreg(pos):
    def subr(i,pos=pos):
        o = i.operands[pos]
        assert o._is_reg
        if i.misc['W'] and o in i.misc['W']:
            return [(Token.Register,'{1}:{0}'.format(o,R[[r.ref for r in R].index(o.ref)+1]))]
        return [(Token.Register,'{0}'.format(o))]
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
        loc = '{0}'.format(i.operands[pos])
        if i.misc['flg']==-1: loc = '-'+loc
        loc = '[{0}]'.format(loc)
        if i.misc['flg']==+1: loc = loc+'+'
        return [(Token.Memory,loc)]
    return deref

def pcrel(pos):
    def subpc(i,pos=pos):
        npc = i.address
        if npc is None: npc=pc
        npc += i.length
        offset = i.operands[pos]
        tgt = npc + 2*offset
        return [(Token.Address,'*'+str(tgt))]
    return subpc

def opadr(pos):
    def subabs(i,pos=pos):
        tgt = i.operands[pos]
        tgt = 2*tgt
        return [(Token.Address,'*'+str(tgt))]
    return subabs

def format_mem(i):
    s = i.misc['mem']
    if   s == 1:
        return listjoin(opreg(0),opmem(1))(i)
    elif s == 2:
        return listjoin(opmem(0),opreg(1))(i)
    else:
        raise ValueError(s)

def format_brc(i):
    b = i.operands[0].ref
    if i.mnemonic == 'BRBC':
        if   b is 'C': mn = 'BRCC'
        elif b is 'Z': mn = 'BRNE'
        elif b is 'N': mn = 'BRPL'
        elif b is 'V': mn = 'BRVC'
        elif b is 'S': mn = 'BRGE'
        elif b is 'H': mn = 'BRHC'
        elif b is 'T': mn = 'BRTC'
        elif b is 'I': mn = 'BRID'
    if i.mnemonic == 'BRBS':
        if   b is 'C': mn = 'BRCS'
        elif b is 'Z': mn = 'BREQ'
        elif b is 'N': mn = 'BRMI'
        elif b is 'V': mn = 'BRVS'
        elif b is 'S': mn = 'BRLT'
        elif b is 'H': mn = 'BRHS'
        elif b is 'T': mn = 'BRTS'
        elif b is 'I': mn = 'BRIE'
    L=[(Token.Mnemonic,'%s'%(mn.lower()).ljust(12))]
    L.extend(pcrel(1)(i))
    return L

AVR_full_formats = {
    'avr_default' : [mnemo, opers],
    'avr_ld'      : [mnemo, format_mem],
    'avr_lax'     : [mnemo, listjoin(opmem(0),opreg(1))],
    'avr_brc'     : [format_brc],
    'avr_br'      : [mnemo, pcrel(0)],
    'avr_noops'   : [mnemo],
    'avr_call'    : [mnemo, opadr(0)],
}

AVR_full = Formatter(AVR_full_formats)
AVR_full.default = [mnemo,opers]
