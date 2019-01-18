# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2018 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *
from .utils import *

from amoco.cas.utils import *

def __mem(a,sz):
    return mem(a,sz,endian=-1)

#------------------------------------------------------------------------------
# helpers and decorators :
def _push_(fmap,_x):
  fmap[sp] = fmap[sp]-_x.length
  fmap[__mem(sp,_x.size)] = _x

def _pop_(fmap,_l):
  fmap[_l] = fmap(__mem(sp,_l.size))
  fmap[sp] = fmap[sp]+_l.length

def __pc(i_xxx):
    def pcnpc(ins,fmap):
        fmap[pc]  = fmap(pc)+ins.length
        i_xxx(ins,fmap)
    return pcnpc

def predecr(ins,fmap):
    if ins.misc['decr']:
        for i in ins.misc['decr']:
            r = ins.operands[i].a.base
            fmap[r] = fmap(r-4)

def postincr(ins,fmap):
    if ins.misc['incr']:
        for i in ins.misc['incr']:
            r = ins.operands[i].a.base
            fmap[r] = fmap(r+4)

# i_xxx is the translation of SH2-A instruction xxx.
#------------------------------------------------------------------------------

@__pc
def i_MOV(ins,fmap):
    src,dst = ins.operands
    predecr(ins,fmap)
    x = fmap(src)
    if dst.size>src.size:
        x = x.signextend(dst.size)
    elif dst.size<src.size:
        x = x[0:dst.size]
    fmap[dst] = x
    postincr(ins,fmap)

i_MOVA = i_MOV
i_MOVI20 = i_MOVI20S = i_MOV

@__pc
def i_MOVML(ins,fmap):
    src,dst = ins.operands
    if ins.misc['incr']:
        assert ins.misc['incr'][0]==0
        assert src._is_mem
        assert src.a.base == R15
        assert dst._is_reg
        for r in R[:obj.m]:
            if r is sp: r = PR
            fmap[r] = fmap(src)
            fmap[R15] = fmap(R15)+4
    if ins.misc['decr']:
        assert ins.misc['decr'][0]==1
        assert src._is_reg
        assert dst._is_mem
        assert dst.a.base == R15
        for r in R[obj.m::-1]:
            if r is sp: r = PR
            fmap[R15] = fmap(R15)-4
            fmap[dst] = fmap(r)

@__pc
def i_MOVMU(ins,fmap):
    src,dst = ins.operands
    if ins.misc['incr']:
        assert ins.misc['incr'][0]==0
        assert src._is_mem
        assert src.a.base == R15
        assert dst._is_reg
        for r in R[obj.m:]:
            if r is sp: r = PR
            fmap[r] = fmap(src)
            fmap[R15] = fmap(R15)+4
    if ins.misc['decr']:
        assert ins.misc['decr'][0]==1
        assert src._is_reg
        assert dst._is_mem
        assert dst.a.base == R15
        for r in R[obj.m:][::-1]:
            if r is sp: r = PR
            fmap[R15] = fmap(R15)-4
            fmap[dst] = fmap(r)

@__pc
def i_MOVRT(ins,fmap):
    dst = ins.operands[0]
    fmap[dst] = fmap(~T).zeroextend(dst.size)

@__pc
def i_MOVT(ins,fmap):
    dst = ins.operands[0]
    fmap[dst] = fmap(T).zeroextend(dst.size)

@__pc
def i_MOVU(ins,fmap):
    src,dst = ins.operands
    fmap[dst] = fmap(src).zeroextend(dst.size)

@__pc
def i_NOTT(ins,fmap):
    fmap[T] = fmap(~T)

@__pc
def i_CLRMAC(ins,fmap):
    fmap[MACH] = cst(0,32)
    fmap[MACL] = cst(0,32)

@__pc
def i_CLRT(ins,fmap):
    fmap[T] = bit0

@__pc
def i_SETT(ins,fmap):
    fmap[T] = bit1

@__pc
def i_LDBANK(ins,fmap):
    src,dst = ins.operands
    fmap[dst] = fmap(src)

@__pc
def i_PREF(ins,fmap):
    pass

@__pc
def i_NOP(ins,fmap):
    pass

@__pc
def i_SWAP(ins,fmap):
    src,dst = ins.operands
    sz = ins.misc['sz']
    if sz==0:
        b0,b1 = src[0:8],src[8:16]
        fmap[dst] = fmap(composer(b1,b0,src[16:32]))
    if sz==1:
        w0,w1 = src[0:16],src[16:32]
        fmap[dst] = fmap(composer(w1,w0))

