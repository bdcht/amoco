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


# Define new formatters, which will generate syntax understandable
# by GNU as and clang assembler.
# They can/should be used for x86 and x64.
# The formatters above are kept for backward compatibility of amoco.
# Note that if env.internals['keep_order'] is True, then the output
# will reflect the order of arguments, e.g. addl (%eax,%ebx), %ecx
# is made distinct of addl (%ebx,%eax), %ecx ; this is coherent with
# the behaviour of most assemblers and disassemblers.

def default_prefix_name(i):
    if i.misc['pfx'] is None: return ''
    pfxgrp0 = i.misc['pfx'][0]
    if pfxgrp0 is None: return ''
    # use the same prefix names as 'as' from binutils
    if pfxgrp0 == 'repne':
        pfxgrp0 = 'repnz'
    if pfxgrp0 == 'rep' and (
            i.mnemonic.startswith('SCAS') or
            i.mnemonic.startswith('CMPS')):
        pfxgrp0 = 'repz'
    return [(Token.Prefix,'%s '%pfxgrp0)]

def default_mnemo_name(i):
    op = i.mnemonic.lower()
    if op in [ 'jcc', 'setcc', 'cmovcc' ]:
        cc = {
          'Z/E':      'e',
          'NZ/NE':    'ne',
          'P/PE':     'p',
          'NP/PO':    'np',
          'NBE/A':    'a',
          'NB/AE/NC': 'ae',
          'B/NAE/C':  'b',
          'BE/NA':    'be',
          'NL/GE':    'ge',
          'NLE/G':    'g',
          'L/NGE':    'l',
          'LE/NG':    'le',
          'S':        's',
          'NS':       'ns',
          'O':        'o',
          'NO':       'no',
          }[i.cond[0]]
        op = op[:-2] + cc
    if op == 'retn': op = 'ret'
    s = [(Token.Mnemonic,op)]
    # Special case: when gcc produces 'rep ret'
    # http://mikedimmick.blogspot.fr/2008/03/what-heck-does-ret-mean.html
    # it usually puts it on two separate lines, and old versions of
    # GNU as don't like a true 'rep ret'
    if op == 'ret' and i.misc.get('pfx') is not None:
        if i.misc['pfx'][0] == 'rep':
            s = [(Token.Prefix,'rep; ')] + s
    return s

def reg_name(r):
    assert r._is_reg
    if r.ref[0] == 'r' and r.ref[-1] == 'l':
        # gcc or clang use 'r8b' instead of 'R8L' from Intel specs
        return r.ref[:-1]+'b'
    return r.ref

def op_includes_reg(op):
    if op is None: return False
    if op._is_cst: return False
    if op._is_lab: return False
    if op._is_reg: return True
    if op._is_eqn: return op_includes_reg(op.l) or op_includes_reg(op.r)
    if op._is_mem: return op_includes_reg(op.a.base)
    NEVER

