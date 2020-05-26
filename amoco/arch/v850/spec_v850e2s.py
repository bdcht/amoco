# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2018 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")
from amoco.arch.core import *
from amoco.arch.v850 import env

ISPECS = []


def _chk_reg_null(obj, r):
    if r == 0:
        raise InstructionError(obj)


# reserved instructions:
@ispec("32<[0000000000000000 ----- 111111 1----]", mnemonic="RIE")
@ispec("16<[0000000001000000]", mnemonic="RIE")
@ispec("16<[0000000000000000]", mnemonic="NOP")
@ispec("16<[0000000000011101]", mnemonic="SYNCE")
@ispec("16<[0000000000011110]", mnemonic="SYNCM")
@ispec("16<[0000000000011111]", mnemonic="SYNCP")
def v850_rie(obj):
    obj.operands = []
    obj.type = type_system


# format I
@ispec("16<[ reg2(5) 001110 reg1(5) ]", mnemonic="ADD")
@ispec("16<[ reg2(5) 001010 reg1(5) ]", mnemonic="AND")
@ispec("16<[ reg2(5) 001111 reg1(5) ]", mnemonic="CMP")
@ispec("16<[ reg2(5) 000010 reg1(5) ]", mnemonic="DIVH", _chk=1 & 2)
@ispec("16<[ reg2(5) 000000 reg1(5) ]", mnemonic="MOV", _chk=2)
@ispec("16<[ reg2(5) 000111 reg1(5) ]", mnemonic="MULH", _chk=2)
@ispec("16<[ reg2(5) 000001 reg1(5) ]", mnemonic="NOT")
@ispec("16<[ reg2(5) 001000 reg1(5) ]", mnemonic="OR")
@ispec("16<[ reg2(5) 000110 reg1(5) ]", mnemonic="SATADD", _chk=2)
@ispec("16<[ reg2(5) 000101 reg1(5) ]", mnemonic="SATSUB", _chk=2)
@ispec("16<[ reg2(5) 000100 reg1(5) ]", mnemonic="SATSUBR", _chk=2)
@ispec("16<[ reg2(5) 001101 reg1(5) ]", mnemonic="SUB")
@ispec("16<[ reg2(5) 001100 reg1(5) ]", mnemonic="SUBR")
@ispec("16<[ reg2(5) 001011 reg1(5) ]", mnemonic="TST")
@ispec("16<[ reg2(5) 001001 reg1(5) ]", mnemonic="XOR")
def v850_reg_reg(obj, reg1, reg2, _chk=0):
    if _chk & 1:
        _chk_reg_null(obj, reg1)
    if _chk & 2:
        _chk_reg_null(obj, reg2)
    dst, src = env.R[reg2], env.R[reg1]
    obj.operands = [src, dst]
    obj.type = type_data_processing


@ispec("16<[ 0 v(4) 000010 00000 ]", mnemonic="FETRAP")
def v850_fetrap(obj, v):
    if v == 0:
        raise InstructionError(obj)
    vector = env.cst(v, 4)
    obj.operands = [vector]
    obj.type = type_system


@ispec("16<[ 00000  000011 reg1(5) ]", mnemonic="JMP")
@ispec("16<[ 00000  000010 reg1(5) ]", mnemonic="SWITCH")
def v850_jmp(obj, reg1):
    dst = env.R[reg1]
    obj.operands = [dst]
    obj.type = type_control_flow


@ispec("16<[ 00000  000101 reg1(5) ]", mnemonic="SXB")
@ispec("16<[ 00000  000111 reg1(5) ]", mnemonic="SXH")
@ispec("16<[ 00000  000100 reg1(5) ]", mnemonic="ZXB")
@ispec("16<[ 00000  000110 reg1(5) ]", mnemonic="ZXH")
def v850_extend(obj, reg1):
    dst = env.R[reg1]
    obj.operands = [dst]
    obj.type = type_data_processing