@__pc
def i_XTRCT(ins,fmap):
    src,dst = ins.operands
    p1 = dst[16:32]
    p2 = src[0:16]
    fmap[dst] = fmap(composer(p1,p2))

@__pc
def i_ADD(ins,fmap):
    src,dst = ins.operands
    _s1 = fmap(dst)
    _s2 = fmap(src)
    fmap[dst] = _s1+_s2

@__pc
def i_ADDC(ins,fmap):
    src,dst = ins.operands
    _s1 = fmap(dst)
    _s2 = fmap(src)
    _r,carry,overflow = AddWithCarry(_s1,_s2,fmap(T))
    fmap[T] = carry
    fmap[dst] = _r

@__pc
def i_ADDV(ins,fmap):
    src,dst = ins.operands
    _s1 = fmap(dst)
    _s2 = fmap(src)
    _r,carry,overflow = AddWithCarry(_s1,_s2)
    fmap[T] = overflow
    fmap[dst] = _r

@__pc
def i_SUB(ins,fmap):
    src,dst = ins.operands
    _s1 = fmap(dst)
    _s2 = fmap(src)
    fmap[dst] = _s1+_s2

@__pc
def i_SUBC(ins,fmap):
    src,dst = ins.operands
    _s1 = fmap(dst)
    _s2 = fmap(src)
    _r,carry,overflow = SubWithBorrow(_s1,_s2,fmap(T))
    fmap[T] = carry
    fmap[dst] = _r

@__pc
def i_SUBV(ins,fmap):
    src,dst = ins.operands
    _s1 = fmap(dst)
    _s2 = fmap(src)
    _r,carry,overflow = SubWithBorrow(_s1,_s2)
    fmap[T] = overflow
    fmap[dst] = _r

@__pc
def i_AND(ins,fmap):
    src,dst = ins.operands
    fmap[dst] = fmap(dst & src)

@__pc
def i_NOT(ins,fmap):
    src,dst = ins.operands
    fmap[dst] = fmap(~src)

@__pc
def i_OR(ins,fmap):
    src,dst = ins.operands
    fmap[dst] = fmap(dst | src)

@__pc
def i_XOR(ins,fmap):
    src,dst = ins.operands
    fmap[dst] = fmap(dst ^ src)

@__pc
def i_CMP(ins,fmap):
    # implementation of CMP/STR in Renesas REJ09B0051-0300 Rev.3.00 08/2005
    # is not consistent with the description of CMP/STR "if a byte in Rn equals
    # a byte in Rm then T=1".
    # Here we have implemented strictly the bytes comparisons.
    # In Renesas pseudo-code, the case where Rn^Rm = 0x08040201 leads to T=1.
    # TODO: check the real implementation on a SH2-A CPU...
    cmpstr = lambda n,m: (n[0:8]  ==m[0:8]  )|\
                         (n[8:16] ==m[8:16] )|\
                         (n[16:24]==m[16:24])|\
                         (n[24:32]==m[24:32])
    if ins.cond in ('PL','PZ'):
        rm,rn = cst(0,32),ins.operands[0]
    elif ins.cond=='HI':
        rn,rm = ins.operands
    else:
        rm,rn = ins.operands
    op_ = {'PL': operator.gt,
           'PZ': operator.ge,
           'EQ': operator.eq,
           'HS': geu,
           'GE': operator.ge,
           'HI': ltu,
           'GT': operator.gt,
           'STR': cmpstr}[ins.cond]
    t = fmap(op_(rn,rm))
    fmap[T] = tst(t,bit1,bit0)

@__pc
def i_TST(ins,fmap):
    Rm,Rn = ins.operands
    t_ = fmap((Rn&Rm)==cst(0,32))
    fmap[T] = tst(t_,bit1,bit0)

@__pc
def i_TAS(ins,fmap):
    src = ins.operands[0]
    t_ = fmap(src==cst(0,32))
    fmap[T] = tst(t_,bit1,bit0)
    fmap[src] = fmap(src)|cst(0x80,32)

@__pc
def i_CLIPS(ins,fmap):
    Rn = ins.operands[0]
    if ins.size==8:
        ul = cst(+127,32)
        ll = cst(-128,32)
    elif ins.size==16:
        ul = cst(+32767,32)
        ll = cst(-32768,32)
    fmap[Rn] = fmap(tst(Rn>ul, ul, Rn))
    fmap[CS] = fmap(tst(Rn>ul, bit1, CS))

