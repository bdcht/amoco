# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2021 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *
from .utils import *

from amoco.cas.utils import *

# ------------------------------------------------------------------------------
# helpers and decorators :

def __npc(i_xxx):
    def npc(ins, fmap):
        fmap[pc] = fmap(pc) + ins.length
        i_xxx(ins, fmap)

    return npc


def trap(ins, fmap, trapname):
    internals["trap"] = trapname


# i_xxx is the translation of TriCore instruction xxx.
# ------------------------------------------------------------------------------

@__npc
def i_MOV(ins, fmap):
    dst, src = ins.operands
    fmap[dst] = fmap(src)

i_MOV_A = i_MOV_AA = i_MOV_D = i_MOV

@__npc
def i_MOVH(ins, fmap):
    dst, src = ins.operands
    v = fmap(src).zeroextend(32)
    fmap[dst] = v<<16

i_MOVH_A = i_MOVH

@__npc
def i_CMOV(ins, fmap):
    dst, cond, src = ins.operands
    fmap[dst] = fmap(tst(cond!=0,src,dst))

@__npc
def i_CMOVN(ins, fmap):
    dst, cond, src = ins.operands
    fmap[dst] = fmap(tst(cond==0,src,dst))

@__npc
def i_LEA(ins, fmap):
    dst = ins.operands[0]
    if ins.mode=="Absolute":
        src = ins.operands[1]
        fmap[dst] = src
    else:
        base,off = ins.operands[1:3]
        fmap[dst] = fmap(base+(off.signextend(32)))

@__npc
def i_LHA(ins, fmap):
    dst = ins.operands[0]
    if ins.mode=="Absolute":
        src = ins.operands[1]
        fmap[dst] = src

@__npc
def i_ABS(ins, fmap):
    dst, src = ins.operands
    v = fmap(src)
    fmap[dst] = tst(v>=0,v,0-v)

@__npc
def i_ABS_B(ins, fmap):
    dst, src = ins.operands
    v = fmap(src)
    fmap[dst] = composer([tst(p>=0,p,0-p) for p in (v[0:8],v[8:16],v[16:24],v[24:32])])

@__npc
def i_ABS_H(ins, fmap):
    dst, src = ins.operands
    v = fmap(src)
    fmap[dst] = composer([tst(p>=0,p,0-p) for p in (v[0:16],v[16:32])])

@__npc
def i_ABSS(ins, fmap):
    dst, src = ins.operands
    v = fmap(src)
    fmap[dst] = ssov(tst(v>=0,v,0-v),32)

@__npc
def i_ABSS_H(ins, fmap):
    dst, src = ins.operands
    v = fmap(src)
    fmap[dst] = composer([ssov(tst(p>=0,p,0-p),32) for p in (v[0:16],v[16:32])])


@__npc
def i_ADD(ins, fmap):
    dst, src1, src2 = ins.operands
    result,carry,overflow = AddWithCarry(fmap(src1),fmap(src2))
    fmap[dst] = result
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))

i_ADDI = i_ADDIH = i_ADD

@__npc
def i_ADD_A(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(src1+src2)
    fmap[dst] = result

i_ADDIH_A = i_ADD_A

@__npc
def i_ADD_B(ins, fmap):
    dst, src1, src2 = ins.operands
    result = []
    overflow = bit0
    advanced_overflow = bit0
    for i in (0,8,16,24):
        s1 = fmap(src1[i:i+8])
        s2 = fmap(src2[i:i+8])
        _r,_c,_o = AddWithCarry(s1,s2)
        result.append(_r)
        overflow |= _o
        advanced_overflow |= _r[7:8]^_r[6:7]
    fmap[dst] = composer(result)
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))

@__npc
def i_ADD_H(ins, fmap):
    dst, src1, src2 = ins.operands
    result = []
    overflow = bit0
    advanced_overflow = bit0
    for i in (0,16):
        s1 = fmap(src1[i:i+16])
        s2 = fmap(src2[i:i+16])
        _r,_c,_o = AddWithCarry(s1,s2)
        result.append(_r)
        overflow |= _o
        advanced_overflow |= _r[15:16]^_r[14:15]
    fmap[dst] = composer(result)
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))


@__npc
def i_ADDC(ins, fmap):
    dst, src1, src2 = ins.operands
    result,carry,overflow = AddWithCarry(fmap(src1),fmap(src2),fmap(C))
    fmap[dst] = result
    fmap[C] = carry
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))

