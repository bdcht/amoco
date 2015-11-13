# -*- coding: utf-8 -*-

from .env import *
from .utils import *
from amoco.arch.core import Formatter

whitespace = '  '

def regs(i):
    return ['%{0}'.format(r) for r in i.operands]

def address(a):
    if not a._is_eqn:
        return '%'+str(a)
    l = reg_or_imm(a.l)
    op = a.op.symbol
    r = reg_or_imm(a.r)
    return '{0}{1}{2}'.format(l,op,r)

def deref(a):
    return '[%s]%s'%(address(a.base+a.disp),a.seg)

def mnemo_icc(i):
    s = i.mnemonic
    if i.misc['icc']: s += 'cc'
    return s+whitespace

def mnemo_cond(i):
    s = CONDxB[i.mnemonic][i.cond]
    if i.misc['annul']:
        s+=',a'
    return s+whitespace

def reg_or_imm(x,t='%d'):
    # Special detections for %hi or %lo
    hilo = None
    if x._is_cmp:
        if sorted(x.parts.keys()) == [(0,10),(10,32)]:
            if str(x.parts[(10,32)]) == "0x0":
                hilo = ['%lo', x.parts[(0,10)].x]
            if str(x.parts[(0,10)]) == "0x0":
                hilo = ['%hi', x.parts[(10,32)].x]
    elif x._is_slc:
        if x.pos == 10 and x.size == 22:
             hilo = ['%hi', x.x]
        if x.pos == 0 and x.size == 10:
             hilo = ['%lo', x.x]
    # Other cases
    elif x._is_ext:
        return x.ref
    elif x._is_reg:
        return '%'+x.ref
    elif x._is_cst:
        return t%x.value
    elif x._is_eqn:
        if x.r is None:
            return ("%s"+t)%(x.op.symbol,x.l)
        elif x.l is None:
            return ("%s"+t)%(x.op.symbol,x.r)
        else:
            return (t+"%s"+t)%(x.l,x.op.symbol,x.r)
    # Now dealing with hilo
    if hilo is None:
        return str(x)
    elif hilo[1]._is_eqn:
        hilo[1] = address(hilo[1])
    elif hilo[1]._is_cst:
        pass
    else:
        hilo[1] = hilo[1].ref
    return '%s(%s)'%tuple(hilo)

def label(i):
    _pc = i.address
    if _pc is None: _pc=pc
    if i.operands[0]._is_ext:
        return str(i.operands[0].ref)
    if i.operands[0]._is_reg:
        return "%"+str(i.operands[0].ref)
    if i.operands[0]._is_cst:
        return "%s"%i.misc['dst']
    offset = i.operands[0].signextend(32)*4
    return str(_pc+offset)


CONDB = {
  0b1000: 'ba',
  0b0000: 'bn',
  0b1001: 'bne',
  0b0001: 'be',
  0b1010: 'bg',
  0b0010: 'ble',
  0b1011: 'bge',
  0b0011: 'bl',
  0b1100: 'bgu',
  0b0100: 'bleu',
  0b1101: 'bcc',
  0b0101: 'bcs',
  0b1110: 'bpos',
  0b0110: 'bneg',
  0b1111: 'bvc',
  0b0111: 'bvs'
}
CONDFB = {
  0b1000: 'fba',
  0b0000: 'fbn',
  0b0111: 'fbu',
  0b0110: 'fbg',
  0b0101: 'fbug',
  0b0100: 'fbl',
  0b0011: 'fbul',
  0b0010: 'fblg',
  0b0001: 'fbne',
  0b1001: 'fbe',
  0b1010: 'fbue',
  0b1011: 'fbge',
  0b1100: 'fbuge',
  0b1101: 'fble',
  0b1110: 'fbule',
  0b1111: 'fbo'
}
CONDCB = {
  0b1000: 'cba',
  0b0000: 'cbn',
  0b0111: 'cb3',
  0b0110: 'cb2',
  0b0101: 'cb23',
  0b0100: 'cb1',
  0b0011: 'cb13',
  0b0010: 'cb12',
  0b0001: 'cb123',
  0b1001: 'cb0',
  0b1010: 'cb03',
  0b1011: 'cb02',
  0b1100: 'cb023',
  0b1101: 'cb01',
  0b1110: 'cb013',
  0b1111: 'cb012'
}
CONDT = {
  0b1000: 'ta',
  0b0000: 'tn',
  0b1001: 'tne',
  0b0001: 'te',
  0b1010: 'tg',
  0b0010: 'tle',
  0b1011: 'tge',
  0b0011: 'tl',
  0b1100: 'tgu',
  0b0100: 'tleu',
  0b1101: 'tcc',
  0b0101: 'tcs',
  0b1110: 'tpos',
  0b0110: 'tneg',
  0b1111: 'tvc',
  0b0111: 'tvs'
}

