# -*- coding: utf-8 -*-

from amoco.cas.expressions import regtype
from amoco.arch.core import Formatter

def pfx(i):
    if i.misc['pfx'] is None: return ''
    pfxgrp0 = i.misc['pfx'][0]
    if pfxgrp0 is None: return ''
    return '%s '%pfxgrp0

def mnemo(i):
    mnemo = i.mnemonic.replace('cc','')
    if hasattr(i,'cond'): mnemo += i.cond[0].split('/')[0]
    return '{: <12}'.format(mnemo.lower())

def deref(op):
    if not op._is_mem: return str(op)
    d = '%+d'%op.a.disp if op.a.disp else ''
    s = {8:'byte ptr ',16:'word ptr ',32:'dword ptr ', 128:'xmmword ptr '}.get(op.size,'')
    s += '%s:'%op.a.seg  if op.a.seg is not '' else ''
    b = op.a.base
    if op.a.base._is_reg and op.a.base.type==regtype.STACK:
        base10 = True
    else:
        base10 = False
    s += '[%s%s]'%(op.a.base,op.a.disp_tostring(base10))
    return s

def opers(i):
    s = []
    for op in i.operands:
        if op._is_mem:
            s.append(deref(op))
            continue
        elif op._is_cst:
            if i.misc['imm_ref'] is not None:
                s.append(str(i.misc['imm_ref']))
                continue
            elif op.sf:
                s.append('%+d'%op.value)
                continue
        # default:
        s.append(str(op))
    return ', '.join(s)

def oprel(i):
    to = i.misc['to']
    if to is not None: return '*'+str(to)
    if (i.address is not None) and i.operands[0]._is_cst:
        v = i.address + i.operands[0].signextend(64) + i.length
        i.misc['to'] = v
        return '*'+str(v)
    return '.%+d'%i.operands[0].value

# main intel formats:
format_intel_default = (mnemo,opers)

format_intel_ptr = (mnemo,opers)

format_intel_str = (pfx,mnemo,opers)

format_intel_rel = (mnemo,oprel)

# formats:
IA32e_Intel_formats = {
    'ia32_strings' : format_intel_str,
    'ia32_mov_adr' : format_intel_ptr,
    'ia32_ptr_ib'  : format_intel_ptr,
    'ia32_ptr_iwd' : format_intel_ptr,
    'ia32_rm8'     : format_intel_ptr,
    'ia32_rm32'    : format_intel_ptr,
    'ia32_imm_rel' : format_intel_rel,
}

IA32e_Intel = Formatter(IA32e_Intel_formats)
IA32e_Intel.default = format_intel_default