@__npc
def i_ADDS(ins, fmap):
    dst, src1, src2 = ins.operands
    result,carry,overflow = AddWithCarry(fmap(src1),fmap(src2))
    fmap[dst] = ssov(result,32)
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))

@__npc
def i_ADDS_U(ins, fmap):
    dst, src1, src2 = ins.operands
    result,carry,overflow = AddWithCarry(fmap(src1),fmap(src2))
    fmap[dst] = suov(result,32)
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))

@__npc
def i_ADDX(ins, fmap):
    dst, src1, src2 = ins.operands
    result,carry,overflow = AddWithCarry(fmap(src1),fmap(src2))
    fmap[dst] = result
    fmap[C] = carry
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))

@__npc
def i_CADD(ins, fmap):
    dst, cond, src1, src2 = ins.operands
    result,carry,overflow = AddWithCarry(fmap(src1),fmap(src2))
    cond = fmap(cond!=0)
    fmap[dst] = tst(cond,result,fmap(dst))
    fmap[V] = tst(cond,overflow,fmap(V))
    fmap[SV] = tst(cond&overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = tst(cond,advanced_overflow,fmap(AV))
    fmap[SAV] = tst(cond&advanced_overflow,bit1,fmap(SAV))

@__npc
def i_CADDN(ins, fmap):
    dst, cond, src1, src2 = ins.operands
    result,carry,overflow = AddWithCarry(fmap(src1),fmap(src2))
    cond = fmap(cond==0)
    fmap[dst] = tst(cond,result,fmap(dst))
    fmap[V] = tst(cond,overflow,fmap(V))
    fmap[SV] = tst(cond&overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = tst(cond,advanced_overflow,fmap(AV))
    fmap[SAV] = tst(cond&advanced_overflow,bit1,fmap(SAV))

@__npc
def i_ADDSC_A(ins, fmap):
    dst, src1, src2, n = ins.operands
    result = fmap(src1+(src2<<n))
    fmap[dst] = result

@__npc
def i_ADDSC_AT(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap((src1+(src2>>3))&0xfffffffc)
    fmap[dst] = result

@__npc
def i_SUB(ins, fmap):
    dst, src1, src2 = ins.operands
    result,carry,overflow = SubWithBorrow(fmap(src1),fmap(src2))
    fmap[dst] = result
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))

i_SUBI = i_SUBIH = i_SUB

@__npc
def i_RSUB(ins, fmap):
    dst, src1, src2 = ins.operands
    result,carry,overflow = SubWithBorrow(fmap(src2),fmap(src1))
    fmap[dst] = result
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))

@__npc
def i_RSUBS(ins, fmap):
    dst, src1, src2 = ins.operands
    result,carry,overflow = SubWithBorrow(fmap(src2),fmap(src1))
    fmap[dst] = ssov(result,32)
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))

@__npc
def i_RSUBS_U(ins, fmap):
    dst, src1, src2 = ins.operands
    result,carry,overflow = SubWithBorrow(fmap(src2),fmap(src1))
    fmap[dst] = suov(result,32)
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))