# format II
@ispec("16<[ reg2(5) 010010 imm(5) ]", mnemonic="ADD")
@ispec("16<[ reg2(5) 010011 imm(5) ]", mnemonic="CMP")
@ispec("16<[ reg2(5) 010000 imm(5) ]", mnemonic="MOV", _chk=2)
@ispec("16<[ reg2(5) 010111 imm(5) ]", mnemonic="MULH", _chk=2)
@ispec("16<[ reg2(5) 010101 imm(5) ]", mnemonic="SAR")
@ispec("16<[ reg2(5) 010001 imm(5) ]", mnemonic="SATADD", _chk=2)
@ispec("16<[ reg2(5) 010110 imm(5) ]", mnemonic="SHL")
@ispec("16<[ reg2(5) 010100 imm(5) ]", mnemonic="SHR")
def v850_imm_reg(obj, imm, reg2, _chk=0):
    if _chk & 2:
        _chk_reg_null(obj, reg2)
    dst = env.R[reg2]
    imm5 = env.cst(imm, 5).signextend(32)
    obj.operands = [imm5, dst]
    obj.type = type_data_processing


@ispec("16<[ 000000 1000 imm(6) ]", mnemonic="CALLT")
def v850_imm_reg(obj, imm):
    imm = env.cst(imm << 1, 32)
    obj.operands = [imm]
    obj.type = type_data_processing