def default_eqn_parser(op):
    # amoco has a sophisticated behaviour wrt expression simplification
    # e.g. the lexicographic order of labels is used to generate (-L0)+L1
    # instead of L1-L0
    # we need a sophisticate pattern matching
    if op._is_cst:
        return None, None, op.value
    elif op._is_lab:
        return op.ref, None, 0
    elif op._is_reg:
        return None, None, 0
    elif        op.op.symbol == '+' \
            and op.l._is_lab \
            and op.r._is_lab:
        if str(op.r.ref) == '_GLOBAL_OFFSET_TABLE_' and \
           str(op.l.ref).startswith('[.-.'):
            # GNU as 2.15 likes _GLOBAL_OFFSET_TABLE_+[.-.L10]
            # which is generated by gcc 3.x, but
            # fails on [.-.L10]+_GLOBAL_OFFSET_TABLE_
            # by computing an erroneous addend
            return '%s+%s'%(op.r.ref,op.l.ref), None, 0
        else:
            NON_REGRESSION_FOUND
            return '%s+%s'%(op.l.ref,op.r.ref), None, 0
    elif        op.op.symbol == '+' \
            and op.l._is_lab \
            and op.r._is_cst:
        # L+cte
        return op.l.ref, None, op.r.value
    elif        op.op.symbol == '-' \
            and op.l._is_lab \
            and op.r._is_cst:
        # L-cte
        return op.l.ref, None, -op.r.value
    elif        op.op.symbol == '-' \
            and op.l._is_lab \
            and op.r._is_lab:
        # L1-L0
        return op.l.ref, op.r.ref, 0
    elif        op.op.symbol == '+' \
            and op.r._is_lab \
            and op.l._is_eqn \
            and op.l.op.symbol == '-' \
            and op.l.l is None \
            and op.l.r._is_lab:
        # L0-L1
        return op.r.ref, op.l.r.ref, 0
    elif        op.op.symbol == '+' \
            and op.r._is_cst \
            and op.l._is_eqn \
            and op.l.op.symbol == '-' \
            and op.l.r._is_lab \
            and op.l.l._is_lab:
        # L1-L0+cte
        return op.l.l.ref, op.l.r.ref, op.r.value
    elif        op.op.symbol == '-' \
            and op.r._is_cst \
            and op.l._is_eqn \
            and op.l.op.symbol == '-' \
            and op.l.r._is_lab \
            and op.l.l._is_lab:
        # L1-L0-cte
        return op.l.r.ref, op.l.l.ref, -op.r.value
    elif        op.op.symbol == '+' \
            and op.r._is_cst \
            and op.l._is_eqn \
            and op.l.op.symbol == '+' \
            and op.l.r._is_lab \
            and op.l.l._is_eqn \
            and op.l.l.op.symbol == '-' \
            and op.l.l.l is None \
            and op.l.l.r._is_lab:
        # L0-L1+cte
        return op.l.r.ref, op.l.l.r.ref, op.r.value
    elif        op.op.symbol == '-' \
            and op.r._is_cst \
            and op.l._is_eqn \
            and op.l.op.symbol == '+' \
            and op.l.r._is_lab \
            and op.l.l._is_eqn \
            and op.l.l.op.symbol == '-' \
            and op.l.l.l is None \
            and op.l.l.r._is_lab:
        # L0-L1-cte
        return op.l.r.ref, op.l.l.r.ref, -op.r.value
    elif        op.op.symbol == '*':
        return None, None, 0
    elif        op.op.symbol == '+' \
            and (op.l._is_reg or op.r._is_reg):
        return None, None, 0
    print("FAILED %s %s %s"%(op.l,op.op.symbol,op.r))

def default_deref(b, d):
    if not op_includes_reg(b):
        # Base does not include a register
        b += d
        if b._is_lab:
            return str(b.ref), None, None
        if b._is_cst:
            return '%d'%b, None, None
        if b._is_eqn and b.op.symbol == '+':
            return '%s%+d'%(b.l.ref, b.r), None, None
    else:
        # Base includes a register; disp may include labels
        if b._is_reg:
            b0, b1, b2 = reg_name(b), None, None
        elif b._is_eqn:
            if b.op.symbol == '*':
                b0, b1, b2 = None, reg_name(b.l), int(b.r)
            elif b.op.symbol == '+' and b.l._is_reg and b.r._is_reg:
                b0, b1, b2 = reg_name(b.l), reg_name(b.r), None
                if b1 in ('esp','rsp'): b0, b1 = b1, b0 # esp is always first
            elif b.op.symbol == '+' and b.r._is_eqn and b.r.op.symbol == '*':
                b0, b1, b2 = reg_name(b.l), reg_name(b.r.l), int(b.r.r)
            elif b.op.symbol == '+' and b.l._is_eqn and b.l.op.symbol == '*':
                b0, b1, b2 = reg_name(b.r), reg_name(b.l.l), int(b.l.r)
            else:
                NEVER
        if not hasattr(d, '_is_cst'):
            # displacement is an integer
            d0, d1 = '', int(d)
        elif d._is_lab or d._is_eqn:
            label, label_dif, d1 = default_eqn_parser(d)
            if label_dif is None: d0 = str(label)
            else:                 d0 = '%s-%s' % (label, label_dif)
        else:
            NEVER
        return None, (b0, b1, b2), (d0, d1)