CONDxB = {'b': CONDB, 'fb': CONDFB, 'cb': CONDCB}

mnemo = '{i.mnemonic}'+whitespace
format_mn     = [mnemo]
format_regs   = [mnemo, lambda i: ', '.join(regs(i))]
format_ld     = [mnemo, lambda i: deref(i.operands[0]), ', %{i.operands[1]}']
format_st     = [mnemo, '%{i.operands[0]}, ', lambda i: deref(i.operands[1])]
format_logic  = [mnemo_icc, '%{i.operands[0]}, ', lambda i: reg_or_imm(i.operands[1],'%#x'), ', %{i.operands[2]}']
format_sethi  = [mnemo, lambda i: reg_or_imm(i.operands[0]), ', %{i.operands[1]}']
format_arith  = [mnemo_icc, '%{i.operands[0]}, ', lambda i: reg_or_imm(i.operands[1],'%d'), ', %{i.operands[2]}']
format_xb     = [mnemo_cond, label]
format_call   = [mnemo, label, ', 0']
format_jmpl   = [mnemo, lambda i: address(i.operands[0]), ', %{i.operands[1]}']
format_addr   = [mnemo, lambda i: address(i.operands[0])]
format_t      = [lambda i: CONDT[i.cond]+whitespace, lambda i: reg_or_imm(i.operands[0])]
format_rd     = format_regs
format_wr     = [mnemo, '%{i.operands[0]}, ', lambda i: reg_or_imm(i.operands[1],'%#x'), ', %{i.operands[2]}']
format_fpop   = format_regs
format_cpop   = [mnemo, '{i.operands[0]:d}', lambda i: ', '.join(regs(i)[1:])]

SPARC_V8_full_formats = {
    'sparc_ld_'         : format_ld,
    'sparc_ldf_ldc'     : format_ld,
    'sparc_st_'         : format_st,
    'sparc_stf_stc'     : format_st,
    'sparc_logic_'      : format_logic,
    'sethi'             : format_sethi,
    'nop'               : format_mn,
    'sparc_arith_'      : format_arith,
    'sparc_shift_'      : format_arith,
    'sparc_tagged_'     : format_arith,
    'sparc_Bicc'        : format_xb,
    'call'              : format_call,
    'jmpl'              : format_jmpl,
    'rett'              : format_addr,
    't'                 : format_t,
    'sparc_rd_'         : format_rd,
    'sparc_wr_'         : format_wr,
    'stbar'             : format_mn,
    'flush'             : format_addr,
    'sparc_Fpop1_group1': format_rd,
    'sparc_Fpop1_group2': format_fpop,
    'sparc_Fpop2_'      : format_rd,
    'sparc_Cpop'        : format_cpop,
}

SPARC_V8_full = Formatter(SPARC_V8_full_formats)

def SPARC_V8_synthetic(null,i,toks=False):
    s = SPARC_V8_full(i)
    return SPARC_Synthetic_renaming(s, i)