@__pc
def i_CLIPU(ins,fmap):
    Rn = ins.operands[0]
    if ins.size==8:
        ul = cst(0xFF,32)
    elif ins.size==16:
        ul = cst(0xFFFF,32)
    fmap[Rn] = fmap(tst(Rn>ul, ul, Rn))
    fmap[CS] = fmap(tst(Rn>ul, bit1, CS))

@__pc
def i_DIV1(ins,fmap):
    Rm,Rn = ins.operands
    oldq = fmap(Q)
    q = fmap((cst(0x80000000,32)&Rn) != bit0)
    rn = fmap(Rn<<1)
    rn |= fmap(T.zeroextend(32))
    # case oldq 0, M 0:
    tmp0 = rn
    rn_00 = rn-fmap(Rm)
    tmp1 = rn_00>tmp0
    newq0_0 = tst(q, tmp1==bit0, tmp1)
    # case oldq0, M 1:
    tmp0 = rn
    rn_01 = rn+fmap(Rm)
    tmp1 = rn_01<tmp0
    newq0_1 = tst(q, tmp1, tmp1==bit0)
    rn0 = tst(fmap(M),rn_01,rn_00)
    newq0 = tst(fmap(M),newq0_1,newq0_0)
    # case oldq 1, M 0:
    tmp0 = rn
    rn_10 = rn+fmap(Rm)
    tmp1 = rn_10<tmp0
    newq1_0 = tst(q, tmp1==bit0, tmp1)
    # case oldq 1, M 1:
    tmp0 = rn
    rn_11 = rn-fmap(Rm)
    tmp1 = rn_11>tmp0
    newq1_1 = tst(q, tmp1, tmp1=bit0)
    rn1 = tst(fmap(M),rn_11,rn_10)
    newq1 = tst(fmap(M),newq1_1,newq1_0)
    # div1 step result:
    fmap[Rn] = tst(oldq,rn1,rn0)
    fmap[Q] = tst(oldq,newq0,newq1)
    fmap[T] = fmap(Q==M)

@__pc
def i_DIV0S(ins,fmap):
    Rm,Rn = ins.operands
    fmap[Q] = fmap(tst((Rn&cst(0x80000000,32))==cst(0,32),bit1,bit0))
    fmap[M] = fmap(tst((Rm&cst(0x80000000,32))==cst(0,32),bit1,bit0))
    fmap[T] = ~(fmap(Q==M))

@__pc
def i_DIV0U(ins,fmap):
    fmap[M] = bit0
    fmap[Q] = bit0
    fmap[T] = bit0

@__pc
def i_DIVS(ins,fmap):
    Rm,Rn = ins.operands
    r1 = fmap(Rm).signed()
    r2 = fmap(Rn).signed()
    fmap[Rn] = (r2/r1)

@__pc
def i_DIVU(ins,fmap):
    Rm,Rn = ins.operands
    r1 = fmap(Rm).unsigned()
    r2 = fmap(Rn).unsigned()
    fmap[Rn] = r2/r1

@__pc
def i_DMULS(ins,fmap):
    Rm,Rn = ins.operands
    r1 = fmap(Rm).signed()
    r2 = fmap(Rn).signed()
    x = fmap(r1**r2)
    fmap[MACL] = x[0:32]
    fmap[MACH] = x[32:64]

@__pc
def i_DMULU(ins,fmap):
    Rm,Rn = ins.operands
    r1 = fmap(Rm).unsigned()
    r2 = fmap(Rn).unsigned()
    x = fmap(r1**r2)
    fmap[MACL] = x[0:32]
    fmap[MACH] = x[32:64]

@__pc
def i_DT(ins,fmap):
    Rn = ins.operands[0]
    fmap[Rn] = fmap(Rn-1)
    fmap[T] = fmap(Rn==0,bit1,bit0)

@__pc
def i_EXTS(ins,fmap):
    Rm,Rn = ins.operands
    fmap[Rn] = fmap(Rm[0:ins.size]).signextend(32)

@__pc
def i_EXTU(ins,fmap):
    Rm,Rn = ins.operands
    fmap[Rn] = fmap(Rm[0:ins.size]).zeroextend(32)

@__pc
def i_MAC(ins,fmap):
    m,n = ins.operands
    res = fmap(m**n)+fmap(composer([MACL,MACH]))
    fmap[MACL] = res[0:32]
    fmap[MACH] = res[0:32]
    postincr(ins,fmap)

@__pc
def i_NEG(ins,fmap):
    Rm,Rn = ins.operands
    fmap[Rn] = fmap(-Rm)

