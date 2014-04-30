from .env64 import *
from .utils import *
from amoco.arch.core import Formatter

def mnemo(i):
    m = i.mnemonic
    if hasattr(i,'setflags') and i.setflags:
        m += 'S'
    if m is 'Bcond': m = 'B.%s'%(i.misc['cond'])
    return '%s'%(m.lower()).ljust(12)

def regs(i,limit=None):
    ops = i.operands
    if limit: ops = ops[:limit]
    return ['{0}'.format(r) for r in ops]

def deref(i,pos=-2):
    assert len(i.operands)>2
    base,offset = i.operands[pos], i.operands[pos+1]
    if offset._is_cst:
        offset.sf = True
        ostr = '%+0d'%offset.value
    else:
        ostr = str(offset)
    if hasattr(i,'wback'):
        wb = '!' if i.wback else ''
        if i.postindex:
            loc = '[%s], %s'%(base, ostr)
        else:
            loc = '[%s, %s]%s'%(base, ostr, wb)
    return [loc]

def label(i,pos=0):
    _pc = i.address
    if _pc is None: _pc=pc
    offset = i.operands[pos]
    return str(_pc+offset)

# -----------------------------------------------------------------------------
# instruction aliases:

def alias_ADD(i):
    m = mnemo(i)
    r = regs(i)
    if not i.setflags:
        if (i.d==0 or i.n==0) and i.operands[-1]==0:
            m = 'mov'
            r.pop()
    elif i.setflags and i.d==0:
        m = 'cmn'
        r.pop(0)
    return m.ljust(12) + ', '.join(r)

def alias_SUB(i):
    m = mnemo(i)
    r = regs(i)
    if not i.setflags:
        if i.n==0:
            m = 'neg'
            r.pop(1)
    elif i.setflags:
        if i.d==0:
            m = 'cmp'
            r.pop(0)
        elif i.n==0:
            m = 'negs'
            r.pop(1)
    return m.ljust(12) + ', '.join(r)

def alias_AND(i):
    m = mnemo(i)
    r = regs(i)
    if i.setflags and i.d==0:
        m = 'tst'
        r.pop(0)
    return m.ljust(12) + ', '.join(r)

def alias_BFM(i):
    m = mnemo(i)
    r = regs(i)
    if i.imms<i.immr:
        r[3] = str(i.immr+1)
        r[2] = str(-i.imms%i.datasize)
        m = 'bfi'
    else:
        r[3] = str(i.imms-i.immr+1)
        m = 'bfxil'
    return m.ljust(12) + ', '.join(r)

def alias_SBFM(i):
    m = mnemo(i)
    r = regs(i)
    if i.imms == i.datasize-1:
        r.pop()
        m = 'asr'
    elif i.imms<i.immr:
        m = 'sbfiz'
        r[3] = str(i.immr+1)
        r[2] = str(-i.imms%i.datasize)
    elif i.immr==0:
        if i.immr==7 : m = 'sxtb'
        if i.immr==15: m = 'sxth'
        if i.immr==31: m = 'sxtw'
        r = r[:2]
    return m.ljust(12) + ', '.join(r)

def alias_UBFM(i):
    m = mnemo(i)
    r = regs(i)
    if i.imms == i.datasize-1:
        r.pop()
        m = 'lsr'
    elif i.imms+1==i.immr:
        m = 'lsl'
        r[2] = str(-i.imms%i.datasize)
        r.pop()
    elif i.imms<i.immr:
        m = 'ubfiz'
        r[3] = str(i.immr+1)
        r[2] = str(-i.imms%i.datasize)
    elif i.immr==0:
        if i.immr==7 : m = 'uxtb'
        if i.immr==15: m = 'uxth'
        if i.immr==31: m = 'uxtw'
        r = r[:2]
    return m.ljust(12) + ', '.join(r)

def alias_CSINC(i):
    m = mnemo(i)
    r = regs(i)
    if (i.n is i.m):
        if (i.cond>>1 != 0b111):
            if i.n!=0:
                m = 'cinc'
                r = r[:2]
            else:
                m = 'cset'
                r = r[:1]
            r.append(CONDITION[i.cond^1][0])
    return m.ljust(12) + ', '.join(r)

def alias_CSINV(i):
    m = mnemo(i)
    r = regs(i)
    if (i.n is i.m):
        if (i.cond>>1 != 0b111):
            if i.n!=0:
                m = 'cinv'
                r = r[:2]
            else:
                m = 'csetm'
                r = r[:1]
            r.append(CONDITION[i.cond^1][0])
    return m.ljust(12) + ', '.join(r)