@__npc
def i_SUB_A(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(src1-src2)
    fmap[dst] = result

i_SUBIH_A = i_SUB_A

@__npc
def i_SUBC(ins, fmap):
    dst, src1, src2 = ins.operands
    result,carry,overflow = SubWithBorrow(fmap(src1),fmap(src2),fmap(C))
    fmap[dst] = result
    fmap[C] = carry
    fmap[V] = overflow
    fmap[SV] = tst(overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = advanced_overflow
    fmap[SAV] = tst(advanced_overflow,bit1,fmap(SAV))

@__npc
def i_CSUB(ins, fmap):
    dst, cond, src1, src2 = ins.operands
    result,carry,overflow = SubWithBorrow(fmap(src1),fmap(src2))
    cond = fmap(cond!=0)
    fmap[dst] = tst(cond,result,fmap(dst))
    fmap[V] = tst(cond,overflow,fmap(V))
    fmap[SV] = tst(cond&overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = tst(cond,advanced_overflow,fmap(AV))
    fmap[SAV] = tst(cond&advanced_overflow,bit1,fmap(SAV))

@__npc
def i_CSUBN(ins, fmap):
    dst, cond, src1, src2 = ins.operands
    result,carry,overflow = SubWithBorrow(fmap(src1),fmap(src2))
    cond = fmap(cond==0)
    fmap[dst] = tst(cond,result,fmap(dst))
    fmap[V] = tst(cond,overflow,fmap(V))
    fmap[SV] = tst(cond&overflow,bit1,fmap(SV))
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = tst(cond,advanced_overflow,fmap(AV))
    fmap[SAV] = tst(cond&advanced_overflow,bit1,fmap(SAV))

@__npc
def i_SH(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(tst(src2>=0,src1<<src2,src1>>(-src2)))
    fmap[dst] = result

@__npc
def i_SHA(ins, fmap):
    dst, src1, src2 = ins.operands
    x = fmap(src1)
    count = fmap(src2)
    if count._is_cst:
        n = count.value
        result = x<<n if n>=0 else op(OP_ASR,x,-n)
        carry = bit0
        if n>0:
            carry = x[32-n:32]!=0
        elif n<0:
            carry = x[0:-n]!=0
    else:
        result = fmap(tst(src2>=0,src1<<src2,op(OP_ASR,src1,-src2)))
        carry = top(1)
    fmap[dst] = result
    fmap[C] = carry
    fmap[SV] = top(1)
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = tst(cond,advanced_overflow,fmap(AV))
    fmap[SAV] = tst(cond&advanced_overflow,bit1,fmap(SAV))

@__npc
def i_SHAS(ins, fmap):
    dst, src1, src2 = ins.operands
    x = fmap(src1)
    count = fmap(src2)
    if count._is_cst:
        n = count.value
        result = x<<n if n>=0 else op(OP_ASR,x,-n)
        carry = bit0
        if n>0:
            carry = x[32-n:32]!=0
        elif n<0:
            carry = x[0:-n]!=0
    else:
        result = fmap(tst(src2>=0,src1<<src2,op(OP_ASR,src1,-src2)))
        carry = top(1)
    fmap[dst] = ssov(result,32)
    fmap[C] = carry
    fmap[SV] = top(1)
    advanced_overflow = result[31:32]^result[30:31]
    fmap[AV] = tst(cond,advanced_overflow,fmap(AV))
    fmap[SAV] = tst(cond&advanced_overflow,bit1,fmap(SAV))

@__npc
def i_AND(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(src1&src2)
    fmap[dst] = result

@__npc
def i_NAND(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(~(src1&src2))
    fmap[dst] = result

@__npc
def i_ANDN(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(src1&(~src2))
    fmap[dst] = result

@__npc
def i_OR(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(src1|src2)
    fmap[dst] = result

@__npc
def i_NOR(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(~(src1|src2))
    fmap[dst] = result

@__npc
def i_ORN(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(src1|(~src2))
    fmap[dst] = result

@__npc
def i_XOR(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(src1^src2)
    fmap[dst] = result

@__npc
def i_XNOR(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(~(src1^src2))
    fmap[dst] = result

@__npc
def i_EQ(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(src1==src2)
    fmap[dst] = result.zeroextend(dst.size)

i_EQ_A = i_EQ

@__npc
def i_NOT(ins, fmap):
    src = ins.operands[0]
    fmap[src] = fmap(~src)

@__npc
def i_EQZ_A(ins, fmap):
    dst, src = ins.operands
    result = fmap(src==0)
    fmap[dst] = result.zeroextend(dst.size)

@__npc
def i_NEZ_A(ins, fmap):
    dst, src = ins.operands
    result = fmap(src!=0)
    fmap[dst] = result.zeroextend(dst.size)

@__npc
def i_NE(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(src1!=src2)
    fmap[dst] = result.zeroextend(dst.size)

@__npc
def i_GE(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(src1>=src2)
    fmap[dst] = result.zeroextend(dst.size)

i_GE_A = i_GE

@__npc
def i_GE_U(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(op(OP_GEU,src1,src2))
    fmap[dst] = result.zeroextend(dst.size)

@__npc
def i_LT(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(src1<src2)
    fmap[dst] = result.zeroextend(dst.size)

i_LT_A = i_LT

@__npc
def i_LT_U(ins, fmap):
    dst, src1, src2 = ins.operands
    result = fmap(op(OP_LTU,src1,src2))
    fmap[dst] = result.zeroextend(dst.size)

@__npc
def i_AND_EQ(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]&(src1==src2))

@__npc
def i_OR_EQ(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]|(src1==src2))

@__npc
def i_XOR_EQ(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]^(src1==src2))

@__npc
def i_AND_GE(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]&(src1>=src2))

@__npc
def i_OR_GE(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]|(src1>=src2))

@__npc
def i_XOR_GE(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]^(src1>=src2))

@__npc
def i_AND_LT(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]&(src1<src2))

@__npc
def i_OR_LT(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]|(src1<src2))

@__npc
def i_XOR_LT(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]^(src1<src2))

@__npc
def i_AND_NE(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]&(src1!=src2))

@__npc
def i_OR_NE(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]|(src1!=src2))

@__npc
def i_XOR_NE(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]^(src1!=src2))

@__npc
def i_AND_GE_U(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]&op(OP_GEU,src1,src2))

@__npc
def i_OR_GE_U(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]|op(OP_GEU,src1,src2))

@__npc
def i_XOR_GE_U(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]^op(OP_GEU,src1,src2))

@__npc
def i_AND_LT_U(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]&op(OP_LTU,src1,src2))

@__npc
def i_OR_LT_U(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]|op(OP_LTU,src1,src2))