def default_opers_address(op):
    label, label_dif, cste = default_eqn_parser(op)
    if cste is 0 and label_dif is None:
        return str(label)
    elif cste is 0:
        return '%s-%s'%(label,label_dif)
    elif label_dif is None:
        return '%s%+d'%(label,cste)
    else:
        return '%s-%s%+d'%(label,label_dif,cste)

def default_opers_reg(op, i, s):
    op = reg_name(op)
    if op.startswith('st'):
        op = 'st(%s)'%op[2]
    # gcc generates %st(0) only when it is a variable parameter
    # when it is twice st(0), let us keep only the second
    # Note that we cannot make the difference between D8C0 and DCC0
    if len(i.operands) == 2 and op == 'st(0)' and \
        (len(s) == 2 or str(i.operands[0]) != 'st0'):
        op = 'st'
    return op

def intel_mnemo(i):
    s = default_mnemo_name(i)
    s[-1] = (Token.Mnemonic, '{: <9} '.format(s[-1][1]))
    return s

def intel_deref(op):
    assert op._is_mem
    b = op.a.base
    d = op.a.disp
    seg = op.a.seg
    if b._is_reg and b.ref == 'rip': seg = '' # Don't display segment
    s, b, d = default_deref(b, d)
    if s is None:
        # Base includes a register; disp may include labels
        (b0, b1, b2), (d0, d1) = b, d
        if b2 is not None: b1 = '%s*%s' % (b1, b2)
        if   b0 is None: b = b1
        elif b1 is None: b = b0
        else:            b = '%s+%s' % (b0, b1)
        if   b0 is None: s = '%s[%d+%s]' % (d0, d1, b)
        elif d1 == 0:    s = '%s[%s]'    % (d0, b)
        else:            s = '%s[%s%+d]' % (d0, b, d1)
    if seg is not '':
        s = '%s:%s' % (seg, s)
    return s

def intel_opers(i):
    s = []
    for op in i.operands:
        if op._is_mem:
            pfx = {
                8:  'BYTE PTR ',
                16: 'WORD PTR ',
                32: 'DWORD PTR ',
                64: 'QWORD PTR ',
                80: 'TBYTE PTR ',
                128:'XMMWORD PTR ',
                }.get(op.size,'')
            op = intel_deref(op)
            if i.mnemonic != 'LEA': op = pfx + op
            if i.mnemonic in ('CALL','JMP'): op = '[%s]' % op
            s.append((Token.Memory,op))
        elif op._is_cst:
            if i.misc['imm_ref'] is not None:
                s.append((Token.Address,str(i.misc['imm_ref'])))
            elif op.sf:
                s.append((Token.Constant,'%+d'%op.value))
            else:
                v = op.value
                if i.mnemonic in ('ADD','AND','XOR','OR','CMP','TEST','MOV','IMUL'):
                    # values are modulo 2^op.size, usually values close
                    # to 2^32 are displayed as negative values
                    if v > (1<<(op.size-1)): v -= (1<<op.size)
                s.append((Token.Constant,'%d'%v))
        elif op._is_lab or op._is_eqn:
            s.append((Token.Address,'OFFSET FLAT:'+default_opers_address(op)))
        elif op._is_reg:
            s.append((Token.Register,default_opers_reg(op, i, s)))
        else:
            import sys
            sys.stderr.write("TODO %s %s\n"%(op.__class__,op))
        s.append((Token.Literal,', '))
    if len(s)>0: s.pop()
    return s

