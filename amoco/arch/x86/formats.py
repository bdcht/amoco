# -*- coding: utf-8 -*-

from amoco.cas.expressions import regtype
from amoco.arch.core import Formatter,Token

def pfx(i):
    if i.misc['pfx'] is None: return ''
    pfxgrp0 = i.misc['pfx'][0]
    if pfxgrp0 is None: return ''
    return [(Token.Prefix,'%s '%pfxgrp0)]

def mnemo(i):
    mnemo = i.mnemonic.replace('cc','')
    if hasattr(i,'cond'): mnemo += i.cond[0].split('/')[0]
    return [(Token.Mnemonic,'{: <12}'.format(mnemo.lower()))]

def deref(op):
    assert op._is_mem
    s = {8:'byte ptr ',16:'word ptr ', 64:'qword ptr ', 128:'xmmword ptr '}.get(op.size,'')
    s += '%s:'%op.a.seg  if (op.a.seg is not '')  else ''
    b = op.a.base
    if op.a.base._is_reg and op.a.base.type==regtype.STACK:
        base10=True
    else:
        base10=False
    s += '[%s%s]'%(op.a.base,op.a.disp_tostring(base10))
    return s

def opers(i):
    s = []
    for op in i.operands:
        if op._is_mem:
            s.append((Token.Memory,deref(op)))
        elif op._is_cst:
            if i.misc['imm_ref'] is not None:
                s.append((Token.Address,str(i.misc['imm_ref'])))
            elif op.sf:
                s.append((Token.Constant,'%+d'%op.value))
            else:
                s.append((Token.Constant,str(op)))
        elif op._is_reg:
            s.append((Token.Register,str(op)))
        s.append((Token.Literal,', '))
    if len(s)>0: s.pop()
    return s

def oprel(i):
    to = i.misc['to']
    if to is not None:
        return [(Token.Address,'*'+str(to))]
    if (i.address is not None) and i.operands[0]._is_cst:
        v = i.address + i.operands[0].signextend(32) + i.length
        i.misc['to'] = v
        return [(Token.Address,'*'+str(v))]
    return [(Token.Constant,'.%+d'%i.operands[0].value)]

# main intel formats:
format_intel_default = (mnemo,opers)

format_intel_ptr = (mnemo,opers)

format_intel_str = (pfx,mnemo,opers)

format_intel_rel = (mnemo,oprel)

# intel formats:
IA32_Intel_formats = {
    'ia32_strings' : format_intel_str,
    'ia32_mov_adr' : format_intel_ptr,
    'ia32_ptr_ib'  : format_intel_ptr,
    'ia32_ptr_iwd' : format_intel_ptr,
    'ia32_rm8'     : format_intel_ptr,
    'ia32_rm32'    : format_intel_ptr,
    'ia32_imm_rel' : format_intel_rel,
}

IA32_Intel = Formatter(IA32_Intel_formats)
IA32_Intel.default = format_intel_default

#------------------------------------------------------------------------------
# AT&T formats:

def mnemo_att(i):
    mnemo = i.mnemonic.replace('cc','')
    opdsz = i.misc['opdsz']
    if  opdsz==16: mnemo+='w'
    elif opdsz==8: mnemo+='b'
    elif hasattr(i,'cond'):
        mnemo += i.cond[0].split('/')[0]
    return [(Token.Mnemonic,'{: <12}'.format(mnemo.lower()))]

def deref_att(op):
    assert op._is_mem
    disp = '%+d'%op.a.disp if op.a.disp else ''
    seg  = '%s:'%op.a.seg  if (op.a.seg is not '')  else ''
    b = op.a.base
    if b._is_reg:
        bis = '(%{})'.format(b)
    else:
        assert b._is_eqn
        if b.op.symbol == '*':
            bis = '(,%{},{})'.format(b.l,b.r)
        else:
            bis = '(%{},%{},{})'.format(b.l,b.r.l,b.r.r)
    s = '%s%s%s'%(seg,disp,bis)
    return [(Token.Memory,s)]

def opers_att(i):
    s = []
    for op in reversed(i.operands):
        if op._is_mem:
            s.extend(deref_att(op))
        elif op._is_cst:
            if i.misc['imm_ref'] is not None:
                s.append((Token.Address,str(i.misc['imm_ref'])))
            elif op.sf:
                s.append((Token.Constant,'$%+d'%op.value))
            else:
                s.append((Token.Constant,str(op)))
        elif op._is_reg:
            s.append((Token.Register,'%{}'.format(op)))
        else:
            raise ValueError,op
        s.append((Token.Literal,', '))
    if len(s)>0: s.pop()
    return s

def oprel_att(i):
    to = i.misc['to']
    if to is not None:
        return [(Token.Address,'*'+str(to))]
    if (i.address is not None) and i.operands[0]._is_cst:
        v = i.address + i.operands[0].signextend(32) + i.length
        i.misc['to'] = v
        return [(Token.Address,'*'+str(v))]
    return [(Token.Constant,'$.%+d'%i.operands[0].value)]

# main at&t formats:
format_att_default = (mnemo_att,opers_att)

format_att_ptr = (mnemo_att,opers_att)

format_att_str = (pfx,mnemo_att,opers_att)

format_att_rel = (mnemo_att,oprel_att)

# formats:
IA32_ATT_formats = {
    'ia32_strings' : format_att_str,
    'ia32_mov_adr' : format_att_ptr,
    'ia32_ptr_ib'  : format_att_ptr,
    'ia32_ptr_iwd' : format_att_ptr,
    'ia32_rm8'     : format_att_ptr,
    'ia32_rm32'    : format_att_ptr,
    'ia32_imm_rel' : format_att_rel,
}

IA32_ATT = Formatter(IA32_ATT_formats)
IA32_ATT.default = format_att_default
#