@__npc
def i_XOR_LT_U(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]^op(OP_LTU,src1,src2))

@__npc
def i_AND_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst] = fmap(op(OP_AND,src1,src2)).zeroextend(dst.size)

@__npc
def i_NAND_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst] = fmap(~op(OP_AND,src1,src2)).zeroextend(dst.size)

@__npc
def i_AND_AND_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]&op(OP_AND,src1,src2))

@__npc
def i_AND_ANDN_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]&op(OP_AND,src1,~src2))

@__npc
def i_AND_NOR_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]&(~op(OP_OR,src1,src2)))

@__npc
def i_AND_OR_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]&(op(OP_OR,src1,src2)))

@__npc
def i_OR_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst] = fmap(op(OP_OR,src1,src2)).zeroextend(dst.size)

@__npc
def i_NOR_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst] = fmap(~op(OP_OR,src1,src2)).zeroextend(dst.size)

@__npc
def i_ORN_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst] = fmap(op(OP_OR,src1,~src2)).zeroextend(dst.size)

@__npc
def i_XOR_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst] = fmap(op(OP_XOR,src1,src2)).zeroextend(dst.size)

@__npc
def i_XNOR_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst] = fmap(~op(OP_XOR,src1,src2)).zeroextend(dst.size)

@__npc
def i_OR_AND_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]|op(OP_AND,src1,src2))

@__npc
def i_OR_ANDN_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]|op(OP_AND,src1,~src2))

@__npc
def i_OR_NOR_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]|(~op(OP_OR,src1,src2)))

@__npc
def i_OR_OR_T(ins, fmap):
    dst, src1, src2 = ins.operands
    fmap[dst[0:1]] = fmap(dst[0:1]|(op(OP_OR,src1,src2)))

# ------------------------------------------------------------------------------

def load(ins,fmap,nbytes,sign):
    dst = ins.operands[0]
    sz = nbytes*8
    if ins.mode == "Absolute":
        src = ins.operands[1]
        off = cst(0,32)
        fmap[dst] = fmap(mem(src+off,sz)).extend(sign,dst.size)
        return
    if ins.mode == "Short-offset":
        src = ins.operands[1]
        off = ins.operands[2].signextend(src.size)
        fmap[dst] = fmap(mem(src+off,sz)).extend(sign,dst.size)
        return
    if ins.mode == "Bit-reverse":
        src = ins.operands[1]
        index = A[ins.b+1][0:16].zeroextend(src.size)
        incr = fmap(A[ins.b+1][16:32])
        fmap[dst] = fmap(mem(src+index,sz)).extend(sign,dst.size)
        new_index = reverse16(reverse16(index[0:16])+reverse16(incr))
        fmap[A[ins.b+1]] = composer([new_index,incr])
        return
    if ins.mode == "Circular":
        src = ins.operands[1]
        off = ins.operands[2].signextend(src.size)
        index = A[ins.b+1][0:16].zeroextend(src.size)
        length = fmap(A[ins.b+1][16:32]).zeroextend(src.size)
        new_index = fmap(index + off)
        fmap[dst] = fmap(mem(src+index,sz)).extend(sign,dst.size)
        new_index = tst(new_index<0, new_index+length, new_index%length)
        fmap[A[ins.b+1]] = composer([new_index[0:16],length[0:16]])
        return
    if ins.mode == "Post-increment":
        src = ins.operands[1]
        off = ins.operands[2].signextend(src.size)
        _ea = fmap(src)
        fmap[dst] = fmap[mem(_ea,sz)].extend(sign,dst.size)
        fmap[src] = _ea+off
        return
    if ins.mode == "Pre-increment":
        src = ins.operands[1]
        off = ins.operands[2].signextend(src.size)
        _ea = fmap(src+off)
        fmap[dst] = fmap[mem(_ea,sz)].extend(sign,dst.size)
        fmap[src] = _ea
        return
    # SC, SLR, SLRO modes:
    src = ins.operands[1]
    off = ins.operands[2]
    fmap[dst] = fmap(mem(src+off,sz)).extend(sign,dst.size)

