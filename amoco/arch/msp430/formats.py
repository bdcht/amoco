# -*- coding: utf-8 -*-
from .env import *
from amoco.arch.core import Formatter
from amoco.ui.render import Token, TokenListJoin, highlight

def mn(m,pad=8):
    return [(Token.Mnemonic, m.lower().ljust(pad))]

def mnemo(i,pad=8):
    m = i.mnemonic
    if i.BW: m+='.B'
    return mn(m)

def jump(i):
    m = i.mnemonic.lower().replace('jcc','j')
    s = COND[i.cond][0].split('/')[0]
    l = mn(m+s)
    adr = i.operands[0].value
    if i.address is None:
        l.append((Token.Constant,'.%+'%adr))
    else:
        l.append((Token.Address,'*%s'%(i.address+adr+2)))
    return l

def ops(i):
    s = []
    for o in i.operands:
        if   o._is_slc:
            assert i.BW
            o = o.x
        if   o._is_reg:
            s.append((Token.Register,str(o)))
        elif o._is_cst:
            s.append((Token.Constant,'#%s'%o))
        else:
            assert o._is_mem
            a = o.a.base
            disp = o.a.disp
            if disp==0 and a._is_reg:
                if i.misc['autoinc'] is a:
                    s.append((Token.Memory,'@%s+'%a))
                else:
                    s.append((Token.Memory,'@%s'%a))
            elif a._is_cst:
                a.sf = False
                s.append((Token.Memory,'&%s'%a))
            else:
                if a._is_eqn:
                    l,r = a.l,a.r
                else:
                    l,r = a,disp
                if l==pc and i.address:
                    s.append((Token.Address,'*%s'%(i.address+r)))
                else:
                    s.append((Token.Memory,'%s(%s)'%(r,l)))
    return TokenListJoin(', ',s)

MSP430_full_formats = {
    'msp430_doubleop' :  [mnemo, ops],
    'msp430_singleop' :  [mnemo, ops],
    'msp430_jumps'    :  [jump],
}

MSP430_full = Formatter(MSP430_full_formats)

def MSP430_synthetic(null,i,toks=False):
    s = MSP430_full(i,True)
    if i.mnemonic == 'ADDC' and i.operands[0]==0:
        s[0] = mn('adc')[0]
        del s[1:3]
    elif i.mnemonic == 'DADD' and i.operands[0]==0:
        s[0] = mn('dadc')[0]
        del s[1:3]
    elif i.mnemonic == 'CMP' and i.operands[0]==0:
        s[0] = mn('tst')[0]
        del s[1:3]
    elif i.mnemonic == 'MOV':
        if i.operands[1] is pc:
            s[0] = mn('br')[0]
            del s[2:4]
        elif i.operands[0]==0:
            s[0] = mn('clr')[0]
            del s[1:3]
        elif i.misc['autoinc'] is sp:
            if i.operands[1] is pc:
                s = mn('ret')
            else:
                s[0] = mn('pop')[0]
                del s[1:3]
    elif i.mnemonic == 'BIC':
        if i.operands[1] is sr:
            m = None
            if   i.operands[0]==1: m = 'clrc'
            elif i.operands[0]==4: m = 'clrn'
            elif i.operands[0]==2: m = 'clrz'
            elif i.operands[0]==8: m = 'dint'
            if m: s = mn(m)
    elif i.mnemonic == 'BIS':
        if i.operands[1] is sr:
            m = None
            if   i.operands[0]==1: m = 'setc'
            elif i.operands[0]==4: m = 'setn'
            elif i.operands[0]==2: m = 'setz'
            elif i.operands[0]==8: m = 'eint'
            if m: s = mn(m)
    elif i.mnemonic == 'SUB' and i.operands[0]==1:
        s[0] = mn('dec')[0]
        del s[1:3]
    elif i.mnemonic == 'SUB' and i.operands[0]==2:
        s[0] = mn('decd')[0]
        del s[1:3]
    elif i.mnemonic == 'ADD' and i.operands[0]==1:
        s[0] = mn('inc')[0]
        del s[1:3]
    elif i.mnemonic == 'ADD' and i.operands[0]==2:
        s[0] = mn('incd')[0]
        del s[1:3]
    elif i.mnemonic == 'XOR' and i.operands[0].signextend(16).value==-1:
        s[0] = mn('inv')[0]
        del s[1:-1]
    if toks: return s
    return highlight(s)