def intel_oprel(i):
    to = i.misc['to']
    if to is not None:
        return [(Token.Address,str(to))]
    op = i.operands[0]
    if op._is_lab:
        return [(Token.Address,str(op.ref))]
    if op._is_eqn and op.op.symbol == '+' \
        and op.l._is_lab:
        return [(Token.Address,'%s%+d'%(op.l.ref,op.r))]
    return [(Token.Constant,'{%s}'%op)]

# Intel syntax, as used in GNU binutils
intel_format_default = (                    intel_mnemo,intel_opers)
intel_format_str     = (default_prefix_name,intel_mnemo,intel_opers)
intel_format_rel     = (                    intel_mnemo,intel_oprel)
IA32_Binutils_Intel_formats = {
    'ia32_strings' : intel_format_str,
    'ia32_imm_rel' : intel_format_rel,
}
IA32_Binutils_Intel = Formatter(IA32_Binutils_Intel_formats)
IA32_Binutils_Intel.default = intel_format_default

# Intel syntax, as used by clang on MacOSX
"""
    Note that the version 700.1.81 of clang cannot use Intel syntax.
    With -masm=intel it can generate Intel asm, but forgots
    the directive .intel_syntax noprefix
    If you add the directive, then it does not understand
    the syntax it generates for LOCSDIF relocations, and
    these Mach-O relocations are needed everywhere.
"""
IA32_MacOSX_Intel = None


att_mnemo_float_optional_suffix = [
    'fld', 'fst', 'fstp',
    'faddp','fsubp','fmulp','fdivp','fsubrp','fdivrp',
    'fadd', 'fsub', 'fmul', 'fdiv', 'fsubr', 'fdivr', 'fcom', 'fcomp',
]
att_mnemo_suffix_one_iflt = [
    'fiadd', 'fisub', 'fisubr', 'fimul', 'fidiv', 'fidivr',
    'ficom', 'ficomp', 'fild', 'fist', 'fistp', 'fisttp',
]
att_mnemo_suffix_one_ptr = [
    'lea', 'mov', 'xchg', 'push', 'pop',
    'test', 'cmp', 'and', 'xor', 'or', 'not', 'neg',
    'add', 'adc', 'sub', 'mul', 'div', 'imul', 'idiv', 'inc', 'dec', 'xadd',
    'sal', 'sar', 'shl', 'shr', 'rol', 'ror', 'sbb', 'shld', 'shrd',
    'bsf', 'bsr',
    'bt', 'bts', 'btr', 'btc', 'lgdt',
    'cvtsi2sd', 'cvtsi2ss', 'cvttsd2si', 'fisttp',
]
att_mnemo_correspondance = {
    # 'movsl': 'movsd', # there is a SSE movsd and a string movsd
    'cmpsl': 'cmpsd',
    'stosl': 'stosd',
    'lodsl': 'lodsd',
    'scasl': 'scasd',
    'pushf': 'pushfd',
    'pushfl':'pushfd',
    'popf':  'popfd',
    'popfl': 'popfd',
    'ljmp':  'jmpf',
    # sign extend
    'cbtw': 'cbw',
    'cwtl': 'cwde',
    'cwtd': 'cwd',
    'cltd': 'cdq',
    'cltq': 'cdqe', # x86-64 only
    'cqto': 'cqo',  # x86-64 only
}
mnemo_string_rep = ('ins','movs','outs','lods','stos','cmps','scas')
mnemo_sse_cmp = [ 'cmpps', 'cmppd', 'cmpsd', 'cmpss' ]
mnemo_sse_cmp_predicate = ['eq','lt','le','unord','neq','nlt','nle','ord']
def att_mnemo_generic(i,s,m):
    if i.mnemonic in [ 'SETcc', 'Jcc' ]:
        pass
    elif m == 'movsd' and len(i.operands) < 2:
        # This 'movsd' is the string instruction
        # The 'movsd' with two arguments is the SSE instruction
        m = 'movsl'
    elif m in mnemo_sse_cmp and len(i.operands) == 3:
        m = m[0:3] + mnemo_sse_cmp_predicate[int(i.operands[2])] + m[3:5]
    elif m in att_mnemo_correspondance.values():
        m = sorted([key
            for key, value in att_mnemo_correspondance.items()
            if m == value ])[0]
    elif m in att_mnemo_suffix_one_ptr:
        if m == 'push' and (i.operands[0]._is_cst
                         or i.operands[0]._is_eqn
                         or i.operands[0]._is_lab
                         or i.operands[0]._is_reg):
            if i.misc.get('opdsz',None) == 16:  m += 'w'
            elif i.operands[0].size == 64:      m += 'q'
            elif 'REX' in i.misc:               m += 'q'
            else:                               m += 'l'
        elif m in [ 'cvtsi2ss', 'cvtsi2sd', ]:
            if i.operands[1]._is_mem:
                m += {32:'l', 64:'q'}[i.operands[1].size]
        else:
            m += {8:'b', 16:'w', 32:'l', 64:'q'}[i.operands[0].size]
    elif m in att_mnemo_float_optional_suffix:
        if len(i.operands) == 1 and not i.operands[0]._is_reg:
            m += {32:'s', 64:'l', 80:'t'}[i.operands[0].size]
    elif m in att_mnemo_suffix_one_iflt:
        m += {16:'s', 32:'l', 64:'q'}[i.operands[0].size]
    elif m in [
        'movsx', 'movzx', 'movsxd',
        ]:
        m = {
            ( 8,16):m[:4]+'bw',
            ( 8,32):m[:4]+'bl',
            ( 8,64):m[:4]+'bq',
            (16,32):m[:4]+'wl',
            (16,64):m[:4]+'wq',
            (32,64):m[:4]+'lq',
            }[(i.misc['opdsz'] or 32,i.operands[0].size)]
    else:
        pass
        # m+=':%s:%s:%s: '%(i.misc['opdsz'],i.operands[0].size,len(i.operands))
    s[-1] = (Token.Mnemonic, '{: <9} '.format(m))
    return s

