# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2018 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

# ref: The SH-2A / SH-2A FPU Software Manual

from amoco.arch.superh.sh2 import env

from amoco.arch.core import *

# -------------------------------------------------------
# sh-2 decoders
# -------------------------------------------------------

ISPECS = []

# data transfer instructions:


@ispec("16<[ 1110 n(4) i(8) ]", mnemonic="MOV")
@ispec("16<[ 0111 n(4) i(8) ]", mnemonic="ADD")
def sh2_data_transfer(obj, n, i):
    Rn = env.R[n]
    imm8 = env.cst(i, 8).signextend(32)
    obj.operands = [imm8, Rn]
    obj.type = type_data_processing


@ispec("16<[ 1001 n(4) d(8) ]", mnemonic="MOV", size=16)
@ispec("16<[ 1101 n(4) d(8) ]", mnemonic="MOV", size=32)
def sh2_data_transfer(obj, n, d):
    Rn = env.R[n]
    scale = obj.size // 8
    disp = env.cst(d * scale, 32)
    obj.operands = [env.mem(env.pc + disp, obj.size), Rn]
    obj.type = type_data_processing


@ispec("16<[ 0110 n(4) m(4) 0 0=a 11=sz(2) ]", mnemonic="MOV")
@ispec("16<[ 0010 n(4) m(4) 0   a    sz(2) ]", mnemonic="MOV")
def sh2_data_transfer(obj, n, m, a, sz):
    Rn = env.R[n]
    Rm = env.R[m]
    dst = Rn if sz == 3 else env.mem(Rn, 8 << sz)
    if sz < 3:
        obj.size = 8 << sz
    obj.operands = [Rm, dst]
    if a == 1:
        if sz == 3:
            raise InstructionError(obj)
        obj.misc["decr"] = (1,)
    obj.type = type_data_processing


@ispec("16<[ 0110 n(4) m(4) 0 a sz(2) ]", mnemonic="MOV")
def sh2_data_transfer(obj, n, m, a, sz):
    if sz == 3:
        raise InstructionError(obj)
    obj.size = 8 << sz
    Rn = env.R[n]
    Rm = env.R[m]
    src = env.mem(Rm, obj.size)
    obj.operands = [src, Rn]
    if a == 1:
        obj.misc["incr"] = (0,)
    obj.type = type_data_processing


@ispec("16<[ 1000 0000 n(4) d(4) ]", mnemonic="MOV", size=8)
@ispec("16<[ 1000 0001 n(4) d(4) ]", mnemonic="MOV", size=16)
def sh2_data_transfer(obj, n, d):
    Rn = env.R[n]
    scale = obj.size // 8
    disp = env.cst(d * scale, 32)
    obj.operands = [env.R[0], env.mem(Rn + disp, obj.size)]
    obj.type = type_data_processing


@ispec("16<[ 0001 n(4) m(4) d(4) ]", mnemonic="MOV", size=32)
def sh2_data_transfer(obj, n, m, d):
    Rn = env.R[n]
    Rm = env.R[m]
    scale = obj.size // 8
    disp = env.cst(d * scale, 32)
    obj.operands = [Rm, env.mem(Rn + disp, obj.size)]
    obj.type = type_data_processing


@ispec("16<[ 1000 0100 m(4) d(4) ]", mnemonic="MOV", size=8)
@ispec("16<[ 1000 0101 m(4) d(4) ]", mnemonic="MOV", size=16)
def sh2_data_transfer(obj, m, d):
    Rm = env.R[m]
    scale = obj.size // 8
    disp = env.cst(d * scale, 32)
    obj.operands = [env.mem(Rm + disp, obj.size), env.R[0]]
    obj.type = type_data_processing


@ispec("16<[ 0101 n(4) m(4) d(4) ]", mnemonic="MOV", size=32)
def sh2_data_transfer(obj, n, m, d):
    Rn = env.R[n]
    Rm = env.R[m]
    scale = obj.size // 8
    disp = env.cst(d * scale, 32)
    obj.operands = [env.mem(Rm + disp, obj.size), Rn]
    obj.type = type_data_processing


@ispec("16<[ 0000 n(4) m(4) 01 sz(2) ]", mnemonic="MOV")
def sh2_data_transfer(obj, n, m, sz):
    if sz == 3:
        raise InstructionError(obj)
    Rn = env.R[n]
    Rm = env.R[m]
    dst = env.mem(env.R[0] + Rn, 8 << sz)
    obj.size = 8 << sz
    obj.operands = [Rm, dst]
    obj.type = type_data_processing