@__npc
def i_LD_A(ins,fmap):
    load(ins,fmap,4,False)

@__npc
def i_LD_B(ins,fmap):
    load(ins,fmap,1,True)

@__npc
def i_LD_BU(ins,fmap):
    load(ins,fmap,1,False)

@__npc
def i_LD_H(ins,fmap):
    load(ins,fmap,2,True)

@__npc
def i_LD_HU(ins,fmap):
    load(ins,fmap,2,False)

@__npc
def i_LD_W(ins,fmap):
    load(ins,fmap,4,False)

@__npc
def i_LD_D(ins,fmap):
    load(ins,fmap,8,False)

@__npc
def i_LD_Q(ins,fmap):
    load(ins,fmap,2,False)
    dst = ins.operands[0]
    fmap[dst] = fmap(dst<<16)

i_LD_DA = i_LD_D

def store(ins,fmap,nbytes,src=None):
    sz = nbytes*8
    if src is None:
        src = fmap(ins.operands[-1])[0:sz]
    if ins.mode == "Absolute":
        dst = mem(fmap(ins.operands[0]),sz)
        fmap[dst] = src
        return
    if ins.mode == "Short-offset":
        addr = fmap(ins.operands[0])
        off = ins.operands[1].signextend(addr.size)
        dst = mem(addr+off,sz)
        fmap[dst] = src
        return
    if ins.mode == "Bit-reverse":
        addr = fmap(ins.operands[0])
        index = fmap(A[ins.b+1])[0:16].zeroextend(addr.size)
        incr = fmap(A[ins.b+1][16:32])
        dst = mem(addr+index,sz)
        fmap[dst] = src
        new_index = reverse16(reverse16(index[0:16])+reverse16(incr))
        fmap[A[ins.b+1]] = composer([new_index,incr])
        return
    if ins.mode == "Circular":
        addr = fmap(ins.operands[0])
        off = ins.operands[2].signextend(addr.size)
        _Abp1 = fmap(A[ins.b+1])
        index = _Abp1[0:16].zeroextend(addr.size)
        length = _Abp1[16:32].zeroextend(addr.size)
        new_index = index + off
        dst = mem(addr+index,sz)
        fmap[dst] = src
        new_index = tst(new_index<0, new_index+length, new_index%length)
        fmap[A[ins.b+1]] = composer([new_index[0:16],length[0:16]])
        return
    if ins.mode == "Post-increment":
        _ea = ins.operands[0]
        off = ins.operands[1].signextend(_ea.size)
        dst = mem(fmap(_ea),sz)
        fmap[dst] = src
        fmap[_ea] = fmap(_ea+off)
        return
    if ins.mode == "Pre-increment":
        addr = ins.operands[0]
        off = ins.operands[1].signextend(addr.size)
        _ea = fmap(addr+off)
        fmap[mem(_ea,sz)] = fmap(src)
        fmap[addr] = _ea
        return
    # SC, SLR, SLRO modes:
    addr = fmap(ins.operands[0])
    off = ins.operands[1]
    dst = mem(addr+off,sz)
    fmap[dst] = src

@__npc
def i_ST_A(ins,fmap):
    store(ins,fmap,4)

@__npc
def i_ST_B(ins,fmap):
    store(ins,fmap,1)

@__npc
def i_ST_H(ins,fmap):
    store(ins,fmap,2)

@__npc
def i_ST_W(ins,fmap):
    store(ins,fmap,4)

@__npc
def i_ST_D(ins,fmap):
    store(ins,fmap,8)