@__pc
def i_NEGC(ins,fmap):
    Rm,Rn = ins.operands
    _r,carry,overflow = SubWithBorrow(cst(0,Rm.size),fmap(Rm),fmap(T))
    fmap[Rn] = _r
    fmap[T] = carry

@__pc
def i_MUL(ins,fmap):
    Rm,Rn = ins.operands
    fmap[MACL] = fmap(Rm*Rn)

@__pc
def i_MULR(ins,fmap):
    R0,Rn = ins.operands
    fmap[Rn] = fmap(R0*Rn)

@__pc
def i_MULS(ins,fmap):
    Rm,Rn = ins.operands
    s1,s2 = fmap(Rm).signed(),fmap(Rn).signed()
    fmap[MACL] = fmap(s1*s2)

@__pc
def i_MULU(ins,fmap):
    Rm,Rn = ins.operands
    s1,s2 = fmap(Rm).unsigned(),fmap(Rn).unsigned()
    fmap[MACL] = fmap(s1*s2)

@__pc
def i_ROTL(ins,fmap):
    Rn = ins.operands[0]
    fmap[T] = fmap(Rn[31:32])
    fmap[Rn] = fmap(rol(Rn,1))

@__pc
def i_ROTR(ins,fmap):
    Rn = ins.operands[0]
    fmap[T] = fmap(Rn[0:1])
    fmap[Rn] = fmap(ror(Rn,1))

@__pc
def i_ROTCL(ins,fmap):
    Rn = ins.operands[0]
    t = fmap(T)
    fmap[T] = fmap(Rn[31:32])
    fmap[Rn] = composer([t,fmap(Rn[0:31])])

@__pc
def i_ROTCR(ins,fmap):
    Rn = ins.operands[0]
    t = fmap(T)
    fmap[T] = fmap(Rn[0:1])
    fmap[Rn] = composer([fmap(Rn[1:32]),t])

@__pc
def i_SHAD(ins,fmap):
    Rm,Rn = ins.operands
    sgn = Rm[31:32]
    s_p = Rm[0:5]
    s_n = (~s_p)+1
    fmap[Rn] = fmap(sgn,Rn<<s_p,op(OP_ASR,Rn,s_n))

@__pc
def i_SHAL(ins,fmap):
    Rn = ins.operands[0]
    fmap[T]  = fmap(Rn[31:32])
    fmap[Rn] = fmap(Rn<<1)

@__pc
def i_SHAR(ins,fmap):
    Rn = ins.operands[0]
    fmap[T]  = fmap(Rn[0:1])
    fmap[Rn] = fmap(op(OP_ASR,Rn,1))

@__pc
def i_SHLD(ins,fmap):
    Rm,Rn = ins.operands
    sgn = Rm[31:32]
    s_p = Rm[0:5]
    s_n = (~s_p)+1
    fmap[Rn] = fmap(sgn,Rn<<s_p,Rn>>s_n)

@__pc
def i_SHLL(ins,fmap):
    Rn = ins.operands[0]
    fmap[T]  = fmap(Rn[31:32])
    fmap[Rn] = fmap(Rn<<1)

@__pc
def i_SHLR(ins,fmap):
    Rn = ins.operands[0]
    fmap[T]  = fmap(Rn[0:1])
    fmap[Rn] = fmap(Rn>>1)

@__pc
def i_SHLL2(ins,fmap):
    Rn = ins.operands[0]
    fmap[Rn] = fmap(Rn<<2)

@__pc
def i_SHLR2(ins,fmap):
    Rn = ins.operands[0]
    fmap[Rn] = fmap(Rn>>2)

@__pc
def i_SHLL8(ins,fmap):
    Rn = ins.operands[0]
    fmap[Rn] = fmap(Rn<<8)

@__pc
def i_SHLR8(ins,fmap):
    Rn = ins.operands[0]
    fmap[Rn] = fmap(Rn>>8)

@__pc
def i_SHLL16(ins,fmap):
    Rn = ins.operands[0]
    fmap[Rn] = fmap(Rn<<16)

@__pc
def i_SHLR16(ins,fmap):
    Rn = ins.operands[0]
    fmap[Rn] = fmap(Rn>>16)

@__pc
def i_SLEEP(ins,fmap):
    pass

@__pc
def i_TRAPA(ins,fmap):
    fmap[pc] = ext(ins.operands[0])

@__pc
def i_STC(ins,fmap):
    Rm,Rn = ins.operands
    predecr(ins,fmap)
    fmap[Rn] = fmap(Rm)

@__pc
def i_STS(ins,fmap):
    Rm,Rn = ins.operands
    predecr(ins,fmap)
    fmap[Rn] = fmap(Rm)