def att_mnemo_binutils(i):
    s = default_mnemo_name(i)
    m = s[-1][1]
    if m.startswith('fsub') or m.startswith('fdiv'):
        # https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=372528
        if m[-1] == 'p':
            if   m[4:] == 'p':  m = m[:4]+'rp'
            elif m[4:] == 'rp': m = m[:4]+'p'
            else: NEVER
        elif len(i.operands) == 2 and str(i.operands[0]) != 'st0':
            if   m[4:] == '':   m = m+'r'
            elif m[4:] == 'r':  m = m[:4]
            else: NEVER
    return att_mnemo_generic(i,s,m)

def att_mnemo_macosx(i):
    s = default_mnemo_name(i)
    m = s[-1][1]
    if m == 'sal': m = 'shl' # clang assembler does not understand 'sal'
    if m.startswith('fsub') or m.startswith('fdiv'):
        # same as binutils
        if m[-1] == 'p':
            if   m[4:] == 'p':  m = m[:4]+'rp'
            elif m[4:] == 'rp': m = m[:4]+'p'
            else: NEVER
        elif len(i.operands) == 2 and str(i.operands[0]) != 'st0':
            if   m[4:] == '':   m = m+'r'
            elif m[4:] == 'r':  m = m[:4]
            else: NEVER
    return att_mnemo_generic(i,s,m)

def att_deref(op):
    assert op._is_mem
    b = op.a.base
    d = op.a.disp
    seg = op.a.seg
    s, b, d = default_deref(b, d)
    if s is None:
        # Base includes a register; disp may include labels
        (b0, b1, b2), (d0, d1) = b, d
        if b0 == 'rip': seg = '' # Don't display segment
        if   b1 is None: b = '(%{})'.format(b0)
        elif b0 is None: b = '(,%{},{})'.format(b1,b2)
        elif b2 is None: b = '(%{},%{})'.format(b0,b1)
        else: b = '(%{},%{},{})'.format(b0,b1,b2)
        if d0 is '':  d = '%d' % d1
        elif d1 is 0: d = d0
        else:         d = '%s%+d' % (d0, d1)
        if b0 is None: s = d + b
        elif d == '0': s = b
        else:          s = d + b
    if seg is not '':
        s = '%{}:{}'.format(seg,s)
    return s

