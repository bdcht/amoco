# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2012-2013 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

# ref: The SPARC Architecture Manual Version 8, Revision SAV080SI9308.
# 72 basic instructions, all encoded in 32 bits.

from amoco.arch.sparc import env

from amoco.arch.core import *

# -------------------------------------------------------
# instruction sparcs decoders
# -------------------------------------------------------

ISPECS = []

# format 3
# ---------

# ld instructions:
@ispec("32[ 11 rd(5) 0 0=a 1001 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="ldsb")
@ispec("32[ 11 rd(5) 0 0=a 1010 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="ldsh",)
@ispec("32[ 11 rd(5) 0 0=a 0001 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="ldub",)
@ispec("32[ 11 rd(5) 0 0=a 0010 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="lduh",)
@ispec("32[ 11 rd(5) 0 0=a 0000 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="ld")
@ispec("32[ 11 rd(5) 0 0=a 0011 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="ldd")
@ispec("32[ 11 rd(5) 0 0=a 1101 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="ldstub",)
@ispec("32[ 11 rd(5) 0 0=a 1111 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="swap",)
@ispec("32[ 11 rd(5) 0 1=a 1001 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="ldsba")
@ispec("32[ 11 rd(5) 0 1=a 1010 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="ldsha",)
@ispec("32[ 11 rd(5) 0 1=a 0001 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="lduba",)
@ispec("32[ 11 rd(5) 0 1=a 0010 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="lduha",)
@ispec("32[ 11 rd(5) 0 1=a 0000 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="lda")
@ispec("32[ 11 rd(5) 0 1=a 0011 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="ldda")
@ispec("32[ 11 rd(5) 0 1=a 1101 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="ldstuba",)
@ispec("32[ 11 rd(5) 0 1=a 1111 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="swapa",)
def sparc_ld_(obj, rd, a, op3, rs1, i, asi, rs2, simm13):
    adr = env.r[rs1]
    if i == 0:
        adr += env.r[rs2]
        src = env.ptr(adr, seg=asi)
    else:
        adr += env.cst(simm13, 13).signextend(32)
        src = env.ptr(adr)
    dst = env.r[rd]
    if op3 & 0xF == 0b0011 and rd % 1 == 1:
        raise InstructionError(obj)
    obj.operands = [src, dst]
    obj.type = type_data_processing


# ld fsr/csr instructions:
@ispec(
    "32[ 11 rd(5) 1 a 0000 =op3(6) rs1(5) i unused(8) rs2(5) =simm13(13) ]",
    mnemonic="ld",
)
@ispec(
    "32[ 11 rd(5) 1 a 0011 =op3(6) rs1(5) i unused(8) rs2(5) =simm13(13) ]",
    mnemonic="ldd",
)
@ispec(
    "32[ 11 rd(5) 1 a 0001 =op3(6) rs1(5) i unused(8) rs2(5) =simm13(13) ]",
    mnemonic="ld",
)
def sparc_ldf_ldc(obj, rd, a, op3, rs1, i, unused, rs2, simm13):
    adr = env.r[rs1]
    if i == 0:
        adr += env.r[rs2]
    else:
        adr += env.cst(simm13, 13).signextend(32)
    src = env.ptr(adr)
    dst = env.f[rd] if a == 0 else env.c[rd]
    if op3 & 0xF == 0b0001:
        dst = env.fsr if a == 0 else env.csr
    obj.operands = [src, dst]
    obj.type = type_data_processing


# st instructions:
@ispec("32[ 11 rd(5) 0 0=a 0101 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="stb")
@ispec("32[ 11 rd(5) 0 0=a 0110 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="sth")
@ispec("32[ 11 rd(5) 0 0=a 0100 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="st")
@ispec("32[ 11 rd(5) 0 0=a 0111 =op3(6) rs1(5)   i asi(8) rs2(5) =simm13(13) ]", mnemonic="std")
@ispec("32[ 11 rd(5) 0 1=a 0101 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="stba")
@ispec("32[ 11 rd(5) 0 1=a 0110 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="stha")
@ispec("32[ 11 rd(5) 0 1=a 0100 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="sta")
@ispec("32[ 11 rd(5) 0 1=a 0111 =op3(6) rs1(5) 0=i asi(8) rs2(5) =simm13(13) ]", mnemonic="stda")
def sparc_st_(obj, rd, a, op3, rs1, i, asi, rs2, simm13):
    adr = env.r[rs1]
    if i == 0:
        adr += env.r[rs2]
        dst = env.ptr(adr, asi)
    else:
        adr += env.cst(simm13, 13).signextend(32)
        dst = env.ptr(adr)
    src = env.r[rd]
    if obj.mnemonic == "std" and rd % 1 == 1:
        raise InstructionError(obj)
    obj.operands = [src, dst]
    obj.type = type_data_processing


# st f/c instructions:
@ispec(
    "32[ 11 rd(5) 1 a 0100 =op3(6) rs1(5) i unused(8) rs2(5) =simm13(13) ]",
    mnemonic="st",
)
@ispec(
    "32[ 11 rd(5) 1 a 0111 =op3(6) rs1(5) i unused(8) rs2(5) =simm13(13) ]",
    mnemonic="std",
)
@ispec(
    "32[ 11 rd(5) 1 a 0101 =op3(6) rs1(5) i unused(8) rs2(5) =simm13(13) ]",
    mnemonic="st",
)
@ispec(
    "32[ 11 rd(5) 1 a 0110 =op3(6) rs1(5) i unused(8) rs2(5) =simm13(13) ]",
    mnemonic="std",
)
def sparc_stf_stc(obj, rd, a, op3, rs1, i, unused, rs2, simm13):
    adr = env.r[rs1]
    if i == 0:
        adr += env.r[rs2]
    else:
        adr += env.cst(simm13, 13).signextend(32)
    dst = env.ptr(adr)
    src = env.f[rd] if a == 0 else env.c[rd]
    if op3 & 0xF == 0b0101:
        src = env.fsr if a == 0 else env.csr
    elif op3 & 0xF == 0b0110:
        src = env.fq if a == 0 else env.cq
    obj.operands = [src, dst]
    obj.type = type_data_processing


@ispec("32[ 10 rd(5) 0 a 0001 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="and")
@ispec("32[ 10 rd(5) 0 a 0101 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="andn")
@ispec("32[ 10 rd(5) 0 a 0010 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="or")
@ispec("32[ 10 rd(5) 0 a 0110 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="orn")
@ispec("32[ 10 rd(5) 0 a 0011 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="xor")
@ispec("32[ 10 rd(5) 0 a 0111 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="xnor")
def sparc_logic_(obj, rd, a, rs1, i, rs2, simm13):
    obj.misc["icc"] = a == 1
    src1 = env.r[rs1]
    src2 = env.r[rs2] if i == 0 else env.cst(simm13, 13).signextend(32)
    dst = env.r[rd]
    obj.operands = [src1, src2, dst]
    obj.type = type_data_processing


@ispec("32[ 10 rd(5) 0 a 0000 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="add")
@ispec("32[ 10 rd(5) 0 a 1000 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="addx")
@ispec("32[ 10 rd(5) 0 a 0100 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="sub")
@ispec("32[ 10 rd(5) 0 a 1100 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="subx")
@ispec("32[ 10 rd(5) 0 a 1010 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="umul")
@ispec("32[ 10 rd(5) 0 a 1011 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="smul")
@ispec("32[ 10 rd(5) 0 a 1110 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="udiv")
@ispec("32[ 10 rd(5) 0 a 1111 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="sdiv")
def sparc_arith_(obj, rd, a, rs1, i, rs2, simm13):
    obj.misc["icc"] = a == 1
    src1 = env.r[rs1]
    src2 = env.r[rs2] if i == 0 else env.cst(simm13, 13).signextend(32)
    dst = env.r[rd]
    obj.operands = [src1, src2, dst]
    obj.type = type_data_processing


@ispec("32[ 10 rd(5) 100101 rs1(5) i -------- rs2(5) ]", mnemonic="sll")
@ispec("32[ 10 rd(5) 100110 rs1(5) i -------- rs2(5) ]", mnemonic="srl")
@ispec("32[ 10 rd(5) 100111 rs1(5) i -------- rs2(5) ]", mnemonic="sra")
def sparc_shift_(obj, rd, rs1, i, rs2):
    src1 = env.r[rs1]
    src2 = env.r[rs2] if i == 0 else env.cst(rs2, 5)
    dst = env.r[rd]
    obj.operands = [src1, src2, dst]
    obj.type = type_data_processing


@ispec("32[ 10 rd(5) 100000 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="taddcc")
@ispec(
    "32[ 10 rd(5) 100010 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="taddcctv"
)
@ispec("32[ 10 rd(5) 100001 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="tsubcc")
@ispec(
    "32[ 10 rd(5) 100011 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="tsubcctv"
)
@ispec("32[ 10 rd(5) 100100 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="mulscc")
@ispec("32[ 10 rd(5) 111100 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="save")
@ispec("32[ 10 rd(5) 111101 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="restore")
def sparc_tagged_(obj, rd, rs1, i, rs2, simm13):
    src1 = env.r[rs1]
    src2 = env.r[rs2] if i == 0 else env.cst(simm13, 13).signextend(32)
    dst = env.r[rd]
    obj.operands = [src1, src2, dst]
    obj.type = type_data_processing


@ispec("32[ 10 rd(5) 111000 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="jmpl")
def sparc_jmpl(obj, rd, rs1, i, rs2, simm13):
    src1 = env.r[rs1]
    src2 = env.r[rs2] if i == 0 else env.cst(simm13, 13).signextend(32)
    adr = src1 + src2
    dst = env.r[rd]
    obj.operands = [adr, dst]
    obj.misc["delayed"] = True
    obj.type = type_control_flow


@ispec("32[ 10 ----- 111001 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="rett")
def sparc_rett(obj, rs1, i, rs2, simm13):
    src1 = env.r[rs1]
    src2 = env.r[rs2] if i == 0 else env.cst(simm13, 13).signextend(32)
    adr = src1 + src2
    obj.operands = [adr]
    obj.type = type_control_flow


@ispec("32[ 10 - .cond(4) 111010 rs1(5) i -------- rs2(5) =imm7(7) ]", mnemonic="t")
def sparc_Ticc(obj, rs1, i, rs2, imm7):
    src1 = env.r[rs1]
    src2 = env.r[rs2] if i == 0 else env.cst(imm7, 7).signextend(32)
    obj.src = (src1 + src2)[0:7]
    obj.operands = [obj.src]
    obj.type = type_control_flow


@ispec("32[ 10 rd(5) 101000 rs1(5) - ------------- ]", mnemonic="rd", _src=env.y)
@ispec("32[ 10 rd(5) 101001 rs1(5) - ------------- ]", mnemonic="rd", _src=env.psr)
@ispec("32[ 10 rd(5) 101010 rs1(5) - ------------- ]", mnemonic="rd", _src=env.wim)
@ispec("32[ 10 rd(5) 101011 rs1(5) - ------------- ]", mnemonic="rd", _src=env.tbr)
def sparc_rd_(obj, rd, rs1, _src):
    if _src == env.y:
        if rs1 == 15 and rd == 0:
            obj.mnemonic = "stbar"
        elif rd != 0:
            _src = env.asr[rd]
    dst = env.r[rd]
    obj.operands = [_src, dst]
    obj.type = type_other

@ispec("32[ 10 00000 101000 01111 - ------------- ]", mnemonic="stbar")
def sparc_rd_(obj, _src):
    _src == env.y
    dst = env.r[rd]
    obj.operands = [_src, dst]
    obj.type = type_other

@ispec(
    "32[ 10 rd(5) 101000 rs1(5) i -------- rs2(5) =simm13(13) ]",
    mnemonic="wr",
    _dst=env.y,
)
@ispec(
    "32[ 10 rd(5) 101001 rs1(5) i -------- rs2(5) =simm13(13) ]",
    mnemonic="wr",
    _dst=env.psr,
)
@ispec(
    "32[ 10 rd(5) 101010 rs1(5) i -------- rs2(5) =simm13(13) ]",
    mnemonic="wr",
    _dst=env.wim,
)
@ispec(
    "32[ 10 rd(5) 101011 rs1(5) i -------- rs2(5) =simm13(13) ]",
    mnemonic="wr",
    _dst=env.tbr,
)
def sparc_wr_(obj, rd, rs1, i, rs2, simm13, _dst):
    if _dst == env.y:
        if rs1 != 0:
            _dst = env.asr[rs1]
    src1 = env.r[rs1]
    src2 = env.r[rs2] if i == 0 else env.cst(simm13, 13).signextend(32)
    obj.operands = [src1, src2, _dst]
    obj.type = type_other


@ispec("32[ 10 ----- 111011 rs1(5) i -------- rs2(5) =simm13(13) ]", mnemonic="flush")
def sparc_flush(obj, rs1, i, rs2, simm13):
    src1 = env.r[rs1]
    src2 = env.r[rs2] if i == 0 else env.cst(simm13, 13).signextend(32)
    obj.operands = [(src1 + src2)]
    obj.type = type_cpu_state


# format 2
# ---------


@ispec("32[ 00 rd(5) 100 imm22(22) ]", mnemonic="sethi")
def sparc_sethi(obj, rd, imm22):
    src = env.cst(imm22, 22)
    dst = env.r[rd]
    obj.operands = [src, dst]
    obj.type = type_data_processing

@ispec("32[ 00 00000 100 0000000000000000000000 ]", mnemonic="nop")
def sparc_nop(obj):
    obj.type = type_data_processing


@ispec("32[ 00 a .cond(4) 010 disp22(22) ]", mnemonic="b")
@ispec("32[ 00 a .cond(4) 110 disp22(22) ]", mnemonic="fb")
@ispec("32[ 00 a .cond(4) 111 disp22(22) ]", mnemonic="cb")
def sparc_Bicc(obj, a, disp22):
    obj.operands = [env.cst(disp22, 22).signextend(32)]
    obj.misc["delayed"] = True
    obj.misc["annul"] = a == 1
    obj.type = type_control_flow


@ispec("32[ 00 ----- 000 const22(22) ]", mnemonic="unimp")
def sparc_unimp(obj, const22):
    obj.operands = [env.cst(const22, 22)]
    obj.type = type_undefined


# format 1
# ---------


@ispec("32[ 01 disp30(30) ]", mnemonic="call")
def sparc_call(obj, disp30):
    obj.operands = [env.cst(disp30, 30).signextend(32)]
    obj.misc["delayed"] = True
    obj.type = type_control_flow


#####


@ispec("32[ 10 rd(5) 110100 rs1(5) 011000100 rs2(5) ]", mnemonic="fitos")
@ispec("32[ 10 rd(5) 110100 rs1(5) 011001000 rs2(5) ]", mnemonic="fitod")
@ispec("32[ 10 rd(5) 110100 rs1(5) 011001100 rs2(5) ]", mnemonic="fitoq")
@ispec("32[ 10 rd(5) 110100 rs1(5) 011010001 rs2(5) ]", mnemonic="fstoi")
@ispec("32[ 10 rd(5) 110100 rs1(5) 011010010 rs2(5) ]", mnemonic="fdtoi")
@ispec("32[ 10 rd(5) 110100 rs1(5) 011010011 rs2(5) ]", mnemonic="fqtoi")
@ispec("32[ 10 rd(5) 110100 rs1(5) 011001001 rs2(5) ]", mnemonic="fstod")
@ispec("32[ 10 rd(5) 110100 rs1(5) 011001101 rs2(5) ]", mnemonic="fstoq")
@ispec("32[ 10 rd(5) 110100 rs1(5) 011000110 rs2(5) ]", mnemonic="fdtos")
@ispec("32[ 10 rd(5) 110100 rs1(5) 011001110 rs2(5) ]", mnemonic="fdtoq")
@ispec("32[ 10 rd(5) 110100 rs1(5) 011000111 rs2(5) ]", mnemonic="fqtos")
@ispec("32[ 10 rd(5) 110100 rs1(5) 011001011 rs2(5) ]", mnemonic="fqtod")
@ispec("32[ 10 rd(5) 110100 rs1(5) 000000001 rs2(5) ]", mnemonic="fmovs")
@ispec("32[ 10 rd(5) 110100 rs1(5) 000000101 rs2(5) ]", mnemonic="fnegs")
@ispec("32[ 10 rd(5) 110100 rs1(5) 000001001 rs2(5) ]", mnemonic="fabss")
@ispec("32[ 10 rd(5) 110100 rs1(5) 000101001 rs2(5) ]", mnemonic="fsqrts")
@ispec("32[ 10 rd(5) 110100 rs1(5) 000101010 rs2(5) ]", mnemonic="fsqrtd")
@ispec("32[ 10 rd(5) 110100 rs1(5) 000101011 rs2(5) ]", mnemonic="fsqrtq")
def sparc_FPop1_group1(obj, rd, rs1, rs2):
    src = env.f[rs2]
    dst = env.f[rd]
    obj.operands = [src, dst]
    obj.type = type_other


@ispec("32[ 10 rd(5) 110100 rs1(5) 001000001 rs2(5) ]", mnemonic="fadds")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001000010 rs2(5) ]", mnemonic="faddd")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001000011 rs2(5) ]", mnemonic="faddq")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001000101 rs2(5) ]", mnemonic="fsubs")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001000110 rs2(5) ]", mnemonic="fsubd")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001000111 rs2(5) ]", mnemonic="fsubq")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001001001 rs2(5) ]", mnemonic="fmuls")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001001010 rs2(5) ]", mnemonic="fmuld")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001001011 rs2(5) ]", mnemonic="fmulq")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001101001 rs2(5) ]", mnemonic="fsmuld")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001101110 rs2(5) ]", mnemonic="fdmulq")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001001101 rs2(5) ]", mnemonic="fdivs")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001001110 rs2(5) ]", mnemonic="fdivd")
@ispec("32[ 10 rd(5) 110100 rs1(5) 001001111 rs2(5) ]", mnemonic="fdivq")
def sparc_FPop1_group2(obj, rd, rs1, rs2):
    src1 = env.f[rs1]
    src2 = env.f[rs2]
    dst = env.f[rd]
    obj.operands = [src1, src2, dst]
    obj.type = type_other


@ispec("32[ 10 rd(5) 110101 rs1(5) 001010001 rs2(5) ]", mnemonic="fcmps")
@ispec("32[ 10 rd(5) 110101 rs1(5) 001010010 rs2(5) ]", mnemonic="fcmpd")
@ispec("32[ 10 rd(5) 110101 rs1(5) 001010011 rs2(5) ]", mnemonic="fcmpq")
@ispec("32[ 10 rd(5) 110101 rs1(5) 001010101 rs2(5) ]", mnemonic="fcmpes")
@ispec("32[ 10 rd(5) 110101 rs1(5) 001010110 rs2(5) ]", mnemonic="fcmped")
@ispec("32[ 10 rd(5) 110101 rs1(5) 001010111 rs2(5) ]", mnemonic="fcmpeq")
def sparc_FPop2_(obj, rd, rs1, rs2):
    src1 = env.f[rs1]
    src2 = env.f[rs2]
    obj.operands = [src1, src2]
    obj.type = type_other


@ispec("32[ 10 rd(5) 110110 rs1(5) opc(9) rs2(5) ]", mnemonic="cpop1")
@ispec("32[ 10 rd(5) 110111 rs1(5) opc(9) rs2(5) ]", mnemonic="cpop2")
def sparc_CPop(obj, rd, rs1, opc, rs2):
    obj.operands = [opc, env.c[rs1], env.c[rs2], env.c[rd]]
    obj.type = type_other