@__pc
def i_BF(ins,fmap):
    disp = ins.operands[0]
    if not ins.misc['delayed']: disp = disp+2 # "nop" delay slot
    fmap[pc] = fmap(tst(T==bit0,pc+disp,pc))

@__pc
def i_BT(ins,fmap):
    disp = ins.operands[0]
    if not ins.misc['delayed']: disp = disp+2 # "nop" delay slot
    fmap[pc] = fmap(tst(T==bit1,pc+disp,pc))

@__pc
def i_BRA(ins,fmap):
    disp = ins.operands[0]
    fmap[pc] = fmap(pc+disp)

@__pc
def i_BRAF(ins,fmap):
    Rm = ins.operands[0]
    fmap[pc] = fmap(pc+Rm)

@__pc
def i_BSR(ins,fmap):
    disp = ins.operands[0]
    fmap[PR] = fmap(pc)
    fmap[pc] = fmap(pc+disp)

@__pc
def i_BSRF(ins,fmap):
    Rm = ins.operands[0]
    fmap[PR] = fmap(pc)
    fmap[pc] = fmap(pc+Rm)

@__pc
def i_JMP(ins,fmap):
    Rm = ins.operands[0]
    fmap[pc] = fmap(Rm+4)

@__pc
def i_JSR(ins,fmap):
    Rm = ins.operands[0]
    fmap[PR] = fmap(pc)
    fmap[pc] = fmap(Rm+4)

@__pc
def i_RTS(ins,fmap):
    fmap[pc] = fmap(PR)

@__pc
def i_RTV(ins,fmap):
    Rm = ins.operands[0]
    fmap[R[0]] = fmap(Rm)
    fmap[pc] = fmap(PR)

@__pc
def i_LDC(ins,fmap):
    Rm,Rn = ins.operands
    if Rn is SR: Rm = Rm&0x63F3
    fmap[Rn] = fmap(Rm)
    postincr(ins,fmap)

@__pc
def i_LDS(ins,fmap):
    Rm,Rn = ins.operands
    fmap[Rn] = fmap(Rm)
    postincr(ins,fmap)

@__pc
def i_BAND(ins,fmap):
    imm,src2 = ins.operands
    assert imm._is_cst
    imm.sf = False
    indx = imm.value
    v = src2[indx:indx+1]
    fmap[T] = fmap(T&v)

@__pc
def i_BANDNOT(ins,fmap):
    imm,src2 = ins.operands
    assert imm._is_cst
    imm.sf = False
    indx = imm.value
    v = src2[indx:indx+1]
    fmap[T] = fmap(T&(~v))

@__pc
def i_BOR(ins,fmap):
    imm,src2 = ins.operands
    assert imm._is_cst
    imm.sf = False
    indx = imm.value
    v = src2[indx:indx+1]
    fmap[T] = fmap(T|v)

@__pc
def i_BORNOT(ins,fmap):
    imm,src2 = ins.operands
    assert imm._is_cst
    imm.sf = False
    indx = imm.value
    v = src2[indx:indx+1]
    fmap[T] = fmap(T|(~v))

@__pc
def i_BXOR(ins,fmap):
    imm,src2 = ins.operands
    assert imm._is_cst
    imm.sf = False
    indx = imm.value
    v = src2[indx:indx+1]
    fmap[T] = fmap(T^v)

@__pc
def i_BCLR(ins,fmap):
    imm,src2 = ins.operands
    assert imm._is_cst
    imm.sf = False
    indx = imm.value
    v = src2[indx:indx+1]
    fmap[v] = bit0

@__pc
def i_BSET(ins,fmap):
    imm,src2 = ins.operands
    assert imm._is_cst
    imm.sf = False
    indx = imm.value
    v = src2[indx:indx+1]
    fmap[v] = bit1

@__pc
def i_BLD(ins,fmap):
    imm,src2 = ins.operands
    assert imm._is_cst
    imm.sf = False
    indx = imm.value
    v = src2[indx:indx+1]
    fmap[T] = fmap(v)

@__pc
def i_BLDNOT(ins,fmap):
    imm,src2 = ins.operands
    assert imm._is_cst
    imm.sf = False
    indx = imm.value
    v = src2[indx:indx+1]
    fmap[T] = fmap(~v)

@__pc
def i_BST(ins,fmap):
    imm,src2 = ins.operands
    assert imm._is_cst
    imm.sf = False
    indx = imm.value
    v = src2[indx:indx+1]
    fmap[v] = fmap(T)