# format III
@ispec("16<[ ~dhi(5) 0000 ~dlo(3) .cond(4) ]", mnemonic="B")
def v850_br_cond(obj, dhi, dlo):
    disp = (dlo // dhi).int()
    disp = env.cst(disp << 1, 9).signextend(32)
    obj.operands = [disp]
    obj.type = type_control_flow


# format IV
@ispec("16<[ reg2(5) 0110 disp(6)   d ]", mnemonic="SLDB", _size=8)
@ispec("16<[ reg2(5) 1000 disp(6)   d ]", mnemonic="SLDH", _size=16)
@ispec("16<[ reg2(5) 1000 disp(6) 0=d ]", mnemonic="SLDW", _size=32)
@ispec("16<[ reg2(5) 0111 disp(6)   d ]", mnemonic="SSTB", _size=8)
@ispec("16<[ reg2(5) 1001 disp(6)   d ]", mnemonic="SSTH", _size=16)
@ispec("16<[ reg2(5) 1010 disp(6) 1=d ]", mnemonic="SSTW", _size=32)
def v850_ld_st(obj, reg2, disp, d, _size):
    disp = disp << 1
    if _size < 32:
        disp += d
    if _size > 8:
        disp = disp << 1
    dst, src = env.R[reg2], env.mem(env.ep, _size, disp=disp)
    if obj.mnemonic.startswith("SST"):
        src, dst = dst, src
    obj.operands = [src, dst]
    obj.type = type_data_processing


@ispec("16<[ reg2(5) 0000110 disp(4) ]", mnemonic="SLDBU", _size=8)
@ispec("16<[ reg2(5) 0000111 disp(4) ]", mnemonic="SLDHU", _size=16)
def v850_ld_st(obj, reg2, disp, _size):
    if reg2 == 0:
        raise InstructionError(obj)
    if _size > 8:
        disp = disp << 1
    dst, src = env.R[reg2], env.mem(env.ep, _size, disp=disp)
    obj.operands = [dst, src]
    obj.type = type_data_processing


# format V
@ispec("32<[ ~dlo(15) 0       reg2(5) 11110 ~dhi(6) ]", mnemonic="JARL")
@ispec("32<[ ~dlo(15) 0 00000=reg2(5) 11110 ~dhi(6) ]", mnemonic="JR")
def v850_jmp(obj, dhi, reg2, dlo):
    disp = env.cst((dlo // dhi).int(), 22).signextend(32)
    obj.operands = [disp]
    if reg2 != 0:
        dst = env.R[reg2]
        obj.operands.append(dst)
    obj.type = type_control_flow


# format VI
@ispec("32<[ imm(16) reg2(5) 110000 reg1(5) ]", mnemonic="ADDI")
@ispec("32<[ imm(16) reg2(5) 110110 reg1(5) ]", mnemonic="ANDI")
@ispec("32<[ imm(16) reg2(5) 110001 reg1(5) ]", mnemonic="MOVEA", _chk=2)
@ispec("32<[ imm(16) reg2(5) 110010 reg1(5) ]", mnemonic="MOVHI", _chk=2)
@ispec("32<[ imm(16) reg2(5) 110111 reg1(5) ]", mnemonic="MULHI", _chk=2)
@ispec("32<[ imm(16) reg2(5) 110100 reg1(5) ]", mnemonic="ORI")
@ispec("32<[ imm(16) reg2(5) 110011 reg1(5) ]", mnemonic="SATSUBI", _chk=2)
@ispec("32<[ imm(16) reg2(5) 110101 reg1(5) ]", mnemonic="XORI")
def v850_3ops(obj, imm, reg2, reg1, _chk=0):
    if _chk & 2:
        _chk_reg_null(obj, reg2)
    dst, src = env.R[reg2], env.R[reg1]
    imm16 = env.cst(imm, 16)
    obj.operands = [imm16, src, dst]
    obj.type = type_data_processing


@ispec("48<[ disp(31) 0 00000 010111       reg1(5) ]", mnemonic="JARL")
@ispec("48<[ disp(31) 0 00000 010111 00000=reg1(5) ]", mnemonic="JR")
@ispec("48<[ disp(31) 0 00000 110111       reg1(5) ]", mnemonic="JMP")
def v850_3ops(obj, disp, reg1):
    dst = env.R[reg1]
    disp32 = env.cst(disp << 1, 32)
    obj.operands = [disp32, dst]
    if obj.mnemonic == "JR":
        obj.operands.pop()
    obj.type = type_control_flow


@ispec("48<[ disp(32) 00000 110001 reg1(5) ]", mnemonic="MOV")
def v850_mov(obj, disp, reg1):
    dst = env.R[reg1]
    disp32 = env.cst(disp, 32)
    obj.operands = [disp32, dst]
    obj.type = type_data_processing


# format VII
@ispec("32<[ ~disp(15)   d reg2(5) 111000 reg1(5) ]", mnemonic="LDB", _size=8)
@ispec("32<[ ~disp(15) 0=d reg2(5) 111001 reg1(5) ]", mnemonic="LDH", _size=16)
@ispec("32<[ ~disp(15) 1=d reg2(5) 111111 reg1(5) ]", mnemonic="LDHU", _size=16)
@ispec("32<[ ~disp(15) 1=d reg2(5) 111001 reg1(5) ]", mnemonic="LDW", _size=32)
@ispec("32<[ ~disp(15)   d reg2(5) 111010 reg1(5) ]", mnemonic="STB", _size=8)
@ispec("32<[ ~disp(15) 0=d reg2(5) 111011 reg1(5) ]", mnemonic="STH", _size=16)
@ispec("32<[ ~disp(15) 1=d reg2(5) 111011 reg1(5) ]", mnemonic="STW", _size=32)
def v850_ld_st(obj, disp, d, reg2, reg1, _size):
    disp = disp.int(-1) << 1
    if _size == 8:
        disp |= d
    src = env.mem(env.R[reg1], _size, disp=disp)
    dst = env.R[reg2]
    if obj.mnemonic.startswith("ST"):
        src, dst = dst, src
    obj.operands = [src, dst]
    obj.type = type_data_processing


@ispec("32<[ ~d(15) 1 reg2(5) 11110 ~b reg1(5) ]", mnemonic="LDBU", _size=8)
def v850_ld_st(obj, d, reg2, b, reg1, _size):
    if reg2 == 0:
        raise InstructionError(obj)
    disp = (b // d).int(-1)
    src = env.mem(env.R[reg1], _size, disp=disp)
    dst = env.R[reg2]
    obj.operands = [src, dst]
    obj.type = type_data_processing


# format VIII
@ispec("32<[ ~disp(16) 10 ~bnum(3) 111110 reg1(5) ]", mnemonic="CLR1")
@ispec("32<[ ~disp(16) 01 ~bnum(3) 111110 reg1(5) ]", mnemonic="NOT1")
@ispec("32<[ ~disp(16) 00 ~bnum(3) 111110 reg1(5) ]", mnemonic="SET1")
@ispec("32<[ ~disp(16) 11 ~bnum(3) 111110 reg1(5) ]", mnemonic="TST1")
def v850_bitwise(obj, disp, bnum, reg1):
    src = env.mem(env.R[reg1], 8, disp=disp.int(-1))
    obj.operands = [cst(bnum.int(), 3), src]
    obj.type = type_data_processing


# format IX
@ispec("32<[ 000000001110010 0 reg2(5) 111111 reg1(5) ]", mnemonic="CLR1")
@ispec("32<[ 000000001110001 0 reg2(5) 111111 reg1(5) ]", mnemonic="NOT1")
@ispec("32<[ 000000001110000 0 reg2(5) 111111 reg1(5) ]", mnemonic="SET1")
@ispec("32<[ 000000001110011 0 reg2(5) 111111 reg1(5) ]", mnemonic="TST1")
def v850_ext1(obj, reg2, reg1):
    src = env.mem(env.R[reg1], 8)
    r2 = env.R[reg2]
    obj.operands = [r2, src]
    obj.type = type_data_processing


@ispec("32<[ 000000000010000 0 reg2(5) 111111 reg1(5) ]", mnemonic="LDSR")
@ispec("32<[ 000000001010000 0 reg2(5) 111111 reg1(5) ]", mnemonic="SAR")
@ispec("32<[ 000000001100000 0 reg2(5) 111111 reg1(5) ]", mnemonic="SHL")
@ispec("32<[ 000000001000000 0 reg2(5) 111111 reg1(5) ]", mnemonic="SHR")
@ispec("32<[ 000000000100000 0 reg2(5) 111111 reg1(5) ]", mnemonic="STSR")
def v850_ldsr(obj, reg2, reg1):
    # src,dst are inverted for LDSR:
    src, dst = env.R[reg2], env.R[reg1]
    if obj.mnemonic.startswith("ST"):
        src, dst = dst, src
    obj.operands = [src, dst]
    obj.type = type_data_processing


@ispec("32<[ 000000100000000 0 reg2(5) 111111 0 cond(4) ]", mnemonic="SASF")
@ispec("32<[ 000000000000000 0 reg2(5) 111111 0 cond(4) ]", mnemonic="SETF")
def v850_cccc(obj, reg2, cond):
    c, dst = cond, env.R[reg2]
    obj.operands = [c, dst]
    obj.type = type_data_processing


# format X
@ispec("32<[ 000000010100010 0 0000011111100000 ]", mnemonic="CTRET")
@ispec("32<[ 000000010110000 0 0000011111100000 ]", mnemonic="DI")
@ispec("32<[ 000000010110000 0 1000011111100000 ]", mnemonic="EI")
@ispec("32<[ 000001111110000 0 0000000101001000 ]", mnemonic="EIRET")
@ispec("32<[ 000000010100101 0 0000011111100000 ]", mnemonic="FERET")
@ispec("32<[ 000000010010000 0 0000011111100000 ]", mnemonic="HALT")
@ispec("32<[ 000000010100000 0 0000011111100000 ]", mnemonic="RETI")
def v850_ext2(obj):
    obj.operands = []
    obj.type = type_data_processing


@ispec("32<[ 00 ~V(3) 001011 00000 11010 111111 ~v(5) ]", mnemonic="SYSCALL")
def v850_syscall(obj, V, v):
    obj.operands = [env.cst((v // V).int(), 8)]
    obj.type = type_control_flow


@ispec("32<[ 0000000100000000 00000 111111 v(5) ]", mnemonic="TRAP")
def v850_trap(obj, v):
    obj.operands = [env.cst(v, 5)]
    obj.type = type_control_flow


# format XI
@ispec("32<[ reg3(5) 011101 cond(4) 0 reg2(5) 111111 reg1(5) ]", mnemonic="ADF")
@ispec("32<[ reg3(5) 011001 cond(4) 0 reg2(5) 111111 reg1(5) ]", mnemonic="CMOV")
@ispec("32<[ reg3(5) 011100 cond(4) 0 reg2(5) 111111 reg1(5) ]", mnemonic="SBF")
def v850_cccc(obj, reg3, cond, reg2, reg1):
    if cond == env.CONDITION_SA and obj.mnemonic in ("ADF", "SBF"):
        raise InstructionError(obj)
    dst, src2, src1 = env.R[reg3], env.R[reg2], env.R[reg1]
    obj.operands = [cond, src1, src2, dst]
    obj.type = type_data_processing


@ispec("32<[ reg3(5) 000111  0111    0 reg2(5) 111111 reg1(5) ]", mnemonic="CAXI")
def v850_ext3(obj, reg3, reg2, reg1):
    dst, src2, src1 = env.R[reg3], env.R[reg2], env.R[reg1]
    adr = src1 & 0xFFFFFFFC
    obj.operands = [env.mem(adr, 32), src2, dst]
    obj.type = type_data_processing


@ispec("32<[ reg4(4) 0011110 reg3(4) 0 reg2(5) 111111 reg1(5) ]", mnemonic="MAC")
@ispec("32<[ reg4(4) 0011111 reg3(4) 0 reg2(5) 111111 reg1(5) ]", mnemonic="MACU")
def v850_mac(obj, reg4, reg3, reg2, reg1):
    dst, src3, src2, src1 = env.R[reg4 << 1], env.R[reg3 << 1], env.R[reg2], env.R[reg1]
    i.misc["reg4"] = reg4 << 1
    i.misc["reg3"] = reg3 << 1
    obj.operands = [src1, src2, src3, dst]
    obj.type = type_data_processing


@ispec("32<[ reg3(5) 01011  000000 reg2(5) 111111 reg1(5) ]", mnemonic="DIV")
@ispec("32<[ reg3(5) 01010  000000 reg2(5) 111111 reg1(5) ]", mnemonic="DIVH")
@ispec("32<[ reg3(5) 01011  000010 reg2(5) 111111 reg1(5) ]", mnemonic="DIVU")
@ispec("32<[ reg3(5) 01010  000010 reg2(5) 111111 reg1(5) ]", mnemonic="DIVHU")
@ispec("32<[ reg3(5) 01011  111100 reg2(5) 111111 reg1(5) ]", mnemonic="DIVQ")
@ispec("32<[ reg3(5) 01011  111110 reg2(5) 111111 reg1(5) ]", mnemonic="DIVQU")
@ispec("32<[ reg3(5) 01000  100000 reg2(5) 111111 reg1(5) ]", mnemonic="MUL")
@ispec("32<[ reg3(5) 01000  100010 reg2(5) 111111 reg1(5) ]", mnemonic="MULU")
@ispec("32<[ reg3(5) 00010  100010 reg2(5) 111111 reg1(5) ]", mnemonic="SAR")
@ispec("32<[ reg3(5) 01110  111010 reg2(5) 111111 reg1(5) ]", mnemonic="SATADD")
@ispec("32<[ reg3(5) 01110  011010 reg2(5) 111111 reg1(5) ]", mnemonic="SATSUB")
@ispec("32<[ reg3(5) 00011  000010 reg2(5) 111111 reg1(5) ]", mnemonic="SHL")
@ispec("32<[ reg3(5) 00010  000010 reg2(5) 111111 reg1(5) ]", mnemonic="SHR")
def v850_ext3(obj, reg3, reg2, reg1):
    dst, src2, src1 = env.R[reg3], env.R[reg2], env.R[reg1]
    obj.operands = [src1, src2, dst]
    obj.type = type_data_processing


# format XII
@ispec("32<[ reg3(5) 01101000010 reg2(5) 111111 00000 ]", mnemonic="BSH")
@ispec("32<[ reg3(5) 01101000000 reg2(5) 111111 00000 ]", mnemonic="BSW")
@ispec("32<[ reg3(5) 01101000110 reg2(5) 111111 00000 ]", mnemonic="HSH")
@ispec("32<[ reg3(5) 01101000100 reg2(5) 111111 00000 ]", mnemonic="HSW")
@ispec("32<[ reg3(5) 01101100100 reg2(5) 111111 00000 ]", mnemonic="SCHOL")
@ispec("32<[ reg3(5) 01101100000 reg2(5) 111111 00000 ]", mnemonic="SCHOR")
@ispec("32<[ reg3(5) 01101100110 reg2(5) 111111 00000 ]", mnemonic="SCH1L")
@ispec("32<[ reg3(5) 01101100010 reg2(5) 111111 00000 ]", mnemonic="SCH1R")
def v850_ext4(obj, reg3, reg2):
    dst, src = env.R[reg3], env.R[reg2]
    obj.operands = [src, dst]
    obj.type = type_data_processing


@ispec("32<[ reg3(5) 011000 cond(4) 0 reg2(5) 111111 imm5(5) ]", mnemonic="CMOV")
def v850_cccc(obj, reg3, cond, reg2, imm5):
    imm = env.cst(imm5, 5).signextend(32)
    dst, src = env.R[reg3], env.R[reg2]
    obj.operands = [cond, imm, src, dst]
    obj.type = type_data_processing


@ispec("32<[ reg3(5) 01001 ~I(4) 00 reg2(5) 111111 ~imm5(5) ]", mnemonic="MUL")
@ispec("32<[ reg3(5) 01001 ~I(4) 10 reg2(5) 111111 ~imm5(5) ]", mnemonic="MULU")
def v850_ext4(obj, reg3, I, reg2, imm5):
    imm9 = env.cst((imm5 // I), 9)
    dst, src = env.R[reg3], env.R[reg2]
    obj.operands = [imm9, src, dst]
    obj.type = type_data_processing


# format XIII
@ispec("32<[ ~l1(11) reg2(5) 00000 11001 imm(5) ~l0(1) ]", mnemonic="DISPOSE")
def v850_dispose(obj, l1, reg2, imm, l0):
    imm = imm << 2
    list12 = [env.R[x] for x in (30, 31, 29, 28, 23, 22, 21, 20, 27, 26, 25, 24)]
    L = []
    for b in (l0 // l1).bitlist():
        r = list12.pop(0)
        if b == 1:
            L.append(r)
    obj.operands = [env.mem(env.sp, 32, disp=imm), L]
    if reg2 != 0:
        obj.operands.append(env.R[reg2])
    obj.type = type_data_processing


@ispec("32<[ ~l1(11) 00001 00000 11110 imm(5) ~l0(1) ]", mnemonic="PREPARE")
def v850_prepare(obj, l1, imm, l0):
    imm = imm << 2
    list12 = [env.R[x] for x in (30, 31, 29, 28, 23, 22, 21, 20, 27, 26, 25, 24)]
    L = []
    for b in (l0 // l1).bitlist():
        r = list12.pop(0)
        if b == 1:
            L.append(r)
    obj.operands = [L, env.cst(imm, 5)]
    obj.type = type_data_processing


@ispec(
    "64<[ imm32(32) ~lh(11) ff(2) 011 00000 11110 imm(5) ~lo(1) ]", mnemonic="PREPARE"
)
def v850_prepare(obj, imm32, lh, ff, imm, lo):
    imm = imm << 2
    list12 = [env.R[x] for x in (30, 31, 29, 28, 23, 22, 21, 20, 27, 26, 25, 24)]
    L = []
    for b in (lo // lh).bitlist():
        r = list12.pop(0)
        if b == 1:
            L.append(r)
    if ff == 0b00:
        op3 = env.sp
    elif ff == 0b01:
        op3 = env.cst(imm & 0xFFFF, 16).signextend(32)
    elif ff == 0b10:
        op3 = env.cst((imm & 0xFFFF) << 16, 32)
    elif ff == 0b11:
        op3 = env.cst(imm, 32)
    obj.operands = [L, env.cst(imm, 5), op3]
    obj.type = type_data_processing


# format XIV
@ispec(
    "48<[ ~dhi(16) reg3(5) ~dlo(7) 0101 00000 111100 reg1(5) ]", mnemonic="LDB", _size=8
)
@ispec(
    "48<[ ~dhi(16) reg3(5) ~dlo(7) 0101 00000 111101 reg1(5) ]",
    mnemonic="LDBU",
    _size=8,
)
@ispec(
    "48<[ ~dhi(16) reg3(5) ~dlo(7) 0111 00000 111100 reg1(5) ]",
    mnemonic="LDH",
    _size=16,
)
@ispec(
    "48<[ ~dhi(16) reg3(5) ~dlo(7) 0111 00000 111101 reg1(5) ]",
    mnemonic="LDHU",
    _size=16,
)
@ispec(
    "48<[ ~dhi(16) reg3(5) ~dlo(7) 1001 00000 111100 reg1(5) ]",
    mnemonic="LDW",
    _size=32,
)
@ispec(
    "48<[ ~dhi(16) reg3(5) ~dlo(7) 1101 00000 111100 reg1(5) ]", mnemonic="STB", _size=8
)
@ispec(
    "48<[ ~dhi(16) reg3(5) ~dlo(7) 1101 00000 111101 reg1(5) ]",
    mnemonic="STH",
    _size=16,
)
@ispec(
    "48<[ ~dhi(16) reg3(5) ~dlo(7) 1111 00000 111100 reg1(5) ]",
    mnemonic="STW",
    _size=32,
)
def v850_ld_st(obj, dhi, reg3, dlo, reg1, _size):
    if _size > 8 and dlo[0]:
        raise InstructionError(obj)
    disp23 = (dlo // dhi).int(-1)
    src = env.mem(env.R[reg1], _size, disp=disp23)
    dst = env.R[reg3]
    if obj.mnemonic.startswith("ST"):
        src, dst = dst, src
    obj.operands = [src, dst]
    obj.type = type_data_processing