@__npc
def i_ST_Q(ins,fmap):
    _r = fmap(ins.operands[0][16:32])
    store(ins,fmap,2,src=_r)

i_ST_DA = i_ST_D

# ------------------------------------------------------------------------------

def i_CALL(ins,fmap):
    off = ins.operands[0]
    fmap[CDE] = env.bit1
    ret_addr = fmap(pc)+4
    tmp_fcx = fmap(FCX)
    _ea = composer([cst(0,6),FCXO,cst(0,6),FCXS])
    new_fcx = fmap(mem(_ea,32))
    disp=0
    for r in (PCXI,PSW,A[10],A[11],D[8],D[9],D[10],D[11],A[12],A[13],A[14],
              A[15],D[12],D[13],D[14],D[15]):
        fmap[mem(_ea,32,disp=disp)] = r
        disp += 4
    fmap[PCPN] = fmap(CCPN)
    fmap[PIE] = fmap(IE)
    fmap[UL] = bit1
    fmap[PCXO] = fmap(FCXO)
    fmap[PCXS] = fmap(FCXS)
    fmap[FCX] = new_fcx
    fmap[pc] = fmap(pc + off)
    fmap[ra] = ret_addr

i_CALLA = i_CALL

def i_RET(ins,fmap):
    fmap[pc] = fmap(ra)&0xfffffffe
    _ea = composer([cst(0,6),PCXO,cst(0,6),PCXS])
    new_pcxi = fmap(mem(_ea,32))
    new_psw = fmap(mem(_ea,32,disp=4))
    disp=8
    for r in (A[10],A[11],D[8],D[9],D[10],D[11],A[12],A[13],A[14],
              A[15],D[12],D[13],D[14],D[15]):
        fmap[r] = fmap(mem(_ea,32,disp=disp))
        disp += 4
    fmap[mem(_ea,32)] = fmap(FCX)
    fmap[FCX] = fmap(PCXI)
    fmap[PCXI] = new_pcxi
    fmap[PSW] = new_psw

def i_RFE(ins,fmap):
    fmap[pc] = fmap(ra)&0xfffffffe
    fmap[IE] = fmap(PIE)
    fmap[CCPN] = fmap(PCPN)
    _ea = composer([cst(0,6),PCXO,cst(0,6),PCXS])
    new_pcxi = fmap(mem(_ea,32))
    new_psw = fmap(mem(_ea,32,disp=4))
    disp=8
    for r in (A[10],A[11],D[8],D[9],D[10],D[11],A[12],A[13],A[14],
              A[15],D[12],D[13],D[14],D[15]):
        fmap[r] = fmap(mem(_ea,32,disp=disp))
        disp += 4
    fmap[mem(_ea,32)] = fmap(FCX)
    fmap[FCX] = fmap(PCXI)
    fmap[PCXI] = new_pcxi
    fmap[PSW] = new_psw


def i_CALLI(ins,fmap):
    fmap[CDE] = env.bit1
    ret_addr = fmap(pc)+4
    tmp_fcx = fmap(FCX)
    _ea = composer([cst(0,6),FCXO,cst(0,6),FCXS])
    new_fcx = fmap(mem(_ea,32))
    disp=0
    for r in (PCXI,PSW,A[10],A[11],D[8],D[9],D[10],D[11],A[12],A[13],A[14],
              A[15],D[12],D[13],D[14],D[15]):
        fmap[mem(_ea,32,disp=disp)] = r
        disp += 4
    fmap[PCPN] = fmap(CCPN)
    fmap[PIE] = fmap(IE)
    fmap[UL] = bit1
    fmap[PCXO] = fmap(FCXO)
    fmap[PCXS] = fmap(FCXS)
    fmap[FCX] = new_fcx
    fmap[pc] = fmap(ins.operands[0]<<1)
    fmap[ra] = ret_addr

def i_FCALL(ins,fmap):
    #push ra:
    fmap[sp] = fmap(sp-4)
    fmap[mem(sp,4)] = fmap(ra)
    #update ra:
    ret_addr = fmap(pc)+4
    fmap[ra] = ret_addr
    off = ins.operands[0]
    fmap[pc] = fmap(pc + off)

def i_FRET(ins,fmap):
    fmap[pc] = fmap(ra)&0xfffffffe
    fmap[ra] = fmap(mem(sp,4))
    fmap[sp] = fmap(sp+4)

i_FCALLA = i_FCALL