def att_opers_macosx(i):
    if i.mnemonic == 'TEST':
        # clang sometimes uses Intel argument order for 'test'
        # verified for Apple LLVM version 7.0.2 (clang-700.1.81)
        if i.operands[1]._is_slc or \
          (i.operands[1]._is_reg and not i.operands[1]._is_lab):
            return att_opers(i, operands=i.operands)
    return att_opers(i)

def att_opers(i, operands=None):
    s = []
    if operands is None:
        operands = reversed(i.operands)
    for op in operands:
        if op._is_mem:
            op = att_deref(op)
            if i.mnemonic in ('CALL','JMP'): op = '*'+op
            s.append((Token.Memory,op))
        elif op._is_cst:
            if i.misc['imm_ref'] is not None:
                s.append((Token.Address,str(i.misc['imm_ref'])))
            else:
                v = op.value
                if v > (1<<(op.size-1)): v -= (1<<op.size)
                s.append((Token.Constant,'$%d'%v))
        elif op._is_lab or op._is_eqn:
            s.append((Token.Address,'$'+default_opers_address(op)))
        elif op._is_reg:
            op = '%'+default_opers_reg(op, i, s)
            if i.mnemonic in ['CALL','JMP']: op = '*'+op
            s.append((Token.Register,op))
        else:
            import sys
            sys.stderr.write("TODO %s %s\n"%(op.__class__,op))
        s.append((Token.Literal,', '))
    if i.mnemonic.lower() in mnemo_sse_cmp and len(i.operands) == 3:
        s = s[2:]
    if len(s)>0: s.pop()
    return s

def att_oprel(i):
    to = i.misc['to']
    if to is not None:
        return [(Token.Address,'*'+str(to))]
    op = i.operands[0]
    if op._is_lab:
        return [(Token.Address,str(op.ref))]
    if op._is_eqn and op.op.symbol == '+' \
        and op.l._is_lab:
        return [(Token.Address,'%s%+d'%(op.l.ref,op.r))]
    if op._is_eqn and op.op.symbol == '+' \
        and op.l._is_eqn and op.l.op.symbol == '+' \
        and op.l.l._is_lab and op.l.r._is_reg and op.l.r.ref == 'rip':
        return [(Token.Address,'%s%+d(%%rip)'%(op.l.l.ref,op.r))]
    return [(Token.Constant,'{%s}'%op)]

# AT&T syntax, as used in GNU binutils
att_format_default = (                    att_mnemo_binutils,att_opers)
att_format_str     = (default_prefix_name,att_mnemo_binutils,att_opers)
att_format_rel     = (                    att_mnemo_binutils,att_oprel)
IA32_Binutils_ATT_formats = {
    'ia32_strings' : att_format_str,
    'ia32_imm_rel' : att_format_rel,
}
IA32_Binutils_ATT = Formatter(IA32_Binutils_ATT_formats)
IA32_Binutils_ATT.default = att_format_default

# AT&T syntax, as used by clang on MacOSX
attm_format_default = (                    att_mnemo_macosx,att_opers_macosx)
attm_format_str     = (default_prefix_name,att_mnemo_macosx,att_opers)
attm_format_rel     = (                    att_mnemo_macosx,att_oprel)
IA32_MacOSX_ATT_formats = {
    'ia32_strings' : attm_format_str,
    'ia32_imm_rel' : attm_format_rel,
}
IA32_MacOSX_ATT = Formatter(IA32_MacOSX_ATT_formats)
IA32_MacOSX_ATT.default = attm_format_default
