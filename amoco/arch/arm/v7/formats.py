# -*- coding: utf-8 -*-

from .env import *
from .utils import *
from amoco.arch.core import Formatter

from amoco.ui.render import Token, TokenListJoin

def mnemo(i):
    m = i.mnemonic
    if hasattr(i,'setflags') and i.setflags:
        m += 'S'
    if hasattr(i,'cond') and i.cond!=CONDITION_AL:
        m += '.%s'%CONDITION[i.cond][0]
    return [(Token.Mnemonic,'%s'%(m.lower()).ljust(12))]

def regs(i,limit=None):
    ops = i.operands
    if limit: ops = ops[:limit]
    return [(Token.Register,'{0}'.format(r)) for r in ops]

def reglist(i,pos=-1):
    l = i.operands[pos]
    return [(Token.Register,"{%s}"%(', '.join(['{0}'.format(r) for r in l])))]

def deref(i,pos=-2):
    assert len(i.operands)>2
    base,offset = i.operands[pos], i.operands[pos+1]
    sign = '+' if i.add else '-'
    if offset._is_cst:
        ostr = '#%c%d'%(sign,offset.value)
    else:
        ostr = sign+str(offset)
    if hasattr(i,'wback'):
        wb = '!' if i.wback else ''
        if i.index:
            loc = '[%s, %s]%s'%(base, ostr, wb)
        else:
            loc = '[%s], %s'%(base, ostr)
    else:
        loc = '[%s], %s'%(base,ostr)
    return [(Token.Memory,loc)]

def label(i,pos=0):
    _pc = i.address
    if _pc is None: _pc=pc
    pcoffset = 4 if internals['isetstate']==0 else 2
    _pc = _pc + 2*pcoffset
    offset = i.operands[pos]
    return [(Token.Address,'*'+str(_pc+offset))]

def setend(i):
    endian_specifier = 'BE' if i.set_bigend else 'LE'
    return mnemo(i)+[(Token.Literal,endian_specifier)]

def plx(i):
    m = mnemo(i)
    base,offset = i.operands[-2], i.operands[-1]
    sign = '+' if i.add else '-'
    if offset._is_cst:
        ostr = '#%c%d'%(sign,offset.value)
    else:
        ostr = sign+str(offset)
    loc = [(Token.Memory,'[%s, %s]'%(base, ostr))]
    return m+loc

def specreg(i):
    spec_reg = "%s_"%apsr
    if i.write_nzcvq: spec_reg += 'nzcvq'
    if i.write_g: spec_reg += 'g'
    return [(Token.Register,'%s, %s'%(i.operands[0],spec_reg))]

format_allregs = [lambda i: TokenListJoin(', ',regs(i))]
format_default = [mnemo]+format_allregs
format_sreg    = format_default
format_label   = [mnemo, label]
format_adr     = [mnemo, lambda i: regs(i,1), lambda i: label(i,1)]
format_bits    = format_default
format_reglist = [mnemo, (lambda i: TokenListJoin(', ',regs(i,-1))), reglist]
format_deref   = [mnemo, lambda i: TokenListJoin(', ',regs(i,-2)+deref(i,-2))]
format_plx     = [plx]
format_msr     = [mnemo, specreg]
format_setend  = [setend]

ARM_V7_full_formats = {
    'A_default'         : format_default,
    'A_sreg'            : format_sreg,
    'A_label'           : format_label,
    'A_adr'             : format_adr,
    'A_bits'            : format_bits,
    'A_reglist'         : format_reglist,
    'A_deref'           : format_deref,
    'instr_PLx'         : format_plx,
    'instr_MSR'         : format_msr,
    'instr_SETEND'      : format_setend,
}

ARM_V7_full = Formatter(ARM_V7_full_formats)