def i_FCALLI(ins,fmap):
    #push ra:
    fmap[sp] = fmap(sp-4)
    fmap[mem(sp,4)] = fmap(ra)
    #update ra:
    ret_addr = fmap(pc)+4
    fmap[ra] = ret_addr
    fmap[pc] = fmap(ins.operands[0]<<1)

def i_JA(ins,fmap):
    fmap[pc] = fmap(ins.operands[0])

def i_J(ins,fmap):
    off = ins.operands[0]
    fmap[pc] = fmap(pc + off)

def i_JNZ(ins,fmap):
    if len(ins.operands)==1:
        off = ins.operands[0]
        fmap[pc] = fmap(tst(D[15]!=0, pc+off, pc+2))
    else:
        _r,off = ins.operands
        fmap[pc] = fmap(tst(_r!=0, pc+off, pc+2))

def i_JZ(ins,fmap):
    if len(ins.operands)==1:
        off = ins.operands[0]
        fmap[pc] = fmap(tst(D[15]==0, pc+off, pc+2))
    else:
        _r,off = ins.operands
        fmap[pc] = fmap(tst(_r==0, pc+off, pc+2))


def i_LOOP(ins,fmap):
    _r,off = ins.operands
    fmap[pc] = fmap(tst(_r!=0, pc+off, pc+4))
    fmap[_r] = fmap(_r-1)

def i_LOOPU(ins,fmap):
    off = ins.operands[0]
    fmap[pc] = fmap(pc+off)

def i_JLA(ins,fmap):
    fmap[ra] = fmap(pc+4)
    fmap[pc] = fmap(ins.operands[0])

def i_JL(ins,fmap):
    off = ins.operands[0]
    fmap[ra] = fmap(pc+4)
    fmap[pc] = fmap(pc+off)

def i_JI(ins,fmap):
    fmap[pc] = fmap(ins.operands[0]&0xfffffffe)

def i_JLI(ins,fmap):
    fmap[ra] = fmap(pc+4)
    fmap[pc] = fmap(ins.operands[0]&0xfffffffe)




# ------------------------------------------------------------------------------
# system instructions:

@__npc
def i_DEBUG(ins, fmap):
    trap(ins,fmap,ins.mnemonic)

@__npc
def i_ISYNC(ins, fmap):
    trap(ins,fmap,ins.mnemonic)

@__npc
def i_DSYNC(ins, fmap):
    trap(ins,fmap,ins.mnemonic)

@__npc
def i_BISR(ins,fmap):
    tmp_fcx = fmap(FCX)
    _ea = composer([cst(0,6),FCXO,cst(0,6),FCXS])
    new_fcx = fmap(mem(_ea,32))
    disp=0
    for r in (PCXI,ra,A[2],A[3],D[0],D[1],D[2],D[3],A[4],A[5],A[6],
              A[7],D[4],D[5],D[6],D[7]):
        fmap[mem(_ea,32,disp=disp)] = r
        disp += 4
    fmap[PCPN] = fmap(CCPN)
    fmap[PIE] = fmap(IE)
    fmap[UL] = bit0
    fmap[PCXO] = fmap(FCXO)
    fmap[PCXS] = fmap(FCXS)
    fmap[FCX] = new_fcx
    fmap[IE] = bit1
    fmap[CCPN] = ins.operands[0:8]

@__npc
def i_MTCR(ins,fmap):
    offset = ins.operands[0]
    src = fmap(ins.operands[1])
    dst = CSFR[ins.operands[0].value]
    fmap[dst] = src

def i_SYSCALL(ins,fmap):
    trap(ins,fmap,"SYS")

@__npc
def i_RSTV(ins,fmap):
    fmap[V] = bit0
    fmap[SV] = bit0
    fmap[AV] = bit0
    fmap[SAV] = bit0


def i_TRAPV(ins,fmap):
    if fmap(V)==bit1:
        trap(ins,fmap,"OVF")

@__npc
def i_WAIT(ins,fmap):
    pass

@__npc
def i_ENABLE(ins,fmap):
    fmap[IE] = bit1

@__npc
def i_DISABLE(ins,fmap):
    dst = ins.operands[0]
    fmap[dst] = composer([fmap(IE),cst(0,31)])
    fmap[IE] = bit0

@__npc
def i_RESTORE(ins,fmap):
    fmap[IE] = fmap(ins.operands[0].bit(0))