@ispec("16<[ 0000 n(4) m(4) 11 sz(2) ]", mnemonic="MOV")
def sh2_data_transfer(obj, n, m, sz):
    if sz == 3:
        raise InstructionError(obj)
    Rn = env.R[n]
    Rm = env.R[m]
    src = env.mem(env.R[0] + Rm, 8 << sz)
    obj.operands = [src, Rn]
    obj.type = type_data_processing


@ispec("16<[ 1100 00 sz(2) d(8) ]", mnemonic="MOV")
def sh2_data_transfer(obj, sz, d):
    if sz == 3:
        raise InstructionError(obj)
    R0 = env.R[0]
    adr = env.GBR
    scale = 1 << sz
    disp = env.cst(d * scale, 32)
    dst = env.mem(adr + disp, 8 << sz)
    obj.size = 8 << sz
    obj.operands = [R0, dst]
    obj.type = type_data_processing


@ispec("16<[ 1100 01    sz(2) d(8) ]", mnemonic="MOV")
@ispec("16<[ 1100 01 11=sz(2) d(8) ]", mnemonic="MOVA")
def sh2_data_transfer(obj, sz, d):
    R0 = env.R[0]
    adr = env.pc if sz == 3 else env.GBR
    scale = 1 << sz
    disp = env.cst(d * scale, 32)
    src = env.mem(adr + disp, 8 << sz)
    obj.operands = [src, R0]
    obj.type = type_data_processing


@ispec("16<[ 0100 n(4) 10 sz(2) 1011 ]", mnemonic="MOV")
def sh2_data_transfer(obj, n, sz):
    if sz == 3:
        raise InstructionError(obj)
    R0 = env.R[0]
    Rn = env.R[n]
    dst = env.mem(Rn, 8 << sz)
    obj.size = 8 << sz
    obj.operands = [R0, dst]
    obj.misc["incr"] = (1,)
    obj.type = type_data_processing


@ispec("16<[ 0100 m(4) 11 sz(2) 1011 ]", mnemonic="MOV")
def sh2_data_transfer(obj, m, sz):
    if sz == 3:
        raise InstructionError(obj)
    R0 = env.R[0]
    Rm = env.R[m]
    src = env.mem(Rm, 8 << sz)
    obj.size = 8 << sz
    obj.operands = [src, R0]
    obj.misc["decr"] = (0,)
    obj.type = type_data_processing


@ispec("32<[ 0011 n(4) m(4) 0001 00 sz(2) d(12) ]", mnemonic="MOV")
def sh2_data_transfer(obj, n, m, sz, d):
    if sz == 3:
        raise InstructionError(obj)
    Rn = env.R[n]
    Rm = env.R[m]
    scale = 1 << sz
    disp = env.cst(d * scale, 32)
    dst = env.mem(Rn + disp, 8 << sz)
    obj.size = 8 << sz
    obj.operands = [Rm, dst]
    obj.type = type_data_processing


@ispec("32<[ 0011 n(4) m(4) 0001 01 sz(2) d(12) ]", mnemonic="MOV")
def sh2_data_transfer(obj, n, m, sz, d):
    if sz == 3:
        raise InstructionError(obj)
    Rn = env.R[n]
    Rm = env.R[m]
    scale = 1 << sz
    disp = env.cst(d * scale, 32)
    src = env.mem(Rm + disp, 8 << sz)
    obj.size = 8 << sz
    obj.operands = [src, Rn]
    obj.type = type_data_processing


