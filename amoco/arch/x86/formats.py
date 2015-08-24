# -*- coding: utf-8 -*-

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
    s = {8:'byte ptr ',16:'word ptr ', 64:'qword ptr ', 128:'xmmword ptr '}.get(op.size,'')
    s += '%s:'%op.a.seg  if (op.a.seg is not '')  else ''
    s += '[%s%s]'%(op.a.base,d)
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
        v = i.address + i.operands[0].signextend(32) + i.length
        i.misc['to'] = v
        return '*'+str(v)
    return '.%+d'%i.operands[0].value

# main intel formats:
format_intel_default = (mnemo,opers)

format_intel_ptr = (mnemo,opers)

format_intel_str = (pfx,mnemo,opers)

format_intel_rel = (mnemo,oprel)

# formats:
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

# highlighted formatter:
#-----------------------
from amoco.ui import render

def IA32_Intel_tokenize(i):
    toks = []
    for f in IA32_Intel.getparts(i):
        if   f is pfx:   toks.append((render.Token.Prefix,f(i)))
        elif f is mnemo: toks.append((render.Token.Mnemonic,f(i)))
        elif f is oprel:
            s = f(i)
            if s.startswith('*'):
                t = render.Token.Address
            else:
                t = render.Token.Constant
            toks.append((t,s))
        elif f is opers:
            for op in i.operands:
                if   op._is_reg: toks.append((render.Token.Register,str(op)))
                elif op._is_mem: toks.append((render.Token.Memory,deref(op)))
                elif op._is_cst:
                    if i.misc['imm_ref'] is not None:
                        toks.append((render.Token.Address,str(i.misc['imm_ref'])))
                    elif op.sf:
                        toks.append((render.Token.Constant,'%+d'%op.value))
                    else:
                        toks.append((render.Token.Constant,str(op)))
                toks.append((render.Token.Literal,', '))
            if toks[-1][0] is render.Token.Literal: toks.pop()
        else:
            toks.append((render.Token.Comment,f(i)))
    return toks

def IA32_Intel_highlighted(null, i):
    return render.highlight(IA32_Intel_tokenize(i))
