from .env import *
from amoco.arch.core import Formatter

def mnemo(i,pad=8):
    m = i.mnemonic
    if i.BW: m+='.B'
    return m.lower().ljust(pad)

def mnemo_cond(i):
    m = mnemo(i,pad=0).replace('jcc','j')
    s = COND[i.cond][0].split('/')[0]
    return (m+s).lower().ljust(8)

def ops(i):
    s = []
    for o in i.operands:
        if   o._is_slc:
            assert i.BW
            o = o.x
        if   o._is_reg:
            s.append(str(o))
        elif o._is_cst:
            s.append('#%s'%o)
        else:
            assert o._is_mem
            a = o.a.base
            if a._is_reg:
                if i.misc['autoinc'] is a:
                    s.append('@%s+'%a)
                else:
                    s.append('@%s'%a)
            elif a._is_cst:
                s.append('&%s'%a)
            else:
                assert a._is_eqn
                l,r = a.l,a.r
                if l==pc and i.address:
                    s.append('*%s'%(i.address+r))
                else:
                    s.append('%s(%s)'%(r,l))
    return ', '.join(s)

MSP430_full_formats = {
    'msp430_doubleop' :  [mnemo, ops],
    'msp430_singleop' :  [mnemo, ops],
    'msp430_jumps'    :  [mnemo_cond, ops],
}

MSP430_full = Formatter(MSP430_full_formats)

def MSP430_synthetic(null,i):
    s = MSP430_full(i)
    if i.mnemonic == 'ADDC' and i.operands[0]==0:
        return s.replace('addc','adc').replace('#0x0,','')
    if i.mnemonic == 'DADD' and i.operands[0]==0:
        return s.replace('dadd','dadc').replace('#0x0,','')
    if i.mnemonic == 'CMP' and i.operands[0]==0:
        return s.replace('cmp','tst').replace('#0x0,','')
    if i.mnemonic == 'MOV':
        if i.operands[1] is pc:
            return s.replace('mov','br').replace(',pc','')
        elif i.operands[0]==0:
            return s.replace('mov','clr').replace('#0x0,','')
        elif i.misc['autoinc'] is sp:
            if i.operands[1] is pc: return 'ret'
            return s.replace('mov','pop').replace('@sp+,','')
    if i.mnemonic == 'BIC':
        if i.operands[1] is sr:
            if i.operands[0]==1: return 'clrc'
            if i.operands[0]==4: return 'clrn'
            if i.operands[0]==2: return 'clrz'
            if i.operands[0]==8: return 'dint'
    if i.mnemonic == 'BIS':
        if i.operands[1] is sr:
            if i.operands[0]==1: return 'setc'
            if i.operands[0]==4: return 'setn'
            if i.operands[0]==2: return 'setz'
            if i.operands[0]==8: return 'eint'
    if i.mnemonic == 'SUB' and i.operands[0]==1:
        return s.replace('sub','dec').replace('#0x1,','')
    if i.mnemonic == 'SUB' and i.operands[0]==2:
        return s.replace('sub','decd').replace('#0x2,','')
    if i.mnemonic == 'ADD' and i.operands[0]==1:
        return s.replace('add','inc').replace('#0x1,','')
    if i.mnemonic == 'ADD' and i.operands[0]==2:
        return s.replace('add','incd').replace('#0x2,','')
    if i.mnemonic == 'XOR' and i.operands[0].signextend(16).value==-1:
        return 'inv '+ops(i).split(',')[-1].strip()
    return s