def alias_CSNEG(i):
    m = mnemo(i)
    r = regs(i)
    if (i.n is i.m):
        if (i.cond>>1 != 0b111):
            m = 'cneg'
            r = r[:2]
            r.append(CONDITION[i.cond^1][0])
    return m.ljust(12) + ', '.join(r)

def alias_EXTR(i):
    m = mnemo(i)
    r = regs(i)
    if (i.n is i.m):
        m = 'ror'
        r.pop(1)
    return m.ljust(12) + ', '.join(r)

def alias_HINT(i):
    m = {0: 'nop',
         5: 'sevl',
         4: 'sev',
         2: 'wfe',
         3: 'wfi',
         1: 'yield'}
    return m.get(i.imm.value,'nop')

def alias_MADD(i):
    m = mnemo(i)
    r = regs(i)
    if i.a==0:
        m = 'mul'
        r.pop()
    return m.ljust(12) + ', '.join(r)

def alias_SMADDL(i):
    m = mnemo(i)
    r = regs(i)
    if i.a==0:
        m = 'smull'
        r.pop()
    return m.ljust(12) + ', '.join(r)

def alias_UMADDL(i):
    m = mnemo(i)
    r = regs(i)
    if i.a==0:
        m = 'umull'
        r.pop()
    return m.ljust(12) + ', '.join(r)

def alias_MSUB(i):
    m = mnemo(i)
    r = regs(i)
    if i.a==0:
        m = 'mneg'
        r.pop()
    return m.ljust(12) + ', '.join(r)

def alias_SMSUBL(i):
    m = mnemo(i)
    r = regs(i)
    if i.a==0:
        m = 'smnegl'
        r.pop()
    return m.ljust(12) + ', '.join(r)

def alias_UMSUBL(i):
    m = mnemo(i)
    r = regs(i)
    if i.a==0:
        m = 'umnegl'
        r.pop()
    return m.ljust(12) + ', '.join(r)

def alias_ORR(i):
    m = mnemo(i)
    r = regs(i)
    if i.n==0:
        m = 'mov'
        r.pop(1)
    return m.ljust(12) + ', '.join(r)

def alias_ORN(i):
    m = mnemo(i)
    r = regs(i)
    if i.n==0:
        m = 'mvn'
        r.pop(1)
    return m.ljust(12) + ', '.join(r)

def alias_SBC(i):
    m = mnemo(i)
    r = regs(i)
    if i.n==0:
        m = m.replace('sbc','ngc')
        r.pop(1)
    return m.ljust(12) + ', '.join(r)

condreg = lambda i: "'%s'"%CONDITION[i.cond][0]

format_allregs = [lambda i: ', '.join(regs(i))]
format_default = [mnemo]+format_allregs
format_ld_st   = [mnemo, lambda i: ', '.join(regs(i,-2)+deref(i,-2))]
format_B       = [mnemo, label]
format_CBx     = [mnemo, lambda i: '%s, %s'%(i.t,label(i,1)) ]
format_CCMx    = [mnemo, lambda i: regs(i,2), lambda i: bin(i.flags.value), condreg]

ARM_V8_full_formats = {
    'A64_generic'       : format_default,
    'A64_load_store'    : format_ld_st,

    'A64_Bcond'         : format_B,
    'A64_B'             : format_B,
    'A64_CBx'           : format_CBx,
    'A64_CCMx'          : format_CCMx,

    'ASRV'              : ['asr ']+format_allregs,
    'LSLV'              : ['lsl ']+format_allregs,
    'LSRV'              : ['lsr ']+format_allregs,
    'RORV'              : ['ror ']+format_allregs,

    'ADD'               : [alias_ADD],
    'SUB'               : [alias_SUB],
    'AND'               : [alias_AND],
    'BFM'               : [alias_BFM],
    'SBFM'              : [alias_SBFM],
    'UBFM'              : [alias_UBFM],
    'CSINC'             : [alias_CSINC],
    'CSINV'             : [alias_CSINV],
    'CSNEG'             : [alias_CSNEG],
    'EXTR'              : [alias_EXTR],
    'HINT'              : [alias_HINT],
    'MADD'              : [alias_MADD],
    'SMADDL'            : [alias_SMADDL],
    'MSUB'              : [alias_MSUB],
    'ORR'               : [alias_ORR],
    'ORN'               : [alias_ORN],
    'SBC'               : [alias_SBC],
}

ARM_V8_full = Formatter(ARM_V8_full_formats)