@ispec("32<[ 0000 n(4) ~i4(4) 0000 ~i16(16) ]", mnemonic="MOVI20")
@ispec("32<[ 0000 n(4) ~i4(4) 0001 ~i16(16) ]", mnemonic="MOVI20S")
def sh2_data_transfer(obj, n, i4, i16):
    Rn = env.R[n]
    imm20 = env.cst((i16 // i4).int(-1), 20)
    if obj.mnemonic == "MOVI20S":
        imm20 = imm20 << 8
    imm20 = imm20.signextend(32)
    obj.operands = [imm20, Rn]
    obj.type = type_data_processing


@ispec("16<[ 0100 m(4) 1111 0001 ]", mnemonic="MOVML")
@ispec("16<[ 0100 m(4) 1111 0000 ]", mnemonic="MOVMU")
def sh2_data_transfer(obj, m):
    Rm = env.R[m] if m != 15 else env.PR
    obj.m = m
    R15 = env.R[15]
    obj.operands = [Rm, env.mem(R15, 32)]
    obj.misc["decr"] = (1,)
    obj.type = type_data_processing


@ispec("16<[ 0100 n(4) 1111 0101 ]", mnemonic="MOVML")
@ispec("16<[ 0100 n(4) 1111 0100 ]", mnemonic="MOVMU")
def sh2_data_transfer(obj, n):
    Rn = env.R[n] if n != 15 else env.PR
    R15 = env.R[15]
    obj.operands = [env.mem(R15, 32), Rn]
    obj.misc["incr"] = (0,)
    obj.type = type_data_processing


@ispec("16<[ 0000 n(4) 0011 1001 ]", mnemonic="MOVRT")
@ispec("16<[ 0000 n(4) 0010 1001 ]", mnemonic="MOVT")
@ispec("16<[ 0100 n(4) 0001 0101 ]", mnemonic="CMP", cond="PL")
@ispec("16<[ 0100 n(4) 0001 0001 ]", mnemonic="CMP", cond="PZ")
@ispec("16<[ 0100 n(4) 1001 0001 ]", mnemonic="CLIPS", size=8)
@ispec("16<[ 0100 n(4) 1001 0101 ]", mnemonic="CLIPS", size=16)
@ispec("16<[ 0100 n(4) 1000 0001 ]", mnemonic="CLIPU", size=8)
@ispec("16<[ 0100 n(4) 1000 0101 ]", mnemonic="CLIPU", size=16)
@ispec("16<[ 0100 n(4) 0001 0000 ]", mnemonic="DT")
@ispec("16<[ 0100 n(4) 0000 0100 ]", mnemonic="ROTL")
@ispec("16<[ 0100 n(4) 0000 0101 ]", mnemonic="ROTR")
@ispec("16<[ 0100 n(4) 0010 0100 ]", mnemonic="ROTCL")
@ispec("16<[ 0100 n(4) 0010 0101 ]", mnemonic="ROTCR")
@ispec("16<[ 0100 n(4) 0010 0000 ]", mnemonic="SHAL")
@ispec("16<[ 0100 n(4) 0010 0001 ]", mnemonic="SHAR")
@ispec("16<[ 0100 n(4) 0000 0000 ]", mnemonic="SHLL")
@ispec("16<[ 0100 n(4) 0000 0001 ]", mnemonic="SHLR")
@ispec("16<[ 0100 n(4) 0000 1000 ]", mnemonic="SHLL2")
@ispec("16<[ 0100 n(4) 0000 1001 ]", mnemonic="SHLR2")
@ispec("16<[ 0100 n(4) 0001 1000 ]", mnemonic="SHLL8")
@ispec("16<[ 0100 n(4) 0001 1001 ]", mnemonic="SHLR8")
@ispec("16<[ 0100 n(4) 0010 1000 ]", mnemonic="SHLL16")
@ispec("16<[ 0100 n(4) 0010 1001 ]", mnemonic="SHLR16")
def sh2_rn(obj, n):
    Rn = env.R[n]
    obj.operands = [Rn]
    obj.type = type_data_processing


@ispec("32<[ 0011 n(4) m(4) 0001 10 sz(2) d(12) ]", mnemonic="MOVU")
def sh2_data_transfer(obj, n, m, sz, d):
    if sz > 1:
        raise InstructionError(obj)
    Rn = env.R[n]
    Rm = env.R[m]
    scale = 1 << sz
    disp = env.cst(d * scale, 32)
    src = env.mem(Rm + disp, 8 << sz)
    obj.operands = [src, Rn]
    obj.type = type_data_processing


@ispec("16<[ 0000 0000 0110 1000 ]", mnemonic="MOVT")
@ispec("16<[ 0000 0000 0001 1001 ]", mnemonic="DIV0U")
@ispec("16<[ 1111 0011 1111 1101 ]", mnemonic="FSCHG")
def sh2_default(obj):
    obj.operands = []
    obj.type = type_data_processing


@ispec("16<[ 0000 n(4) 1000 0011 ]", mnemonic="PREF")
@ispec("16<[ 0100 n(4) 0001 1011 ]", mnemonic="TAS", size=8)
def sh2_data_transfer(obj, n):
    Rn = env.R[n]
    obj.operands = [env.mem(Rn, 32)]
    obj.type = type_data_processing


@ispec("16<[ 0110 n(4) m(4) 10 sz(2) ]", mnemonic="SWAP")
def sh2_data_transfer(obj, n, m, sz):
    if sz > 1:
        raise InstructionError(obj)
    Rn = env.R[n]
    Rm = env.R[m]
    obj.operands = [Rm, Rn]
    obj.misc["sz"] = sz
    obj.type = type_data_processing


@ispec("16<[ 0010 n(4) m(4) 1101 ]", mnemonic="XTRCT")
@ispec("16<[ 0010 n(4) m(4) 1100 ]", mnemonic="CMP", cond="STR")
@ispec("16<[ 0011 n(4) m(4) 0100 ]", mnemonic="DIV1")
@ispec("16<[ 0010 n(4) m(4) 0111 ]", mnemonic="DIV0S")
@ispec("16<[ 0110 n(4) m(4) 1110 ]", mnemonic="EXTS", size=8)
@ispec("16<[ 0110 n(4) m(4) 1111 ]", mnemonic="EXTS", size=16)
@ispec("16<[ 0110 n(4) m(4) 1100 ]", mnemonic="EXTU", size=8)
@ispec("16<[ 0110 n(4) m(4) 1101 ]", mnemonic="EXTU", size=16)
@ispec("16<[ 0000 n(4) m(4) 0111 ]", mnemonic="MUL", size=32)
@ispec("16<[ 0010 n(4) m(4) 1111 ]", mnemonic="MULS", size=8)
@ispec("16<[ 0010 n(4) m(4) 1110 ]", mnemonic="MULU", size=16)
@ispec("16<[ 0110 n(4) m(4) 1011 ]", mnemonic="NEG")
@ispec("16<[ 0110 n(4) m(4) 1010 ]", mnemonic="NEGC")
@ispec("16<[ 0010 n(4) m(4) 1001 ]", mnemonic="AND")
@ispec("16<[ 0110 n(4) m(4) 0111 ]", mnemonic="NOT")
@ispec("16<[ 0010 n(4) m(4) 1011 ]", mnemonic="OR")
@ispec("16<[ 0010 n(4) m(4) 1000 ]", mnemonic="TST")
@ispec("16<[ 0010 n(4) m(4) 1010 ]", mnemonic="XOR")
@ispec("16<[ 0100 n(4) m(4) 1100 ]", mnemonic="SHAD")
@ispec("16<[ 0100 n(4) m(4) 1101 ]", mnemonic="SHLD")
@ispec("16<[ 0011 n(4) m(4) 1100 ]", mnemonic="ADD")
@ispec("16<[ 0011 n(4) m(4) 1110 ]", mnemonic="ADDC")
@ispec("16<[ 0011 n(4) m(4) 1111 ]", mnemonic="ADDV")
@ispec("16<[ 0011 n(4) m(4) 0000 ]", mnemonic="CMP", cond="EQ")
@ispec("16<[ 0011 n(4) m(4) 0010 ]", mnemonic="CMP", cond="HS")
@ispec("16<[ 0011 n(4) m(4) 0011 ]", mnemonic="CMP", cond="GE")
@ispec("16<[ 0011 n(4) m(4) 0110 ]", mnemonic="CMP", cond="HI")
@ispec("16<[ 0011 n(4) m(4) 0111 ]", mnemonic="CMP", cond="GT")
@ispec("16<[ 0011 n(4) m(4) 1101 ]", mnemonic="DMULS")
@ispec("16<[ 0011 n(4) m(4) 0101 ]", mnemonic="DMULU")
@ispec("16<[ 0011 n(4) m(4) 1000 ]", mnemonic="SUB")
@ispec("16<[ 0011 n(4) m(4) 1010 ]", mnemonic="SUBC")
@ispec("16<[ 0011 n(4) m(4) 1011 ]", mnemonic="SUBV")
def sh2_default(obj, n, m):
    Rn = env.R[n]
    Rm = env.R[m]
    obj.operands = [Rm, Rn]
    obj.type = type_data_processing


@ispec("16<[ 1000 1000 i(8) ]", mnemonic="CMP", cond="EQ")
def sh2_default(obj, i):
    R0 = env.R[0]
    imm8 = env.cst(i, 8).signextend(32)
    obj.operands = [imm8, R0]
    obj.type = type_data_processing


@ispec("16<[ 1100 1001 i(8) ]", mnemonic="AND")
@ispec("16<[ 1100 1011 i(8) ]", mnemonic="OR")
@ispec("16<[ 1100 1010 i(8) ]", mnemonic="XOR")
@ispec("16<[ 1100 1000 i(8) ]", mnemonic="TST")
def sh2_default(obj, i):
    R0 = env.R[0]
    imm8 = env.cst(i, 8).zeroextend(32)
    obj.operands = [imm8, R0]
    obj.type = type_data_processing


@ispec("16<[ 0100 n(4) 1001 0100 ]", mnemonic="DIVS")
@ispec("16<[ 0100 n(4) 1000 0100 ]", mnemonic="DIVU")
@ispec("16<[ 0100 n(4) 1000 0000 ]", mnemonic="MULR")
def sh2_default(obj, n):
    Rn = env.R[n]
    obj.operands = [env.R[0], Rn]
    obj.type = type_data_processing


@ispec("16<[ 0000 n(4) m(4) 1111 ]", mnemonic="MAC", size=32)
@ispec("16<[ 0100 n(4) m(4) 1111 ]", mnemonic="MAC", size=16)
def sh2_default(obj, n, m):
    Rn = env.R[n]
    Rm = env.R[m]
    obj.misc["incr"] = (0, 1)
    obj.operands = [env.mem(Rm, obj.size), env.mem(Rn, obj.size)]
    obj.type = type_data_processing


@ispec("16<[ 1100 1101 i(8) ]", mnemonic="AND")
@ispec("16<[ 1100 1111 i(8) ]", mnemonic="OR")
@ispec("16<[ 1100 1100 i(8) ]", mnemonic="TST")
@ispec("16<[ 1100 1110 i(8) ]", mnemonic="XOR")
def sh2_default(obj, i):
    R0 = env.R[0]
    imm8 = env.cst(i, 8)
    obj.operands = [imm8, env.mem(R0 + env.GBR, 8)]
    obj.type = type_data_processing


# Branch instructions


@ispec("16<[ 1000 1011 d(8) ]", mnemonic="BF")
@ispec("16<[ 1000 1111 d(8) ]", mnemonic="BF", cond="S")
@ispec("16<[ 1000 1001 d(8) ]", mnemonic="BT")
@ispec("16<[ 1000 1101 d(8) ]", mnemonic="BT", cond="S")
def sh2_branch(obj, d):
    offset = env.cst(d, 8).signextend(32)
    obj.operands = [offset * 2]
    if hasattr(obj, "cond"):
        obj.misc["delayed"] = True
    obj.type = type_control_flow


@ispec("16<[ 1010 d(12) ]", mnemonic="BRA")
@ispec("16<[ 1011 d(12) ]", mnemonic="BSR")
def sh2_branch(obj, d):
    R0 = env.R[0]
    offset = env.cst(d, 12).signextend(32)
    obj.operands = [offset * 2]
    obj.misc["delayed"] = True
    obj.type = type_control_flow


@ispec("16<[ 0000 m(4) 00100011 ]", mnemonic="BRAF")
@ispec("16<[ 0000 m(4) 00000011 ]", mnemonic="BSRF")
@ispec("16<[ 0000 m(4) 01111011 ]", mnemonic="RTV", cond="N")
def sh2_branch(obj, m):
    Rm = env.R[m]
    obj.operands = [Rm]
    if not hasattr(obj, "cond"):
        obj.misc["delayed"] = True
    obj.type = type_control_flow


@ispec("16<[ 0100 m(4) 00101011 ]", mnemonic="JMP")
@ispec("16<[ 0100 m(4) 00001011 ]", mnemonic="JSR")
@ispec("16<[ 0100 m(4) 01001011 ]", mnemonic="JSR", cond="N")
def sh2_branch(obj, m):
    Rm = env.R[m]
    obj.operands = [Rm]
    if not hasattr(obj, "cond"):
        obj.misc["delayed"] = True
    obj.type = type_control_flow


@ispec("16<[ 1000 0011 d(8) ]", mnemonic="JSR", cond="N")
def sh2_jsr_nn(obj, d):
    imm = env.cst(d, 32)
    p = env.mem(env.TBR + imm, 32)
    obj.operands = [env.mem(p, 32)]
    obj.type = type_control_flow


@ispec("16<[ {00} 0000 1011 ]", mnemonic="RTS")
@ispec("16<[ {00} 0110 1011 ]", mnemonic="RTS", cond="N")
def sh2_default(obj):
    obj.operands = []
    obj.type = type_control_flow


# System control instructions


@ispec("16<[ {00} 0000 1000 ]", mnemonic="CLRT")
@ispec("16<[ {00} 0010 1000 ]", mnemonic="CLRMAC")
@ispec("16<[ {00} 0110 1000 ]", mnemonic="NOTT")
@ispec("16<[ {00} 0000 1001 ]", mnemonic="NOP")
@ispec("16<[ {00} 0101 1011 ]", mnemonic="RESBANK")
@ispec("16<[ {00} 0010 1011 ]", mnemonic="RTE")
@ispec("16<[ {00} 0001 1000 ]", mnemonic="SETT")
@ispec("16<[ {00} 0001 1011 ]", mnemonic="SLEEP")
def sh2_default(obj):
    obj.operands = []
    obj.type = type_other


@ispec("16<[ 0100 m(4) 11100101 ]", mnemonic="LDBANK")
def sh2_default(obj, m):
    Rm = env.R[m]
    obj.operands = [env.mem(Rm, 32), env.R[0]]
    obj.type = type_other


@ispec("16<[ 0100 m(4) 00001110 ]", mnemonic="LDC", _op2=env.SR)
@ispec("16<[ 0100 m(4) 01001010 ]", mnemonic="LDC", _op2=env.TBR)
@ispec("16<[ 0100 m(4) 00011110 ]", mnemonic="LDC", _op2=env.GBR)
@ispec("16<[ 0100 m(4) 00101110 ]", mnemonic="LDC", _op2=env.VBR)
@ispec("16<[ 0100 m(4) 00001010 ]", mnemonic="LDS", _op2=env.MACH)
@ispec("16<[ 0100 m(4) 00011010 ]", mnemonic="LDS", _op2=env.MACL)
@ispec("16<[ 0100 m(4) 00101010 ]", mnemonic="LDS", _op2=env.PR)
@ispec("16<[ 0100 m(4) 01101010 ]", mnemonic="LDS", _op2=env.FPSCR)
@ispec("16<[ 0100 m(4) 01011010 ]", mnemonic="LDS", _op2=env.FPUL)
def sh2_default(obj, m, _op2):
    Rm = env.R[m]
    obj.operands = [Rm, _op2]
    obj.type = type_other


@ispec("16<[ 0100 m(4) 00000111 ]", mnemonic="LDC", size=32, _op2=env.SR)
@ispec("16<[ 0100 m(4) 00010111 ]", mnemonic="LDC", size=32, _op2=env.GBR)
@ispec("16<[ 0100 m(4) 00100111 ]", mnemonic="LDC", size=32, _op2=env.VBR)
@ispec("16<[ 0100 m(4) 00000110 ]", mnemonic="LDS", size=32, _op2=env.MACH)
@ispec("16<[ 0100 m(4) 00010110 ]", mnemonic="LDS", size=32, _op2=env.MACL)
@ispec("16<[ 0100 m(4) 00100110 ]", mnemonic="LDS", size=32, _op2=env.PR)
@ispec("16<[ 0100 m(4) 01100110 ]", mnemonic="LDS", size=32, _op2=env.FPSCR)
@ispec("16<[ 0100 m(4) 01010110 ]", mnemonic="LDS", size=32, _op2=env.FPUL)
def sh2_default(obj, m, _op2):
    Rm = env.R[m]
    obj.operands = [env.mem(Rm, 32), _op2]
    obj.misc["incr"] = (0,)
    obj.type = type_other


@ispec("16<[ 0100 n(4) 11100101 ]", mnemonic="STBANK")
def sh2_default(obj, n):
    Rn = env.R[n]
    obj.operands = [env.R[0], env.mem(n, 32)]
    obj.type = type_other


@ispec("16<[ 0000 n(4) 00000010 ]", mnemonic="STC", _op2=env.SR)
@ispec("16<[ 0000 n(4) 01001010 ]", mnemonic="STC", _op2=env.TBR)
@ispec("16<[ 0000 n(4) 00010010 ]", mnemonic="STC", _op2=env.GBR)
@ispec("16<[ 0000 n(4) 00100010 ]", mnemonic="STC", _op2=env.VBR)
@ispec("16<[ 0000 n(4) 00001010 ]", mnemonic="STS", _op2=env.MACH)
@ispec("16<[ 0000 n(4) 00011010 ]", mnemonic="STS", _op2=env.MACL)
@ispec("16<[ 0000 n(4) 00101010 ]", mnemonic="STS", _op2=env.PR)
@ispec("16<[ 0000 n(4) 01101010 ]", mnemonic="STS", _op2=env.FPSCR)
@ispec("16<[ 0000 n(4) 01011010 ]", mnemonic="STS", _op2=env.FPUL)
def sh2_default(obj, n, _op2):
    Rn = env.R[n]
    obj.operands = [_op2, Rn]
    obj.type = type_other


@ispec("16<[ 0100 n(4) 00000111 ]", mnemonic="STC", size=32, _op2=env.SR)
@ispec("16<[ 0100 n(4) 00010111 ]", mnemonic="STC", size=32, _op2=env.GBR)
@ispec("16<[ 0100 n(4) 00100111 ]", mnemonic="STC", size=32, _op2=env.VBR)
@ispec("16<[ 0100 n(4) 00000110 ]", mnemonic="STS", size=32, _op2=env.MACH)
@ispec("16<[ 0100 n(4) 00010110 ]", mnemonic="STS", size=32, _op2=env.MACL)
@ispec("16<[ 0100 n(4) 00100110 ]", mnemonic="STS", size=32, _op2=env.PR)
@ispec("16<[ 0100 n(4) 01100010 ]", mnemonic="STS", size=32, _op2=env.FPSCR)
@ispec("16<[ 0100 n(4) 01010010 ]", mnemonic="STS", size=32, _op2=env.FPUL)
def sh2_default(obj, n, _op2):
    Rn = env.R[n]
    obj.operands = [_op2, env.mem(Rn, 32)]
    obj.misc["decr"] = (1,)
    obj.type = type_other


@ispec("16<[ 11000011 i(8) ]", mnemonic="TRAPA")
def sh2_default(obj, i):
    imm8 = env.cst(i, 8)
    obj.operands = [imm8]
    obj.type = type_other


# bit manipulation instructions


@ispec("32<[ 0011 n(4) 0 i(3) 1001 0100 d(12) ]", mnemonic="BAND", size=8)
@ispec("32<[ 0011 n(4) 0 i(3) 1001 1100 d(12) ]", mnemonic="BANDNOT", size=8)
@ispec("32<[ 0011 n(4) 0 i(3) 1001 0000 d(12) ]", mnemonic="BCLR", size=8)
@ispec("32<[ 0011 n(4) 0 i(3) 1001 0011 d(12) ]", mnemonic="BLD", size=8)
@ispec("32<[ 0011 n(4) 0 i(3) 1001 1011 d(12) ]", mnemonic="BLDNOT", size=8)
@ispec("32<[ 0011 n(4) 0 i(3) 1001 0101 d(12) ]", mnemonic="BOR", size=8)
@ispec("32<[ 0011 n(4) 0 i(3) 1001 1101 d(12) ]", mnemonic="BORNOT", size=8)
@ispec("32<[ 0011 n(4) 0 i(3) 1001 0001 d(12) ]", mnemonic="BSET", size=8)
@ispec("32<[ 0011 n(4) 0 i(3) 1001 0010 d(12) ]", mnemonic="BST", size=8)
@ispec("32<[ 0011 n(4) 0 i(3) 1001 0110 d(12) ]", mnemonic="BXOR", size=8)
def sh2_default(obj, n, i, d):
    Rn = env.R[n]
    imm3 = env.cst(i, 3)
    disp = env.cst(d, 12).zeroextend(32)
    dst = env.mem(disp + Rn, obj.size)
    obj.operands = [imm3, dst]
    obj.type = type_data_processing


@ispec("16<[ 10000110 n(4) 0 i(3) ]", mnemonic="BCLR")
@ispec("16<[ 10000111 n(4) 1 i(3) ]", mnemonic="BLD")
@ispec("16<[ 10000110 n(4) 1 i(3) ]", mnemonic="BSET")
@ispec("16<[ 10000111 n(4) 0 i(3) ]", mnemonic="BST")
def sh2_default(obj, n, i):
    Rn = env.R[n]
    imm3 = env.cst(i, 3)
    obj.operands = [imm3, Rn]
    obj.type = type_data_processing


# floating point instructions


@ispec("16<[ 1111 n(4) 01011101 ]", mnemonic="FABS")
@ispec("16<[ 1111 n(4) 10001101 ]", mnemonic="FLDI0")
@ispec("16<[ 1111 n(4) 10011101 ]", mnemonic="FLDI1")
@ispec("16<[ 1111 n(4) 01001101 ]", mnemonic="FNEG")
@ispec("16<[ 1111 n(4) 01101101 ]", mnemonic="FSQRT")
def sh2_float(obj, n):
    FRn = env.FR[n]
    obj.operands = [FRn]
    obj.type = type_data_processing


@ispec("16<[ 1111 n(4) m(4) 0000 ]", mnemonic="FADD")
@ispec("16<[ 1111 n(4) m(4) 0100 ]", mnemonic="FCMP", cond="EQ")
@ispec("16<[ 1111 n(4) m(4) 0101 ]", mnemonic="FCMP", cond="GT")
@ispec("16<[ 1111 n(4) m(4) 0011 ]", mnemonic="FDIV")
@ispec("16<[ 1111 n(4) m(4) 1100 ]", mnemonic="FMOV")
@ispec("16<[ 1111 n(4) m(4) 0010 ]", mnemonic="FMUL")
@ispec("16<[ 1111 n(4) m(4) 0001 ]", mnemonic="FSUB")
def sh2_float(obj, m, n):
    FRn = env.FR[n]
    FRm = env.FR[m]
    obj.operands = [FRm, FRn]
    obj.type = type_data_processing


@ispec("16<[ 1111 m(3) 010111101 ]", mnemonic="FCNVDS")
def sh2_default(obj, m):
    DRm = env.DR[m]
    obj.operands = [DRm, env.FPUL]
    obj.type = type_data_processing


@ispec("16<[ 1111 n(3) 010101101 ]", mnemonic="FCNVSD")
def sh2_float(obj, n):
    DRn = env.DR[n]
    obj.operands = [env.FPUL, DRn]
    obj.type = type_data_processing


@ispec("16<[ 1111 m(4) 00011101 ]", mnemonic="FLDS")
@ispec("16<[ 1111 m(4) 00111101 ]", mnemonic="FTRC")
def sh2_float(obj, m):
    FRm = env.FR[m]
    obj.operands = [FRm, env.FPUL]
    obj.type = type_data_processing


@ispec("16<[ 1111 n(4) 00101101 ]", mnemonic="FLOAT")
@ispec("16<[ 1111 n(4) 00001101 ]", mnemonic="FSTS")
def sh2_float(obj, n):
    FRn = env.FR[n]
    obj.operands = [env.FPUL, FRn]
    obj.type = type_data_processing


@ispec("16<[ 1111 n(4) m(4) 1100 ]", mnemonic="FMAC")
def sh2_float(obj, m, n):
    FRn = env.FR[n]
    FRm = env.FR[m]
    obj.operands = [env.FR[0], FRm, FRn]
    obj.type = type_data_processing


@ispec("16<[ 1111 n(4) m(4) 0110 ]", mnemonic="FMOV", cond="S")
def sh2_float(obj, m, n):
    FRn = env.FR[n]
    R0 = env.R[0]
    Rm = env.R[m]
    obj.operands = [env.mem(R0 + Rm, 32), FRn]
    obj.type = type_data_processing


@ispec("16<[ 1111 n(4) m(4) 100i ]", mnemonic="FMOV", cond="S")
def sh2_float(obj, m, n, i):
    FRn = env.FR[n]
    Rm = env.R[m]
    obj.operands = [env.mem(Rm, 32), FRn]
    if i:
        obj.misc["incr"] = (0,)
    obj.type = type_data_processing


@ispec("32<[ 0011 n(4) m(4) 0001 0111 d(12) ]", mnemonic="FMOV", cond="S")
def sh2_float(obj, m, n, d):
    FRn = env.FR[n]
    Rm = env.R[m]
    disp = env.cst(d, 12).zeroextend(32) << 2
    obj.operands = [env.mem(Rm + disp, 32), FRn]
    obj.type = type_data_processing


@ispec("16<[ 1111 n(4) m(4) 0111 ]", mnemonic="FMOV", cond="S")
def sh2_float(obj, m, n):
    FRm = env.FR[m]
    R0 = env.R[0]
    Rn = env.R[n]
    obj.operands = [FRm, env.mem(R0 + Rn, 32)]
    obj.type = type_data_processing


@ispec("16<[ 1111 n(4) m(4) 100i ]", mnemonic="FMOV", cond="S")
def sh2_float(obj, m, n, i):
    FRm = env.FR[m]
    Rn = env.R[n]
    obj.operands = [FRm, env.mem(Rn, 32)]
    if i:
        obj.misc["decr"] = (1,)
    obj.type = type_data_processing


@ispec("32<[ 0011 n(4) m(4) 0001 0111 d(12) ]", mnemonic="FMOV", cond="S")
def sh2_float(obj, m, n, d):
    FRm = env.FR[m]
    Rn = env.R[n]
    disp = env.cst(d, 12).zeroextend(32) << 2
    obj.operands = [FRm, env.mem(Rn + disp, 32)]
    obj.type = type_data_processing