def SPARC_Synthetic_renaming(s, i):
    if i.mnemonic=='sethi' and i.operands[0]==cst(0,22) and i.operands[1]==g0:
        return 'nop'
    if i.mnemonic=='or' and not i.misc['icc'] and i.operands[0]==i.operands[1]==g0:
        return s.replace('or','clr').replace('%g0, ','')
    if i.mnemonic=='or' and not i.misc['icc'] and i.operands[0]==g0:
        return s.replace('or','mov').replace('%g0, ','')
    if i.mnemonic=='or' and not i.misc['icc'] and i.operands[0]==i.operands[2]:
        return s.replace('or','bset').replace('%%%s,'%i.operands[0],'',1)
    if i.mnemonic=='rd':
        op1 = str(i.operands[0])
        if op1.startswith('asr') or op1 in ('y','psr','wim','tbr'):
            return s.replace('rd','mov')
    if i.mnemonic=='wr' and i.operands[0]==g0:
        return s.replace('wr','mov').replace('%g0,','')
    if i.mnemonic=='sub' and i.misc['icc'] and i.operands[2]==g0:
        return s.replace('subcc','cmp').replace(', %g0','')
    if i.mnemonic=='jmpl' and i.operands[1]==g0:
        if i.operands[0] == (i7+cst(8)):
            return 'ret'
        if i.operands[0] == (o7+cst(8)):
            return 'retl'
        return s.replace('jmpl','jmp').replace(', %g0','')
    if i.mnemonic=='jmpl' and i.operands[1]==o7:
        return s.replace('jmpl','call').replace(', %o7','')
    if i.mnemonic=='or' and i.misc['icc'] and i.operands[1]._is_reg and i.operands[0]==i.operands[2]==g0:
        return s.replace('orcc','tst').replace('%g0,','').replace(', %g0','')
    if i.mnemonic=='restore' and i.operands[0]==i.operands[1]==i.operands[2]==g0:
        return 'restore'
    if i.mnemonic=='save' and i.operands[0]==i.operands[1]==i.operands[2]==g0:
        return 'save'
    if i.mnemonic=='xnor' and i.operands[1]==g0:
        s = s.replace('xnor','not').replace('%g0,','',1)
        if i.operands[0]==i.operands[2]:
            return s.rpartition(',')[0]
        return s
    if i.mnemonic=='sub' and i.operands[0]==g0 and i.operands[1]._is_reg:
        s = s.replace('sub','neg').replace('%g0,','',1)
        if i.operands[1]==i.operands[2]:
            return s.rpartition(',')[0]
        return s
    if i.mnemonic=='add' and i.operands[0]==i.operands[2] and i.operands[1]._is_cst:
        m = 'inccc' if i.misc['icc'] else 'inc'
        if i.operands[1]==1:
            return '{}{}%{}'.format(m,whitespace,i.operands[0])
        else:
            return '{}{}{}, %{}'.format(m,whitespace,i.operands[1],i.operands[0])
    if i.mnemonic=='sub' and i.operands[0]==i.operands[2] and i.operands[1]._is_cst:
        m = 'deccc' if i.misc['icc'] else 'dec'
        if i.operands[1]==1:
            return '{} %{}'.format(m,i.operands[0])
        else:
            return '{}{}{}, %{}'.format(m,whitespace,i.operands[1],i.operands[0])
    if i.mnemonic=='and' and i.misc['icc'] and i.operands[2]==g0:
        s = s.replace('andcc','btst').replace(', %g0','')
        m = s.split()
        return '{}{}{}, {}'.format(m[0],whitespace,m[2],m[1].replace(',',''))
    if i.mnemonic=='andn' and not i.misc['icc'] and i.operands[0]==i.operands[2]:
        return s.replace('andn','bclr').replace('%%%s,'%i.operands[0],'',1)
    if i.mnemonic=='xor' and not i.misc['icc'] and i.operands[0]==i.operands[2]:
        return s.replace('xor','btog').replace('%%%s,'%i.operands[0],'',1)
    if i.mnemonic=='stb' and i.operands[0]==g0:
        return s.replace('stb','clrb').replace('%g0, ','')
    if i.mnemonic=='sth' and i.operands[0]==g0:
        return s.replace('sth','clrh').replace('%g0, ','')
    if i.mnemonic=='st' and i.operands[0]==g0:
        return s.replace('st','clr').replace('%g0, ','')
    return s
