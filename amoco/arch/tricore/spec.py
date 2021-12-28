# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2021 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.arch.tricore import env

from amoco.arch.core import *

# -------------------------------------------------------
# from TriCore TC1.6.2 core architecture manual V1.2.2
# (32-bit Unified Processor Core), 2020-01-15

# define all except FPU instructions
# -------------------------------------------------------

ISPECS = []

@ispec("32<[ disp1(16) disp2(8) {6d} ]", mnemonic="CALL")
@ispec("32<[ disp1(16) disp2(8) {61} ]", mnemonic="FCALL")
@ispec("32<[ disp1(16) disp2(8) {1d} ]", mnemonic="J")
@ispec("32<[ disp1(16) disp2(8) {5d} ]", mnemonic="JL")
def tricore_branch(obj, disp1, disp2):
    v = env.cst(((disp2<<16)+disp1)<<1,24)
    obj.operands = [disp.signextend(32)]
    obj.type = type_control_flow

@ispec("32<[ disp1(16) disp2(8) {ed} ]", mnemonic="CALLA")
@ispec("32<[ disp1(16) disp2(8) {e1} ]", mnemonic="FCALLA")
@ispec("32<[ disp1(16) disp2(8) {9d} ]", mnemonic="JA")
@ispec("32<[ disp1(16) disp2(8) {dd} ]", mnemonic="JLA")
def tricore_branch(obj, disp1, disp2):
    v = env.cst((disp2<<16)+disp1,24)
    addr = composer([env.bit0,v[0:20],env.cst(0,7),v[20:24]])
    obj.operands = [addr]
    obj.type = type_control_flow

@ispec("32<[ ---- {00} ---- ---- a(4) {2d} ]", mnemonic="CALLI")
@ispec("32<[ ---- {01} ---- ---- a(4) {2d} ]", mnemonic="FCALLI")
@ispec("32<[ ---- {03} ---- ---- a(4) {2d} ]", mnemonic="JI")
@ispec("32<[ ---- {02} ---- ---- a(4) {2d} ]", mnemonic="JLI")
def tricore_branchI(obj, a):
    src = env.A[a]
    obj.operands = [src]
    obj.type = type_control_flow

@ispec("16<[ disp(8) {5c} ]", mnemonic="CALL")
@ispec("16<[ disp(8) {3c} ]", mnemonic="J")
@ispec("16<[ disp(8) {ee} ]", mnemonic="JNZ")
@ispec("16<[ disp(8) {6e} ]", mnemonic="JZ")
def tricore_branch(obj, disp):
    disp = env.cst(disp<<1,8)
    obj.operands = [disp.signextend(32)]
    obj.type = type_control_flow

@ispec("32<[ ---- 0000000 const9(9) ---- {ad} ]", mnemonic="BISR")
@ispec("32<[ ---- 0000100 const9(9) ---- {ad} ]", mnemonic="SYSCALL")
def tricore_system(obj, const9):
    obj.operands = [env.cst(const9,9)]
    obj.type = type_system

@ispec("32<[ c(4) {1c} ---- b(4) ---- {0b} ]", mnemonic="ABS")
@ispec("32<[ c(4) {5c} ---- b(4) ---- {0b} ]", mnemonic="ABS_B")
@ispec("32<[ c(4) {7c} ---- b(4) ---- {0b} ]", mnemonic="ABS_H")
@ispec("32<[ c(4) {1d} ---- b(4) ---- {0b} ]", mnemonic="ABSS")
@ispec("32<[ c(4) {7d} ---- b(4) ---- {0b} ]", mnemonic="ABSS_H")
@ispec("32<[ c(4) {1f} ---- b(4) ---- {0b} ]", mnemonic="MOV")
def tricore_dd_arithmetic(obj, c, b):
    src = env.D[b]
    dst = env.D[c]
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("32<[ c(4) {80} ---- b(4) ---- {0b} ]", mnemonic="MOV")
def tricore_dd_arithmetic(obj, c, b):
    src = env.D[b]
    dst = env.E[c]
    obj.operands = [dst, src.signextend(64)]
    obj.type = type_data_processing

@ispec("32<[ c(4) {81} ---- b(4) a(4) {0b} ]", mnemonic="MOV")
def tricore_dd_arithmetic(obj, c, b, a):
    src2 = env.D[b]
    dst = env.E[c]
    obj.operands = [dst, composer([src2,src1])]
    obj.type = type_data_processing

@ispec("32<[ c(4) {0e} ---- b(4) a(4) {0b} ]", mnemonic="ABSDIF")
@ispec("32<[ c(4) {4e} ---- b(4) a(4) {0b} ]", mnemonic="ABSDIF_B")
@ispec("32<[ c(4) {6e} ---- b(4) a(4) {0b} ]", mnemonic="ABSDIF_H")
@ispec("32<[ c(4) {0f} ---- b(4) a(4) {0b} ]", mnemonic="ABSDIFS")
@ispec("32<[ c(4) {6f} ---- b(4) a(4) {0b} ]", mnemonic="ABSDIFS_H")
@ispec("32<[ c(4) {00} ---- b(4) a(4) {0b} ]", mnemonic="ADD")
@ispec("32<[ c(4) {40} ---- b(4) a(4) {0b} ]", mnemonic="ADD_B")
@ispec("32<[ c(4) {60} ---- b(4) a(4) {0b} ]", mnemonic="ADD_H")
@ispec("32<[ c(4) {05} ---- b(4) a(4) {0b} ]", mnemonic="ADDC")
@ispec("32<[ c(4) {02} ---- b(4) a(4) {0b} ]", mnemonic="ADDS")
@ispec("32<[ c(4) {62} ---- b(4) a(4) {0b} ]", mnemonic="ADDS_H")
@ispec("32<[ c(4) {63} ---- b(4) a(4) {0b} ]", mnemonic="ADDS_HU")
@ispec("32<[ c(4) {03} ---- b(4) a(4) {0b} ]", mnemonic="ADDS_U")
@ispec("32<[ c(4) {04} ---- b(4) a(4) {0b} ]", mnemonic="ADDX")
@ispec("32<[ c(4) {08} ---- b(4) a(4) {0f} ]", mnemonic="AND")
@ispec("32<[ c(4) {20} ---- b(4) a(4) {0b} ]", mnemonic="AND_EQ")
@ispec("32<[ c(4) {24} ---- b(4) a(4) {0b} ]", mnemonic="AND_GE")
@ispec("32<[ c(4) {25} ---- b(4) a(4) {0b} ]", mnemonic="AND_GE_U")
@ispec("32<[ c(4) {22} ---- b(4) a(4) {0b} ]", mnemonic="AND_LT")
@ispec("32<[ c(4) {23} ---- b(4) a(4) {0b} ]", mnemonic="AND_LT_U")
@ispec("32<[ c(4) {21} ---- b(4) a(4) {0b} ]", mnemonic="AND_NE")
@ispec("32<[ c(4) {0e} ---- b(4) a(4) {0f} ]", mnemonic="ANDN")
@ispec("32<[ c(4) {10} ---- b(4) a(4) {0b} ]", mnemonic="EQ")
@ispec("32<[ c(4) {50} ---- b(4) a(4) {0b} ]", mnemonic="EQ_B")
@ispec("32<[ c(4) {70} ---- b(4) a(4) {0b} ]", mnemonic="EQ_H")
@ispec("32<[ c(4) {90} ---- b(4) a(4) {0b} ]", mnemonic="EQ_W")
@ispec("32<[ c(4) {56} ---- b(4) a(4) {0b} ]", mnemonic="EQANY_B")
@ispec("32<[ c(4) {76} ---- b(4) a(4) {0b} ]", mnemonic="EQANY_H")
@ispec("32<[ c(4) {14} ---- b(4) a(4) {0b} ]", mnemonic="GE")
@ispec("32<[ c(4) {15} ---- b(4) a(4) {0b} ]", mnemonic="GE_U")
@ispec("32<[ c(4) {12} ---- b(4) a(4) {0b} ]", mnemonic="LT")
@ispec("32<[ c(4) {13} ---- b(4) a(4) {0b} ]", mnemonic="LT_U")
@ispec("32<[ c(4) {52} ---- b(4) a(4) {0b} ]", mnemonic="LT_B")
@ispec("32<[ c(4) {53} ---- b(4) a(4) {0b} ]", mnemonic="LT_BU")
@ispec("32<[ c(4) {72} ---- b(4) a(4) {0b} ]", mnemonic="LT_H")
@ispec("32<[ c(4) {73} ---- b(4) a(4) {0b} ]", mnemonic="LT_HU")
@ispec("32<[ c(4) {92} ---- b(4) a(4) {0b} ]", mnemonic="LT_W")
@ispec("32<[ c(4) {93} ---- b(4) a(4) {0b} ]", mnemonic="LT_WU")
@ispec("32<[ c(4) {1a} ---- b(4) a(4) {0b} ]", mnemonic="MAX")
@ispec("32<[ c(4) {1b} ---- b(4) a(4) {0b} ]", mnemonic="MAX_U")
@ispec("32<[ c(4) {5a} ---- b(4) a(4) {0b} ]", mnemonic="MAX_B")
@ispec("32<[ c(4) {5b} ---- b(4) a(4) {0b} ]", mnemonic="MAX_BU")
@ispec("32<[ c(4) {7a} ---- b(4) a(4) {0b} ]", mnemonic="MAX_H")
@ispec("32<[ c(4) {7b} ---- b(4) a(4) {0b} ]", mnemonic="MAX_HU")
@ispec("32<[ c(4) {18} ---- b(4) a(4) {0b} ]", mnemonic="MIN")
@ispec("32<[ c(4) {19} ---- b(4) a(4) {0b} ]", mnemonic="MIN_U")
@ispec("32<[ c(4) {58} ---- b(4) a(4) {0b} ]", mnemonic="MIN_B")
@ispec("32<[ c(4) {59} ---- b(4) a(4) {0b} ]", mnemonic="MIN_BU")
@ispec("32<[ c(4) {78} ---- b(4) a(4) {0b} ]", mnemonic="MIN_H")
@ispec("32<[ c(4) {79} ---- b(4) a(4) {0b} ]", mnemonic="MIN_HU")
@ispec("32<[ c(4) {09} ---- b(4) a(4) {0f} ]", mnemonic="NAND")
@ispec("32<[ c(4) {11} ---- b(4) a(4) {0b} ]", mnemonic="NE")
@ispec("32<[ c(4) {0b} ---- b(4) a(4) {0f} ]", mnemonic="NOR")
@ispec("32<[ c(4) {0a} ---- b(4) a(4) {0f} ]", mnemonic="OR")
@ispec("32<[ c(4) {27} ---- b(4) a(4) {0b} ]", mnemonic="OR_EQ")
@ispec("32<[ c(4) {2b} ---- b(4) a(4) {0b} ]", mnemonic="OR_GE")
@ispec("32<[ c(4) {2c} ---- b(4) a(4) {0b} ]", mnemonic="OR_GE_U")
@ispec("32<[ c(4) {29} ---- b(4) a(4) {0b} ]", mnemonic="OR_LT")
@ispec("32<[ c(4) {2a} ---- b(4) a(4) {0b} ]", mnemonic="OR_LT_U")
@ispec("32<[ c(4) {28} ---- b(4) a(4) {0b} ]", mnemonic="OR_NE")
@ispec("32<[ c(4) {0f} ---- b(4) a(4) {0f} ]", mnemonic="ORN")
@ispec("32<[ c(4) {00} ---- b(4) a(4) {0f} ]", mnemonic="SH")
@ispec("32<[ c(4) {37} ---- b(4) a(4) {0b} ]", mnemonic="SH_EQ")
@ispec("32<[ c(4) {3b} ---- b(4) a(4) {0b} ]", mnemonic="SH_GE")
@ispec("32<[ c(4) {3c} ---- b(4) a(4) {0b} ]", mnemonic="SH_GE_U")
@ispec("32<[ c(4) {40} ---- b(4) a(4) {0f} ]", mnemonic="SH_H")
@ispec("32<[ c(4) {39} ---- b(4) a(4) {0b} ]", mnemonic="SH_LT")
@ispec("32<[ c(4) {3a} ---- b(4) a(4) {0b} ]", mnemonic="SH_LT_U")
@ispec("32<[ c(4) {38} ---- b(4) a(4) {0b} ]", mnemonic="SH_NE")
@ispec("32<[ c(4) {01} ---- b(4) a(4) {0f} ]", mnemonic="SHA")
@ispec("32<[ c(4) {41} ---- b(4) a(4) {0f} ]", mnemonic="SHA_H")
@ispec("32<[ c(4) {02} ---- b(4) a(4) {0f} ]", mnemonic="SHAS")
@ispec("32<[ c(4) {08} ---- b(4) a(4) {0b} ]", mnemonic="SUB")
@ispec("32<[ c(4) {48} ---- b(4) a(4) {0b} ]", mnemonic="SUB_B")
@ispec("32<[ c(4) {68} ---- b(4) a(4) {0b} ]", mnemonic="SUB_H")
@ispec("32<[ c(4) {0d} ---- b(4) a(4) {0b} ]", mnemonic="SUBC")
@ispec("32<[ c(4) {0a} ---- b(4) a(4) {0b} ]", mnemonic="SUBS")
@ispec("32<[ c(4) {0b} ---- b(4) a(4) {0b} ]", mnemonic="SUBS_U")
@ispec("32<[ c(4) {6a} ---- b(4) a(4) {0b} ]", mnemonic="SUBS_H")
@ispec("32<[ c(4) {6b} ---- b(4) a(4) {0b} ]", mnemonic="SUBS_HU")
@ispec("32<[ c(4) {0c} ---- b(4) a(4) {0b} ]", mnemonic="SUBX")
@ispec("32<[ c(4) {0d} ---- b(4) a(4) {0f} ]", mnemonic="XNOR")
@ispec("32<[ c(4) {0c} ---- b(4) a(4) {0f} ]", mnemonic="XOR")
@ispec("32<[ c(4) {2f} ---- b(4) a(4) {0b} ]", mnemonic="XOR_EQ")
@ispec("32<[ c(4) {30} ---- b(4) a(4) {0b} ]", mnemonic="XOR_NE")
def tricore_ddd_arithmetic(obj, c, b, a):
    src1 = env.D[a]
    src2 = env.D[b]
    dst = env.D[c]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) {40} ---- b(4) a(4) {01} ]", mnemonic="EQ_A")
@ispec("32<[ c(4) {43} ---- b(4) a(4) {01} ]", mnemonic="GE_A")
@ispec("32<[ c(4) {42} ---- b(4) a(4) {01} ]", mnemonic="LT_A")
@ispec("32<[ c(4) {41} ---- b(4) a(4) {01} ]", mnemonic="NE_A")
def tricore_daa_arithmetic(obj, c, b, a):
    src1 = env.A[a]
    src2 = env.A[b]
    dst = env.D[c]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) {63} ---- b(4) ---- {01} ]", mnemonic="MOV_A",  _dst=env.A, _src=env.D)
@ispec("32<[ c(4) {00} ---- b(4) ---- {01} ]", mnemonic="MOV_AA", _dst=env.A, _src=env.A)
@ispec("32<[ c(4) {4c} ---- b(4) ---- {01} ]", mnemonic="MOV_D",  _dst=env.D, _src=env.A)
def tricore_daa_arithmetic(obj, c, b, _dst, _src):
    dst = _dst[c]
    src = _src[b]
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("32<[ c(4) {48} ---- ---- a(4) {01} ]", mnemonic="EQZ_A")
@ispec("32<[ c(4) {49} ---- ---- a(4) {01} ]", mnemonic="NEZ_A")
def tricore_da_arithmetic(obj, c, a):
    src1 = env.A[a]
    dst = env.D[c]
    obj.operands = [dst, src1]
    obj.type = type_data_processing

@ispec("32<[ c(4) {01} --00 b(4) a(4) {4b} ]", mnemonic="BMERGE")
def tricore_ddd_arithmetic(obj, c, b, a):
    src1 = env.D[a]
    src2 = env.D[b]
    dst = env.D[c]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) {06} --00 b(4) a(4) {4b} ]", mnemonic="CRC32_B")
@ispec("32<[ c(4) {03} --00 b(4) a(4) {4b} ]", mnemonic="CRC32B_W")
@ispec("32<[ c(4) {03} --00 b(4) a(4) {4b} ]", mnemonic="CRC32L_W")
def tricore_crc32(obj, c, b, a):
    src1 = env.D[a]
    src2 = env.D[b]
    dst = env.D[c]
    obj.operands = [dst, src2, src1]
    obj.type = type_data_processing

@ispec("32<[ c(4) {20} --01 b(4) a(4) {4b} ]", mnemonic="DIV")
@ispec("32<[ c(4) {21} --01 b(4) a(4) {4b} ]", mnemonic="DIV_U")
@ispec("32<[ c(4) {5a} --00 b(4) a(4) {4b} ]", mnemonic="DVINIT_B")
@ispec("32<[ c(4) {4a} --00 b(4) a(4) {4b} ]", mnemonic="DVINIT_BU")
@ispec("32<[ c(4) {3a} --00 b(4) a(4) {4b} ]", mnemonic="DVINIT_H")
@ispec("32<[ c(4) {2a} --00 b(4) a(4) {4b} ]", mnemonic="DVINIT_HU")
@ispec("32<[ c(4) {1a} --00 b(4) a(4) {4b} ]", mnemonic="DVINIT")
@ispec("32<[ c(4) {0a} --00 b(4) a(4) {4b} ]", mnemonic="DVINIT_U")
def tricore_edd_arithmetic(obj, c, b, a):
    src1 = env.D[a]
    src2 = env.D[b]
    if c%2:
        raise InstructionError(obj)
    dst = env.E[c]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 100 ----- b(4) a(4) {17} ]", mnemonic="DEXTR")
def tricore_dddc(obj, c, d, b, a):
    shift = env.D[d]
    src1 = env.D[a]
    src2 = env.D[b]
    dst = env.D[c]
    obj.operands = [dst, src1, src2, shift]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 010 ----- ---- a(4) {17} ]", mnemonic="EXTR")
@ispec("32<[ c(4) d(4) 011 ----- ---- a(4) {17} ]", mnemonic="EXTR_U")
def tricore_extr(obj, c, d, a):
    if d%2:
        raise InstructionError(obj)
    width = env.E[d][32:37]
    src1 = env.D[a]
    dst = env.D[c]
    obj.operands = [dst, src1, width]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 000 0--00 ---- a(4) {6b} ]", mnemonic="PACK")
def tricore_extr(obj, c, d, a):
    if d%2:
        raise InstructionError(obj)
    src1 = env.E[d]
    src2 = env.D[a]
    dst = env.D[c]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) {08} -- 00 ---- a(4) {4b} ]", mnemonic="UNPACK")
def tricore_extr(obj, c, d, a):
    src = env.D[a]
    dst = env.E[c]
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("32<[ c(4) {02} -- 00 ---- a(4) {4b} ]", mnemonic="PARITY")
@ispec("32<[ c(4) {22} -- 00 ---- a(4) {4b} ]", mnemonic="POPCNT_W")
def tricore_extr(obj, c, d, a):
    src = env.D[a]
    dst = env.D[c]
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("32<[ c(4) pos(5) 00 ----- b(4) a(4) {77} ]", mnemonic="DEXTR")
def tricore_dextr(obj, c, pos, b, a):
    src1 = env.D[a]
    src2 = env.D[b]
    dst = env.D[c]
    obj.operands = [dst, src1, src2, env.cst(pos,5)]
    obj.type = type_data_processing

@ispec("32<[ c(4) pos(5) 10 width(5) ---- a(4) {37} ]", mnemonic="EXTR")
@ispec("32<[ c(4) pos(5) 11 width(5) ---- a(4) {37} ]", mnemonic="EXTR_U")
def tricore_extr(obj, c, pos, width, a):
    src1 = env.D[a]
    dst = env.D[c]
    obj.operands = [dst, src1, env.cst(pos,5), env.cst(width,5)]
    obj.type = type_data_processing

@ispec("32<[ c(4) pos(5) 01 width(5) const(4) ---- {b7} ]", mnemonic="IMASK")
def tricore_imask(obj, c, pos, width, const):
    if c%2:
        raise InstructionError(obj)
    dst = env.E[c]
    obj.operands = [dst, env.cst(const,4), env.cst(pos,5), env.cst(width,5)]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 001 width(5) const(4) ---- {d7} ]", mnemonic="IMASK")
def tricore_imask(obj, c, d, width, const):
    src2 = env.D[d]
    if c%2:
        raise InstructionError(obj)
    dst = env.E[c]
    obj.operands = [dst, env.cst(const,4), src2, env.cst(width,5)]
    obj.type = type_data_processing

@ispec("32<[ c(4) pos(5) 01 width(5) b(4) ---- {37} ]", mnemonic="IMASK")
def tricore_imask(obj, c, pos, width, b):
    src1 = env.D[b]
    if c%2:
        raise InstructionError(obj)
    dst = env.E[c]
    obj.operands = [dst, src1, env.cst(pos,5), env.cst(width,5)]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 001 width(5) b(4) ---- {57} ]", mnemonic="IMASK")
def tricore_imask(obj, c, d, width, b):
    src1 = env.D[b]
    src2 = env.D[d]
    if c%2:
        raise InstructionError(obj)
    dst = env.E[c]
    obj.operands = [dst, src1, src2, env.cst(width,5)]
    obj.type = type_data_processing

@ispec("32<[ c(4) pos(5) 00 width(5) const(4) a(4) {b7} ]", mnemonic="INSERT")
def tricore_imask(obj, c, pos, width, const, a):
    dst = env.D[c]
    src1 = env.D[a]
    obj.operands = [dst, src1, env.cst(const,4), env.cst(pos,5), env.cst(width,5)]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 000 ----- const(4) a(4) {97} ]", mnemonic="INSERT")
def tricore_imask(obj, c, d, const, a):
    src1 = env.D[a]
    if d%2:
        raise InstructionError(obj)
    src3 = env.E[d]
    dst = env.D[c]
    obj.operands = [dst, src1, env.cst(const,4), src3]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 000 width(5) const(4) a(4) {d7} ]", mnemonic="INSERT")
def tricore_imask(obj, c, d, width, const, a):
    src1 = env.D[a]
    src3 = env.D[d]
    dst = env.D[c]
    obj.operands = [dst, src1, env.cst(const,4), src3]
    obj.type = type_data_processing

@ispec("32<[ c(4) pos(5) 00 width(5) b(4) a(4) {37} ]", mnemonic="INSERT")
def tricore_imask(obj, c, pos, width, b, a):
    dst = env.D[c]
    src1 = env.D[a]
    src2 = env.D[b]
    obj.operands = [dst, src1, src2, env.cst(pos,5), env.cst(width,5)]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 000 ----- b(4) a(4) {17} ]", mnemonic="INSERT")
def tricore_imask(obj, c, d, b, a):
    src1 = env.D[a]
    src2 = env.D[b]
    if d%2:
        raise InstructionError(obj)
    src3 = env.E[d]
    dst = env.D[c]
    obj.operands = [dst, src1, src2, src3]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 000 width(5) b(4) a(4) {57} ]", mnemonic="INSERT")
def tricore_imask(obj, c, d, width, b, a):
    src1 = env.D[a]
    src2 = env.D[b]
    src3 = env.D[d]
    dst = env.D[c]
    obj.operands = [dst, src1, src2, src3, env.cst(width,5)]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 010 width(5) ---- a(4) {57} ]", mnemonic="EXTR")
@ispec("32<[ c(4) d(4) 011 width(5) ---- a(4) {57} ]", mnemonic="EXTR_U")
def tricore_extr(obj, c, d, width, a):
    src2 = env.D[d]
    src1 = env.D[a]
    dst = env.D[c]
    obj.operands = [dst, src1, src2, env.cst(width,5)]
    obj.type = type_data_processing

@ispec("32<[ c(4) {09} --00 ---- a(4) {4b} ]", mnemonic="BSPLIT")
def tricore_edd_arithmetic(obj, c, a):
    src1 = env.D[a]
    dst = env.E[c]
    obj.operands = [dst, src1]
    obj.type = type_data_processing

@ispec("32<[ c(4) 0001110 ~const9(9) a(4) {8b} ]", mnemonic="ABSDIF")
@ispec("32<[ c(4) 0001111 ~const9(9) a(4) {8b} ]", mnemonic="ABSDIFS")
@ispec("32<[ c(4) 0000000 ~const9(9) a(4) {8b} ]", mnemonic="ADD")
@ispec("32<[ c(4) 0000101 ~const9(9) a(4) {8b} ]", mnemonic="ADDC")
@ispec("32<[ c(4) 0000010 ~const9(9) a(4) {8b} ]", mnemonic="ADDS")
@ispec("32<[ c(4) 0000011 ~const9(9) a(4) {8b} ]", mnemonic="ADDS_U")  #const9 is signed
@ispec("32<[ c(4) 0000100 ~const9(9) a(4) {8b} ]", mnemonic="ADDX")
@ispec("32<[ c(4) 0100000 ~const9(9) a(4) {8b} ]", mnemonic="AND_EQ")
@ispec("32<[ c(4) 0100100 ~const9(9) a(4) {8b} ]", mnemonic="AND_GE")
@ispec("32<[ c(4) 0100010 ~const9(9) a(4) {8b} ]", mnemonic="AND_LT")
@ispec("32<[ c(4) 0100001 ~const9(9) a(4) {8b} ]", mnemonic="AND_NE")
@ispec("32<[ c(4) 0010000 ~const9(9) a(4) {8b} ]", mnemonic="EQ")
@ispec("32<[ c(4) 1010110 ~const9(9) a(4) {8b} ]", mnemonic="EQANY_B")
@ispec("32<[ c(4) 1110110 ~const9(9) a(4) {8b} ]", mnemonic="EQANY_H")
@ispec("32<[ c(4) 0010100 ~const9(9) a(4) {8b} ]", mnemonic="GE")
@ispec("32<[ c(4) 0010010 ~const9(9) a(4) {8b} ]", mnemonic="LT")
@ispec("32<[ c(4) 0011010 ~const9(9) a(4) {8b} ]", mnemonic="MAX")
@ispec("32<[ c(4) 0010001 ~const9(9) a(4) {8b} ]", mnemonic="NE")
@ispec("32<[ c(4) 0100111 ~const9(9) a(4) {8b} ]", mnemonic="OR_EQ")
@ispec("32<[ c(4) 0101011 ~const9(9) a(4) {8b} ]", mnemonic="OR_GE")
@ispec("32<[ c(4) 0101001 ~const9(9) a(4) {8b} ]", mnemonic="OR_LT")
@ispec("32<[ c(4) 0001000 ~const9(9) a(4) {8b} ]", mnemonic="RSUB")
@ispec("32<[ c(4) 0001001 ~const9(9) a(4) {8b} ]", mnemonic="RSUBS")
@ispec("32<[ c(4) 0001011 ~const9(9) a(4) {8b} ]", mnemonic="RSUBS_U") #const9 is signed
@ispec("32<[ c(4) 0000000 ~const9(9) a(4) {8f} ]", mnemonic="SH")
@ispec("32<[ c(4) 1000000 ~const9(9) a(4) {8f} ]", mnemonic="SH_H")
@ispec("32<[ c(4) 0110111 ~const9(9) a(4) {8b} ]", mnemonic="SH_EQ")
@ispec("32<[ c(4) 0111011 ~const9(9) a(4) {8b} ]", mnemonic="SH_GE")
@ispec("32<[ c(4) 0111001 ~const9(9) a(4) {8b} ]", mnemonic="SH_LT")
@ispec("32<[ c(4) 0111000 ~const9(9) a(4) {8b} ]", mnemonic="SH_NE")
@ispec("32<[ c(4) 0000001 ~const9(9) a(4) {8f} ]", mnemonic="SHA")
@ispec("32<[ c(4) 1000001 ~const9(9) a(4) {8f} ]", mnemonic="SHA_H")
@ispec("32<[ c(4) 0000010 ~const9(9) a(4) {8f} ]", mnemonic="SHAS")
@ispec("32<[ c(4) 0101111 ~const9(9) a(4) {8b} ]", mnemonic="XOR_EQ")
@ispec("32<[ c(4) 0110011 ~const9(9) a(4) {8b} ]", mnemonic="XOR_GE")
@ispec("32<[ c(4) 0110001 ~const9(9) a(4) {8b} ]", mnemonic="XOR_LT")
@ispec("32<[ c(4) 0110000 ~const9(9) a(4) {8b} ]", mnemonic="XOR_NE")
def tricore_ddc_arithmetic(obj, c, const9, a):
    src1 = env.D[a]
    if obj.mnemonic in ("SH","SHA","SHAS"):
        const9 = const9[0:6]
    elif obj.mnemonic in ("SH_H","SHA_H"):
        const9 = const9[0:5]
    src2 = env.cst(const9.int(-1),32)
    dst = env.D[c]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) pos2(5) 00 pos1(5) b(4) a(4) {47} ]", mnemonic="AND_AND_T")
@ispec("32<[ c(4) pos2(5) 11 pos1(5) b(4) a(4) {47} ]", mnemonic="AND_ANDN_T")
@ispec("32<[ c(4) pos2(5) 10 pos1(5) b(4) a(4) {47} ]", mnemonic="AND_NOR_T")
@ispec("32<[ c(4) pos2(5) 01 pos1(5) b(4) a(4) {47} ]", mnemonic="AND_OR_T")
@ispec("32<[ c(4) pos2(5) 00 pos1(5) b(4) a(4) {87} ]", mnemonic="AND_T")
@ispec("32<[ c(4) pos2(5) 11 pos1(5) b(4) a(4) {87} ]", mnemonic="ANDN_T")
@ispec("32<[ c(4) pos2(5) 00 pos1(5) b(4) a(4) {67} ]", mnemonic="INS_T")
@ispec("32<[ c(4) pos2(5) 01 pos1(5) b(4) a(4) {67} ]", mnemonic="INSN_T")
@ispec("32<[ c(4) pos2(5) 00 pos1(5) b(4) a(4) {07} ]", mnemonic="NAND_T")
@ispec("32<[ c(4) pos2(5) 10 pos1(5) b(4) a(4) {87} ]", mnemonic="NOR_T")
@ispec("32<[ c(4) pos2(5) 00 pos1(5) b(4) a(4) {c7} ]", mnemonic="OR_AND_T")
@ispec("32<[ c(4) pos2(5) 11 pos1(5) b(4) a(4) {c7} ]", mnemonic="OR_ANDN_T")
@ispec("32<[ c(4) pos2(5) 10 pos1(5) b(4) a(4) {c7} ]", mnemonic="OR_NOR_T")
@ispec("32<[ c(4) pos2(5) 01 pos1(5) b(4) a(4) {c7} ]", mnemonic="OR_OR_T")
@ispec("32<[ c(4) pos2(5) 01 pos1(5) b(4) a(4) {87} ]", mnemonic="OR_T")
@ispec("32<[ c(4) pos2(5) 01 pos1(5) b(4) a(4) {07} ]", mnemonic="ORN_T")
@ispec("32<[ c(4) pos2(5) 00 pos1(5) b(4) a(4) {27} ]", mnemonic="SH_AND_T")
@ispec("32<[ c(4) pos2(5) 11 pos1(5) b(4) a(4) {27} ]", mnemonic="SH_ANDN_T")
@ispec("32<[ c(4) pos2(5) 00 pos1(5) b(4) a(4) {a7} ]", mnemonic="SH_NAND_T")
@ispec("32<[ c(4) pos2(5) 10 pos1(5) b(4) a(4) {27} ]", mnemonic="SH_NOR_T")
@ispec("32<[ c(4) pos2(5) 01 pos1(5) b(4) a(4) {27} ]", mnemonic="SH_OR_T")
@ispec("32<[ c(4) pos2(5) 01 pos1(5) b(4) a(4) {a7} ]", mnemonic="SH_ORN_T")
@ispec("32<[ c(4) pos2(5) 10 pos1(5) b(4) a(4) {a7} ]", mnemonic="SH_XNOR_T")
@ispec("32<[ c(4) pos2(5) 11 pos1(5) b(4) a(4) {a7} ]", mnemonic="SH_XOR_T")
@ispec("32<[ c(4) pos2(5) 10 pos1(5) b(4) a(4) {07} ]", mnemonic="XNOR_T")
@ispec("32<[ c(4) pos2(5) 11 pos1(5) b(4) a(4) {07} ]", mnemonic="XOR_T")
def tricore_ddd_arithmetic(obj, c, pos2, pos1, b, a):
    src1 = env.D[a]
    src2 = env.D[b]
    dst = env.D[c]
    obj.operands = [dst, src1[pos1:pos1+1], src2[pos2:pos2+1]]
    obj.type = type_data_processing

@ispec("32<[ c(4) 0001000 const9(9) a(4) {8f} ]", mnemonic="AND")
@ispec("32<[ c(4) 0100101 const9(9) a(4) {8b} ]", mnemonic="AND_GE_U")
@ispec("32<[ c(4) 0100011 const9(9) a(4) {8b} ]", mnemonic="AND_LT_U")
@ispec("32<[ c(4) 0001110 const9(9) a(4) {8f} ]", mnemonic="ANDN")
@ispec("32<[ c(4) 0001001 const9(9) a(4) {8f} ]", mnemonic="NAND")
@ispec("32<[ c(4) 0001011 const9(9) a(4) {8f} ]", mnemonic="NOR")
@ispec("32<[ c(4) 0010101 const9(9) a(4) {8b} ]", mnemonic="GE_U")
@ispec("32<[ c(4) 0001010 const9(9) a(4) {8f} ]", mnemonic="OR")
@ispec("32<[ c(4) 0101100 const9(9) a(4) {8b} ]", mnemonic="OR_GE_U")
@ispec("32<[ c(4) 0101010 const9(9) a(4) {8b} ]", mnemonic="OR_LT_U")
@ispec("32<[ c(4) 0101000 const9(9) a(4) {8b} ]", mnemonic="OR_NE")
@ispec("32<[ c(4) 0001111 const9(9) a(4) {8f} ]", mnemonic="ORN")
@ispec("32<[ c(4) 0000111 const9(9) a(4) {8f} ]", mnemonic="SHUFFLE")
@ispec("32<[ c(4) 0001101 const9(9) a(4) {8f} ]", mnemonic="XNOR")
@ispec("32<[ c(4) 0001100 const9(9) a(4) {8f} ]", mnemonic="XOR")
@ispec("32<[ c(4) 0111100 const9(9) a(4) {8b} ]", mnemonic="SH_GE_U")
@ispec("32<[ c(4) 0111010 const9(9) a(4) {8b} ]", mnemonic="SH_LT_U")
@ispec("32<[ c(4) 0110100 const9(9) a(4) {8b} ]", mnemonic="XOR_GE_U")
@ispec("32<[ c(4) 0110011 const9(9) a(4) {8b} ]", mnemonic="XOR_LT_U")
@ispec("32<[ c(4) 0011011 const9(9) a(4) {8b} ]", mnemonic="MAX_U")
@ispec("32<[ c(4) 0010011 const9(9) a(4) {8b} ]", mnemonic="LT_U")
def tricore_ddc_arithmetic(obj, c, const9, a):
    src1 = env.D[a]
    src2 = env.cst(const9,32)
    dst = env.D[c]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ ~const4(4) a(4) {c2} ]", mnemonic="ADD")
@ispec("16<[ ~const4(4) a(4) {06} ]", mnemonic="SH")
@ispec("16<[ ~const4(4) a(4) {86} ]", mnemonic="SHA")
def tricore_ddc_arithmetic(obj, const4, a):
    dst = env.D[a]
    src2 = env.cst(const4.int(-1),32)
    src1 = env.D[a]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ ~const4(4) a(4) {92} ]", mnemonic="ADD")
@ispec("16<[ ~const4(4) a(4) {8a} ]", mnemonic="CADD")
@ispec("16<[ ~const4(4) a(4) {ca} ]", mnemonic="CADDN")
@ispec("16<[ ~const4(4) a(4) {aa} ]", mnemonic="CMOV")
@ispec("16<[ ~const4(4) a(4) {ea} ]", mnemonic="CMOVN")
def tricore_ddc_arithmetic(obj, const4, a):
    dst = env.D[a]
    src2 = env.cst(const4.int(-1),32)
    src1 = env.D[15]
    obj.operands = [dst, src1, src2]
    if "CADD" in obj.mnemonic:
        obj.operands = [dst, src1, dst, src2]
    obj.type = type_data_processing

@ispec("16<[ ~const4(4) a(4) {9a} ]", mnemonic="ADD")
@ispec("16<[ ~const4(4) a(4) {ba} ]", mnemonic="EQ")
@ispec("16<[ ~const4(4) a(4) {fa} ]", mnemonic="LT")
@ispec("16<[ ~const4(4) a(4) {82} ]", mnemonic="MOV")
def tricore_ddc_arithmetic(obj, const4, a):
    dst = env.D[15]
    src2 = env.cst(const4.int(-1),32)
    src1 = env.D[a]
    obj.operands = [dst, src1, src2]
    if obj.mnemonic=="MOV":
        obj.operands = [src1,src2]
    obj.type = type_data_processing

@ispec("16<[ ~const4(4) a(4) {d2} ]", mnemonic="MOV")
def tricore_ec_arithmetic(obj, const4, a):
    dst = env.E[a]
    src = env.cst(const4.int(-1),64)
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("16<[ const4(4) a(4) {a0} ]", mnemonic="MOV_A")
def tricore_ec_arithmetic(obj, const4, a):
    dst = env.A[a]
    src = env.cst(const4,32)
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("16<[ const8(8) {16} ]", mnemonic="AND")
@ispec("16<[ const8(8) {da} ]", mnemonic="MOV")
@ispec("16<[ const8(8) {96} ]", mnemonic="OR")
def tricore_ddc_arithmetic(obj, const8):
    dst = env.D[15]
    src2 = env.cst(const8,32)
    src1 = env.D[15]
    obj.operands = [dst, src1, src2]
    if obj.mnemonic=="MOV":
        obj.operands = [src1,src2]
    obj.type = type_data_processing

@ispec("16<[ b(4) a(4) {42} ]", mnemonic="ADD")
@ispec("16<[ b(4) a(4) {26} ]", mnemonic="AND")
@ispec("16<[ b(4) a(4) {a6} ]", mnemonic="OR")
@ispec("16<[ b(4) a(4) {a2} ]", mnemonic="SUB")
@ispec("16<[ b(4) a(4) {62} ]", mnemonic="SUBS")
@ispec("16<[ b(4) a(4) {c6} ]", mnemonic="XOR")
def tricore_dd_arithmetic(obj, b, a):
    dst = env.D[a]
    src1 = env.D[a]
    src2 = env.D[b]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ b(4) a(4) {02} ]", mnemonic="MOV"    , _dst=env.D, _src=env.D)
@ispec("16<[ b(4) a(4) {60} ]", mnemonic="MOV_A"  , _dst=env.A, _src=env.D)
@ispec("16<[ b(4) a(4) {40} ]", mnemonic="MOV_AA" , _dst=env.A, _src=env.A)
@ispec("16<[ b(4) a(4) {80} ]", mnemonic="MOV_D"  , _dst=env.D, _src=env.A)
def tricore_mov(obj, b, a, _dst, _src):
    dst = _dst[a]
    src = _src[b]
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("16<[ b(4) a(4) {12} ]", mnemonic="ADD")
@ispec("16<[ b(4) a(4) {2a} ]", mnemonic="CMOV")
@ispec("16<[ b(4) a(4) {6a} ]", mnemonic="CMOVN")
@ispec("16<[ b(4) a(4) {52} ]", mnemonic="SUB")
def tricore_dd_arithmetic(obj, b, a):
    dst = env.D[a]
    src1 = env.D[15]
    src2 = env.D[b]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ b(4) a(4) {1a} ]", mnemonic="ADD")
@ispec("16<[ b(4) a(4) {22} ]", mnemonic="ADDS")
@ispec("16<[ b(4) a(4) {3a} ]", mnemonic="EQ")
@ispec("16<[ b(4) a(4) {7a} ]", mnemonic="LT")
@ispec("16<[ b(4) a(4) {5a} ]", mnemonic="SUB")
def tricore_dd_arithmetic(obj, b, a):
    dst = env.D[15]
    src1 = env.D[a]
    src2 = env.D[b]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) {01} ---- b(4) a(4) {01} ]", mnemonic="ADD_A")
@ispec("32<[ c(4) {02} ---- b(4) a(4) {01} ]", mnemonic="SUB_A")
def tricore_aaa_arithmetic(obj, c, b, a):
    src1 = env.A[a]
    src2 = env.A[b]
    dst = env.A[c]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ ~const4(4) a(4) {b0} ]", mnemonic="ADD_A")
def tricore_aac_arithmetic(obj, const4, a):
    dst = env.A[a]
    src2 = env.cst(const4.int(-1),32)
    src1 = env.A[a]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ const8(8) {20} ]", mnemonic="SUB_A")
def tricore_aac_arithmetic(obj, const8, a):
    dst = env.A[10]
    src2 = env.cst(const8,32)
    src1 = env.A[10]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ b(4) a(4) {30} ]", mnemonic="ADD_A")
def tricore_aa_arithmetic(obj, b, a):
    dst = env.A[a]
    src1 = env.A[a]
    src2 = env.A[b]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) ~const16(16) a(4) {1b} ]", mnemonic="ADDI")
@ispec("32<[ c(4) ~const16(16) a(4) {9b} ]", mnemonic="ADDIH")
def tricore_di_arithmetic(obj, c, const16, a):
    src1 = env.D[a]
    src2 = env.cst(const16.int(-1),32)
    if self.mnemonic=="ADDIH": src2=src2<<16
    dst = env.D[c]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) ~const16(16) a(4) {11} ]", mnemonic="ADDIH_A")
def tricore_ai_arithmetic(obj, c, const16, a):
    src1 = env.A[a]
    src2 = env.cst(const16.int(-1),32)<<16
    dst = env.A[c]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) {60} -- n(2) b(4) a(4) {01} ]", mnemonic="ADDSC_A")
def tricore_aaa_arithmetic(obj, c, n, b, a):
    src1 = env.D[a]
    src2 = env.A[b]
    dst = env.A[c]
    obj.operands = [dst, src2, src1, env.cst(n,2)]
    obj.type = type_data_processing

@ispec("32<[ c(4) {62} ---- b(4) a(4) {01} ]", mnemonic="ADDSC_AT")
def tricore_aaa_arithmetic(obj, c, b, a):
    src1 = env.D[a]
    src2 = env.A[b]
    dst = env.A[c]
    obj.operands = [dst, src2, src1]
    obj.type = type_data_processing

@ispec("16<[ b(4) a(4) n(2) 010000 ]", mnemonic="ADDSC_A")
def tricore_aa_arithmetic(obj, b, a, n):
    dst = env.A[a]
    src1 = env.D[15]
    src2 = env.A[b]
    obj.operands = [dst, src2, src1, env.cst(n,2)]
    obj.type = type_data_processing

@ispec("32<[ off2(4) 10 1110 off1(6) b(4) ---- {89} ]", mnemonic="CACHEA_I",  mode="Short-offset")
@ispec("32<[ off2(4) 00 1110 off1(6) b(4) ---- {a9} ]", mnemonic="CACHEA_I",  mode="Bit-reverse")
@ispec("32<[ off2(4) 01 1110 off1(6) b(4) ---- {a9} ]", mnemonic="CACHEA_I",  mode="Circular")
@ispec("32<[ off2(4) 00 1110 off1(6) b(4) ---- {89} ]", mnemonic="CACHEA_I",  mode="Post-increment")
@ispec("32<[ off2(4) 01 1110 off1(6) b(4) ---- {89} ]", mnemonic="CACHEA_I",  mode="Pre-increment")
@ispec("32<[ off2(4) 10 1100 off1(6) b(4) ---- {89} ]", mnemonic="CACHEA_W",  mode="Short-offset")
@ispec("32<[ off2(4) 00 1100 off1(6) b(4) ---- {a9} ]", mnemonic="CACHEA_W",  mode="Bit-reverse")
@ispec("32<[ off2(4) 01 1100 off1(6) b(4) ---- {a9} ]", mnemonic="CACHEA_W",  mode="Circular")
@ispec("32<[ off2(4) 00 1100 off1(6) b(4) ---- {89} ]", mnemonic="CACHEA_W",  mode="Post-increment")
@ispec("32<[ off2(4) 01 1100 off1(6) b(4) ---- {89} ]", mnemonic="CACHEA_W",  mode="Pre-increment")
@ispec("32<[ off2(4) 10 1101 off1(6) b(4) ---- {89} ]", mnemonic="CACHEA_WI", mode="Short-offset")
@ispec("32<[ off2(4) 00 1101 off1(6) b(4) ---- {a9} ]", mnemonic="CACHEA_WI", mode="Bit-reverse")
@ispec("32<[ off2(4) 01 1101 off1(6) b(4) ---- {a9} ]", mnemonic="CACHEA_WI", mode="Circular")
@ispec("32<[ off2(4) 00 1101 off1(6) b(4) ---- {89} ]", mnemonic="CACHEA_WI", mode="Post-increment")
@ispec("32<[ off2(4) 01 1101 off1(6) b(4) ---- {89} ]", mnemonic="CACHEA_WI", mode="Pre-increment")
@ispec("32<[ off2(4) 10 1011 off1(6) b(4) ---- {89} ]", mnemonic="CACHEI_W",  mode="Short-offset")
@ispec("32<[ off2(4) 00 1011 off1(6) b(4) ---- {89} ]", mnemonic="CACHEI_W",  mode="Post-increment")
@ispec("32<[ off2(4) 01 1011 off1(6) b(4) ---- {89} ]", mnemonic="CACHEI_W",  mode="Pre-increment")
@ispec("32<[ off2(4) 10 1010 off1(6) b(4) ---- {89} ]", mnemonic="CACHEI_I",  mode="Short-offset")
@ispec("32<[ off2(4) 00 1010 off1(6) b(4) ---- {89} ]", mnemonic="CACHEI_I",  mode="Post-increment")
@ispec("32<[ off2(4) 01 1010 off1(6) b(4) ---- {89} ]", mnemonic="CACHEI_I",  mode="Pre-increment")
@ispec("32<[ off2(4) 10 1111 off1(6) b(4) ---- {89} ]", mnemonic="CACHEI_WI", mode="Short-offset")
@ispec("32<[ off2(4) 00 1111 off1(6) b(4) ---- {89} ]", mnemonic="CACHEI_WI", mode="Post-increment")
@ispec("32<[ off2(4) 01 1111 off1(6) b(4) ---- {89} ]", mnemonic="CACHEI_WI", mode="Pre-increment")
def tricore_cache(obj, off2, off1, b):
    src2 = env.A[b]
    src1 = env.cst((off2<<6)+off1,10)
    obj.operands = [src2, src1]
    obj.type = type_system

@ispec("32<[ off2(4) 10 0011 off1(6) b(4) a(4) {49} ]", mnemonic="CMPSWAP_W", mode="Short-offset")
@ispec("32<[ off2(4) 00 0011 off1(6) b(4) a(4) {69} ]", mnemonic="CMPSWAP_W", mode="Bit-reverse")
@ispec("32<[ off2(4) 01 0011 off1(6) b(4) a(4) {69} ]", mnemonic="CMPSWAP_W", mode="Circular")
@ispec("32<[ off2(4) 00 0011 off1(6) b(4) a(4) {49} ]", mnemonic="CMPSWAP_W", mode="Post-increment")
@ispec("32<[ off2(4) 01 0011 off1(6) b(4) a(4) {49} ]", mnemonic="CMPSWAP_W", mode="Pre-increment")
@ispec("32<[ off2(4) 10 0010 off1(6) b(4) a(4) {49} ]", mnemonic="SWAPMSK_W", mode="Short-offset")
@ispec("32<[ off2(4) 00 0010 off1(6) b(4) a(4) {69} ]", mnemonic="SWAPMSK_W", mode="Bit-reverse")
@ispec("32<[ off2(4) 01 0010 off1(6) b(4) a(4) {69} ]", mnemonic="SWAPMSK_W", mode="Circular")
@ispec("32<[ off2(4) 00 0010 off1(6) b(4) a(4) {49} ]", mnemonic="SWAPMSK_W", mode="Post-increment")
@ispec("32<[ off2(4) 01 0010 off1(6) b(4) a(4) {49} ]", mnemonic="SWAPMSK_W", mode="Pre-increment")
def tricore_swap(obj, off2, off1, b, a):
    if a%2:
        raise InstructionError(obj)
    dst = env.D[a]
    src1 = env.A[b]
    src2 = env.cst((off2<<6)+off1,10)
    src3 = env.E[a]
    obj.operands = [dst, src1, src2, src3]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 000 ~const9(9) a(4) {ab} ]", mnemonic="CADD")
@ispec("32<[ c(4) d(4) 001 ~const9(9) a(4) {ab} ]", mnemonic="CADDN")
@ispec("32<[ c(4) d(4) 001 ~const9(9) a(4) {13} ]", mnemonic="MADD", opt4="32+(32+K9)->32")
@ispec("32<[ c(4) d(4) 101 ~const9(9) a(4) {13} ]", mnemonic="MADDS",  opt4="32+(32+K9)->32")
@ispec("32<[ c(4) d(4) 100 ~const9(9) a(4) {13} ]", mnemonic="MADDS_U", opt4="32+(32+K9)->32")
@ispec("32<[ c(4) d(4) 001 ~const9(9) a(4) {33} ]", mnemonic="MSUB", opt4="32+(32+K9)->32")
@ispec("32<[ c(4) d(4) 101 ~const9(9) a(4) {33} ]", mnemonic="MSUBS",  opt4="32+(32+K9)->32")
@ispec("32<[ c(4) d(4) 100 ~const9(9) a(4) {33} ]", mnemonic="MSUBS_U", opt4="32+(32+K9)->32")
@ispec("32<[ c(4) d(4) 100 ~const9(9) a(4) {ab} ]", mnemonic="SEL")
@ispec("32<[ c(4) d(4) 101 ~const9(9) a(4) {ab} ]", mnemonic="SELN")
def tricore_cond_ddc(obj, c, d, const9, a):
    cond = env.D[d]
    src1 = env.D[a]
    src2 = env.cst(const9.int(-1),32)
    dst = env.D[c]
    obj.operands = [dst, cond, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 011 ~const9(9) a(4) {13} ]", mnemonic="MADD", opt4="64+(32+K9)->64")
@ispec("32<[ c(4) d(4) 111 ~const9(9) a(4) {13} ]", mnemonic="MADDS", opt4="64+(32+K9)->64")
@ispec("32<[ c(4) d(4) 010 ~const9(9) a(4) {13} ]", mnemonic="MADD_U", opt4="64+(32+K9)->64")
@ispec("32<[ c(4) d(4) 111 ~const9(9) a(4) {13} ]", mnemonic="MADDS_U", opt4="64+(32+K9)->64")
@ispec("32<[ c(4) d(4) 011 ~const9(9) a(4) {33} ]", mnemonic="MSUB", opt4="64+(32+K9)->64")
@ispec("32<[ c(4) d(4) 111 ~const9(9) a(4) {33} ]", mnemonic="MSUBS", opt4="64+(32+K9)->64")
@ispec("32<[ c(4) d(4) 010 ~const9(9) a(4) {33} ]", mnemonic="MSUB_U", opt4="64+(32+K9)->64")
@ispec("32<[ c(4) d(4) 111 ~const9(9) a(4) {33} ]", mnemonic="MSUBS_U", opt4="64+(32+K9)->64")
def tricore_cond_eec(obj, c, d, const9, a):
    cond = env.E[d]
    src1 = env.D[a]
    src2 = env.cst(const9.int(-1),32)
    dst = env.E[c]
    obj.operands = [dst, cond, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 011010 n(2) b(4) a(4) {83} ]", mnemonic="MADD_H", op4="LL")
@ispec("32<[ c(4) d(4) 011001 n(2) b(4) a(4) {83} ]", mnemonic="MADD_H", op4="LU")
@ispec("32<[ c(4) d(4) 011000 n(2) b(4) a(4) {83} ]", mnemonic="MADD_H", op4="UL")
@ispec("32<[ c(4) d(4) 011011 n(2) b(4) a(4) {83} ]", mnemonic="MADD_H", op4="UU")
@ispec("32<[ c(4) d(4) 111010 n(2) b(4) a(4) {83} ]", mnemonic="MADDS_H", op4="LL")
@ispec("32<[ c(4) d(4) 111001 n(2) b(4) a(4) {83} ]", mnemonic="MADDS_H", op4="LU")
@ispec("32<[ c(4) d(4) 111000 n(2) b(4) a(4) {83} ]", mnemonic="MADDS_H", op4="UL")
@ispec("32<[ c(4) d(4) 111011 n(2) b(4) a(4) {83} ]", mnemonic="MADDS_H", op4="UU")
@ispec("32<[ c(4) d(4) 000010 n(2) b(4) a(4) {43} ]", mnemonic="MADD_Q", op4="32+(32*32)Up->32")
@ispec("32<[ c(4) d(4) 011011 n(2) b(4) a(4) {43} ]", mnemonic="MADD_Q", op4="64+(32*32)->64")
@ispec("32<[ c(4) d(4) 000001 n(2) b(4) a(4) {43} ]", mnemonic="MADD_Q", op4="32+(16L*32)Up->32")
@ispec("32<[ c(4) d(4) 011001 n(2) b(4) a(4) {43} ]", mnemonic="MADD_Q", op4="64+(16L*32)->64")
@ispec("32<[ c(4) d(4) 000000 n(2) b(4) a(4) {43} ]", mnemonic="MADD_Q", op4="32+(16U*32)Up->32")
@ispec("32<[ c(4) d(4) 011000 n(2) b(4) a(4) {43} ]", mnemonic="MADD_Q", op4="64+(16U*32)->64")
@ispec("32<[ c(4) d(4) 000101 n(2) b(4) a(4) {43} ]", mnemonic="MADD_Q", op4="32+(16L*16L)->32")
@ispec("32<[ c(4) d(4) 011101 n(2) b(4) a(4) {43} ]", mnemonic="MADD_Q", op4="64+(16L*16L)->64")
@ispec("32<[ c(4) d(4) 000100 n(2) b(4) a(4) {43} ]", mnemonic="MADD_Q", op4="32+(16U*16U)->32")
@ispec("32<[ c(4) d(4) 011100 n(2) b(4) a(4) {43} ]", mnemonic="MADD_Q", op4="64+(16U*16U)->64")
@ispec("32<[ c(4) d(4) 100010 n(2) b(4) a(4) {43} ]", mnemonic="MADDS_Q", op4="32+(32*32)Up->32")
@ispec("32<[ c(4) d(4) 111011 n(2) b(4) a(4) {43} ]", mnemonic="MADDS_Q", op4="64+(32*32)->64")
@ispec("32<[ c(4) d(4) 100001 n(2) b(4) a(4) {43} ]", mnemonic="MADDS_Q", op4="32+(16L*32)Up->32")
@ispec("32<[ c(4) d(4) 111001 n(2) b(4) a(4) {43} ]", mnemonic="MADDS_Q", op4="64+(16L*32)->64")
@ispec("32<[ c(4) d(4) 100000 n(2) b(4) a(4) {43} ]", mnemonic="MADDS_Q", op4="32+(16U*32)Up->32")
@ispec("32<[ c(4) d(4) 111000 n(2) b(4) a(4) {43} ]", mnemonic="MADDS_Q", op4="64+(16U*32)->64")
@ispec("32<[ c(4) d(4) 100101 n(2) b(4) a(4) {43} ]", mnemonic="MADDS_Q", op4="32+(16L*16L)->32")
@ispec("32<[ c(4) d(4) 111101 n(2) b(4) a(4) {43} ]", mnemonic="MADDS_Q", op4="64+(16L*16L)->64")
@ispec("32<[ c(4) d(4) 100100 n(2) b(4) a(4) {43} ]", mnemonic="MADDS_Q", op4="32+(16U*16U)->32")
@ispec("32<[ c(4) d(4) 111100 n(2) b(4) a(4) {43} ]", mnemonic="MADDS_Q", op4="64+(16U*16U)->64")
@ispec("32<[ c(4) d(4) 011010 n(2) b(4) a(4) {a3} ]", mnemonic="MSUB_H", op4="LL")
@ispec("32<[ c(4) d(4) 011001 n(2) b(4) a(4) {a3} ]", mnemonic="MSUB_H", op4="LU")
@ispec("32<[ c(4) d(4) 011000 n(2) b(4) a(4) {a3} ]", mnemonic="MSUB_H", op4="UL")
@ispec("32<[ c(4) d(4) 011011 n(2) b(4) a(4) {a3} ]", mnemonic="MSUB_H", op4="UU")
@ispec("32<[ c(4) d(4) 111010 n(2) b(4) a(4) {a3} ]", mnemonic="MSUBS_H", op4="LL")
@ispec("32<[ c(4) d(4) 111001 n(2) b(4) a(4) {a3} ]", mnemonic="MSUBS_H", op4="LU")
@ispec("32<[ c(4) d(4) 111000 n(2) b(4) a(4) {a3} ]", mnemonic="MSUBS_H", op4="UL")
@ispec("32<[ c(4) d(4) 111011 n(2) b(4) a(4) {a3} ]", mnemonic="MSUBS_H", op4="UU")
@ispec("32<[ c(4) d(4) 000010 n(2) b(4) a(4) {63} ]", mnemonic="MSUB_Q", op4="32+(32*32)Up->32")
@ispec("32<[ c(4) d(4) 011011 n(2) b(4) a(4) {63} ]", mnemonic="MSUB_Q", op4="64+(32*32)->64")
@ispec("32<[ c(4) d(4) 000001 n(2) b(4) a(4) {63} ]", mnemonic="MSUB_Q", op4="32+(16L*32)Up->32")
@ispec("32<[ c(4) d(4) 011001 n(2) b(4) a(4) {63} ]", mnemonic="MSUB_Q", op4="64+(16L*32)->64")
@ispec("32<[ c(4) d(4) 000000 n(2) b(4) a(4) {63} ]", mnemonic="MSUB_Q", op4="32+(16U*32)Up->32")
@ispec("32<[ c(4) d(4) 011000 n(2) b(4) a(4) {63} ]", mnemonic="MSUB_Q", op4="64+(16U*32)->64")
@ispec("32<[ c(4) d(4) 000101 n(2) b(4) a(4) {63} ]", mnemonic="MSUB_Q", op4="32+(16L*16L)->32")
@ispec("32<[ c(4) d(4) 011101 n(2) b(4) a(4) {63} ]", mnemonic="MSUB_Q", op4="64+(16L*16L)->64")
@ispec("32<[ c(4) d(4) 000100 n(2) b(4) a(4) {63} ]", mnemonic="MSUB_Q", op4="32+(16U*16U)->32")
@ispec("32<[ c(4) d(4) 011100 n(2) b(4) a(4) {63} ]", mnemonic="MSUB_Q", op4="64+(16U*16U)->64")
@ispec("32<[ c(4) d(4) 100010 n(2) b(4) a(4) {63} ]", mnemonic="MSUBS_Q", op4="32+(32*32)Up->32")
@ispec("32<[ c(4) d(4) 111011 n(2) b(4) a(4) {63} ]", mnemonic="MSUBS_Q", op4="64+(32*32)->64")
@ispec("32<[ c(4) d(4) 100001 n(2) b(4) a(4) {63} ]", mnemonic="MSUBS_Q", op4="32+(16L*32)Up->32")
@ispec("32<[ c(4) d(4) 111001 n(2) b(4) a(4) {63} ]", mnemonic="MSUBS_Q", op4="64+(16L*32)->64")
@ispec("32<[ c(4) d(4) 100000 n(2) b(4) a(4) {63} ]", mnemonic="MSUBS_Q", op4="32+(16U*32)Up->32")
@ispec("32<[ c(4) d(4) 111000 n(2) b(4) a(4) {63} ]", mnemonic="MSUBS_Q", op4="64+(16U*32)->64")
@ispec("32<[ c(4) d(4) 100101 n(2) b(4) a(4) {63} ]", mnemonic="MSUBS_Q", op4="32+(16L*16L)->32")
@ispec("32<[ c(4) d(4) 111101 n(2) b(4) a(4) {63} ]", mnemonic="MSUBS_Q", op4="64+(16L*16L)->64")
@ispec("32<[ c(4) d(4) 100100 n(2) b(4) a(4) {63} ]", mnemonic="MSUBS_Q", op4="32+(16U*16U)->32")
@ispec("32<[ c(4) d(4) 111100 n(2) b(4) a(4) {63} ]", mnemonic="MSUBS_Q", op4="64+(16U*16U)->64")
def tricore_cond_eec(obj, c, d, n, b, a):
    cond = env.E[d]
    src1 = env.D[a]
    src2 = env.D[b]
    dst = env.E[c]
    obj.operands = [dst, cond, src1, src2, env.cst(n,2)]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) 0000 ---- b(4) a(4) {2b} ]", mnemonic="CADD")
@ispec("32<[ c(4) d(4) 0001 ---- b(4) a(4) {2b} ]", mnemonic="CADDN")
@ispec("32<[ c(4) d(4) 0010 ---- b(4) a(4) {2b} ]", mnemonic="CSUB")
@ispec("32<[ c(4) d(4) 0011 ---- b(4) a(4) {2b} ]", mnemonic="CSUBN")
@ispec("32<[ c(4) d(4)      {0a} b(4) a(4) {03} ]", mnemonic="MADD", opt4="32+(32*32)->32")
@ispec("32<[ c(4) d(4)      {8a} b(4) a(4) {03} ]", mnemonic="MADDS", opt4="32+(32*32)->32")
@ispec("32<[ c(4) d(4)      {88} b(4) a(4) {03} ]", mnemonic="MADDS_U", opt4="32+(32*32)->32")
@ispec("32<[ c(4) d(4) 0100 ---- b(4) a(4) {2b} ]", mnemonic="SEL")
@ispec("32<[ c(4) d(4) 0101 ---- b(4) a(4) {2b} ]", mnemonic="SELN")
def tricore_cond_ddd(obj, c, d, b, a):
    cond = env.D[d]
    src1 = env.D[a]
    src2 = env.D[b]
    dst = env.D[c]
    obj.operands = [dst, cond, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) d(4) {6a}      b(4) a(4) {03} ]", mnemonic="MADD", opt4="64+(32*32)->64")
@ispec("32<[ c(4) d(4) {ea}      b(4) a(4) {03} ]", mnemonic="MADDS", opt4="64+(32*32)->64")
@ispec("32<[ c(4) d(4) {68}      b(4) a(4) {03} ]", mnemonic="MADD_U", opt4="64+(32*32)->64")
@ispec("32<[ c(4) d(4) {e8}      b(4) a(4) {03} ]", mnemonic="MADDS_U", opt4="64+(32*32)->64")
def tricore_cond_ddd(obj, c, d, b, a):
    cond = env.E[d]
    src1 = env.D[a]
    src2 = env.D[b]
    dst = env.E[c]
    obj.operands = [dst, cond, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ c(4) {1c} ---- ---- a(4) {0f} ]", mnemonic="CLO")
@ispec("32<[ c(4) {7d} ---- ---- a(4) {0f} ]", mnemonic="CLO_H")
@ispec("32<[ c(4) {1d} ---- ---- a(4) {0f} ]", mnemonic="CLS")
@ispec("32<[ c(4) {7e} ---- ---- a(4) {0f} ]", mnemonic="CLS_H")
@ispec("32<[ c(4) {1b} ---- ---- a(4) {0f} ]", mnemonic="CLZ")
@ispec("32<[ c(4) {7c} ---- ---- a(4) {0f} ]", mnemonic="CLZ_H")
@ispec("32<[ c(4) {5e} ---- ---- a(4) {0b} ]", mnemonic="SAT_B")
@ispec("32<[ c(4) {5f} ---- ---- a(4) {0b} ]", mnemonic="SAT_BU")
@ispec("32<[ c(4) {7e} ---- ---- a(4) {0b} ]", mnemonic="SAT_H")
@ispec("32<[ c(4) {7f} ---- ---- a(4) {0b} ]", mnemonic="SAT_HU")
def tricore_dd_arithmetic(obj, c, a):
    src = env.D[a]
    dst = env.D[c]
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("16<[ 1010 ---- {00} ]", mnemonic="DEBUG")
@ispec("16<[ 0000 ---- {00} ]", mnemonic="NOP")
def tricore_system(obj):
    obj.operands = []
    obj.type = type_system

@ispec("16<[ 0111 ---- {00} ]", mnemonic="FRET")
@ispec("16<[ 1001 ---- {00} ]", mnemonic="RET")
@ispec("16<[ 1000 ---- {00} ]", mnemonic="RFE")
def tricore_ret(obj):
    obj.operands = []
    obj.type = type_control_flow

@ispec("32<[ ---- 000100 ---------- ---- {0d} ]", mnemonic="DEBUG")
@ispec("32<[ ---- 001101 ---------- ---- {0d} ]", mnemonic="DISABLE")
@ispec("32<[ ---- 010010 ---------- ---- {0d} ]", mnemonic="DSYNC")
@ispec("32<[ ---- 001100 ---------- ---- {0d} ]", mnemonic="ENABLE")
@ispec("32<[ ---- 010011 ---------- ---- {0d} ]", mnemonic="ISYNC")
@ispec("32<[ ---- 010101 ---------- ---- {0d} ]", mnemonic="TRAPSV")
@ispec("32<[ ---- 010100 ---------- ---- {0d} ]", mnemonic="TRAPV")
@ispec("32<[ ---- 000000 ---------- ---- {0d} ]", mnemonic="NOP")
@ispec("32<[ ---- 001001 ---------- ---- {0d} ]", mnemonic="RSLCX")
@ispec("32<[ ---- 000000 ---------- ---- {2f} ]", mnemonic="RSTV")
@ispec("32<[ ---- 001000 ---------- ---- {0d} ]", mnemonic="SVLCX")
@ispec("32<[ ---- 010110 ---------- ---- {0d} ]", mnemonic="WAIT")
def tricore_system(obj):
    obj.operands = []
    obj.type = type_system

@ispec("32<[ ---- 000011 ---------- ---- {0d} ]", mnemonic="FRET")
@ispec("32<[ ---- 000110 ---------- ---- {0d} ]", mnemonic="RET")
@ispec("32<[ ---- 000111 ---------- ---- {0d} ]", mnemonic="RFE")
@ispec("32<[ ---- 000101 ---------- ---- {0d} ]", mnemonic="RFM")
def tricore_ret(obj):
    obj.operands = []
    obj.type = type_control_flow

@ispec("32<[ ---- 001111 ---------- a(4) {0d} ]", mnemonic="DISABLE")
@ispec("32<[ ---- 001110 ---------- a(4) {0d} ]", mnemonic="RESTORE")
def tricore_system(obj, a):
    obj.operands = [env.D[a]]
    obj.type = type_system

@ispec("32<[ c(4) d(4) 1101 -- 00 b(4) ---- {6b} ]", mnemonic="DVADJ")
@ispec("32<[ c(4) d(4) 1111 -- 00 b(4) ---- {6b} ]", mnemonic="DVSTEP")
@ispec("32<[ c(4) d(4) 1110 -- 00 b(4) ---- {6b} ]", mnemonic="DVSTEP_U")
@ispec("32<[ c(4) d(4) 1010 -- 00 b(4) ---- {6b} ]", mnemonic="IXMAX")
@ispec("32<[ c(4) d(4) 1011 -- 00 b(4) ---- {6b} ]", mnemonic="IXMAX_U")
@ispec("32<[ c(4) d(4) 1000 -- 00 b(4) ---- {6b} ]", mnemonic="IXMIN")
@ispec("32<[ c(4) d(4) 1001 -- 00 b(4) ---- {6b} ]", mnemonic="IXMIN_U")
def tricore_eee(obj, c, d, b):
    if d%2 or b%2 or c%2:
        raise InstructionError(obj)
    src1 = env.E[d]
    src2 = env.E[b]
    dst = env.E[c]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ ~const4(4) disp(4) {1e} ]", mnemonic="JEQ", _off=0)
@ispec("16<[ ~const4(4) disp(4) {9e} ]", mnemonic="JEQ", _off=16)
@ispec("16<[ ~const4(4) disp(4) {5e} ]", mnemonic="JNE", _off=0)
@ispec("16<[ ~const4(4) disp(4) {de} ]", mnemonic="JNE", _off=16)
def tricore_jcc(obj, const4, disp, _off):
    dst = env.D[15]
    src1 = env.cst(const4.int(-1),32)
    src2 = env.cst(disp,32)+_off
    obj.operands = [dst, src1, src2]
    obj.type = type_control_flow

@ispec("16<[ b(4) disp(4) {3e} ]", mnemonic="JEQ", _off=0)
@ispec("16<[ b(4) disp(4) {be} ]", mnemonic="JEQ", _off=16)
@ispec("16<[ b(4) disp(4) {7e} ]", mnemonic="JNE", _off=0)
@ispec("16<[ b(4) disp(4) {fe} ]", mnemonic="JNE", _off=16)
def tricore_jcc(obj, b, disp, _off):
    dst = env.D[15]
    src1 = env.D[b]
    src2 = env.cst(disp,32)+_off
    obj.operands = [dst, src1, src2]
    obj.type = type_control_flow

@ispec("16<[ b(4) disp(4) {ce} ]", mnemonic="JGEZ")
@ispec("16<[ b(4) disp(4) {4e} ]", mnemonic="JGTZ")
@ispec("16<[ b(4) disp(4) {8e} ]", mnemonic="JLEZ")
@ispec("16<[ b(4) disp(4) {0e} ]", mnemonic="JLTZ")
@ispec("16<[ b(4) disp(4) {f6} ]", mnemonic="JNZ")
@ispec("16<[ b(4) disp(4) {76} ]", mnemonic="JZ")
def tricore_jcc(obj, b, disp):
    src1 = env.D[b]
    src2 = env.cst(disp,32)
    obj.operands = [src1, src2]
    obj.type = type_control_flow

@ispec("32<[ 0 ~disp(15) const(4) a(4) {df} ]", mnemonic="JEQ")
@ispec("32<[ 1 ~disp(15) const(4) a(4) {df} ]", mnemonic="JNE")
@ispec("32<[ 0 ~disp(15) const(4) a(4) {ff} ]", mnemonic="JGE")
@ispec("32<[ 1 ~disp(15) const(4) a(4) {ff} ]", mnemonic="JGE_U")
@ispec("32<[ 0 ~disp(15) const(4) a(4) {bf} ]", mnemonic="JLT")
@ispec("32<[ 1 ~disp(15) const(4) a(4) {bf} ]", mnemonic="JLT_U")
@ispec("32<[ 1 ~disp(15) const(4) a(4) {9f} ]", mnemonic="JNED")
@ispec("32<[ 0 ~disp(15) const(4) a(4) {9f} ]", mnemonic="JNEI")
def tricore_jcc(obj, disp, const, a):
    src1 = env.D[a]
    src2 = env.cst(const,4)
    obj.operands = [src1, src2, env.cst(disp.int(-1),32)]
    obj.type = type_control_flow

@ispec("32<[ 0 ~disp(15) b(4) a(4) {5f} ]", mnemonic="JEQ")
@ispec("32<[ 1 ~disp(15) b(4) a(4) {5f} ]", mnemonic="JNE")
@ispec("32<[ 0 ~disp(15) b(4) a(4) {7f} ]", mnemonic="JGE")
@ispec("32<[ 1 ~disp(15) b(4) a(4) {7f} ]", mnemonic="JGE_U")
@ispec("32<[ 0 ~disp(15) b(4) a(4) {3f} ]", mnemonic="JLT")
@ispec("32<[ 1 ~disp(15) b(4) a(4) {3f} ]", mnemonic="JLT_U")
@ispec("32<[ 1 ~disp(15) b(4) a(4) {1f} ]", mnemonic="JNED")
@ispec("32<[ 0 ~disp(15) b(4) a(4) {1f} ]", mnemonic="JNEI")
def tricore_jcc(obj, disp, b, a):
    src1 = env.D[a]
    src2 = env.D[b]
    obj.operands = [src1, src2, env.cst(disp.int(-1),32)]
    obj.type = type_control_flow

@ispec("32<[ 0 ~disp(15) b(4) a(4) {7d} ]", mnemonic="JEQ_A")
@ispec("32<[ 1 ~disp(15) b(4) a(4) {7d} ]", mnemonic="JNE_A")
def tricore_jcc(obj, disp, b, a):
    src1 = env.A[a]
    src2 = env.A[b]
    obj.operands = [src1, src2, env.cst(disp.int(-1),32)]
    obj.type = type_control_flow

@ispec("32<[ 1 ~disp(15) ---- a(4) {bd} ]", mnemonic="JNZ_A")
@ispec("32<[ 0 ~disp(15) ---- a(4) {bd} ]", mnemonic="JZ_A")
def tricore_jcc(obj, disp, a):
    src1 = env.A[a]
    src2 = env.A[b]
    obj.operands = [src1, src2, env.cst(disp.int(-1),32)]
    obj.type = type_control_flow

@ispec("32<[ 0 ~disp(15) b(4) ---- {fd} ]", mnemonic="LOOP")
@ispec("32<[ 1 ~disp(15) b(4) ---- {fd} ]", mnemonic="LOOPU")
def tricore_jcc(obj, disp, b):
    src1 = env.A[b]
    src2 =  env.cst(disp.int(-1)*2,32)
    obj.operands = [src1, src2]
    if obj.mnemonic=="LOOPU":
        obj.operands = [src2]
    obj.type = type_control_flow

@ispec("16<[ b(4) disp(4) {7c} ]", mnemonic="JNZ_A")
@ispec("16<[ b(4) disp(4) {bc} ]", mnemonic="JZ_A")
def tricore_jcc(obj, b, disp):
    src1 = env.A[b]
    src2 = env.cst(disp,32)
    obj.operands = [src1, src2]
    obj.type = type_control_flow

@ispec("16<[ b(4) #disp(4) {fc} ]", mnemonic="LOOP")
def tricore_jcc(obj, b, disp):
    src1 = env.A[b]
    src2 = env.cst(int(("1"*27)+disp+"0",2),32)
    obj.operands = [src1, src2]
    obj.type = type_control_flow

@ispec("16<[ 0000 a(4) {dc} ]", mnemonic="JI")
def tricore_ji(obj, a):
    src = env.A[a]
    obj.operands = [src]
    obj.type = type_control_flow

@ispec("16<[ 0000 a(4) {46} ]", mnemonic="NOT")
@ispec("16<[ 0101 a(4) {32} ]", mnemonic="RSUB")
@ispec("16<[ 0000 a(4) {32} ]", mnemonic="SAT_B")
@ispec("16<[ 0001 a(4) {32} ]", mnemonic="SAT_BU")
@ispec("16<[ 0010 a(4) {32} ]", mnemonic="SAT_H")
@ispec("16<[ 0011 a(4) {32} ]", mnemonic="SAT_HU")
def tricore_a(obj, a):
    src = env.D[a]
    obj.operands = [src]
    obj.type = type_data_processing

@ispec("16<[ n(4) disp(4) {ae} ]", mnemonic="JNZ_T")
@ispec("16<[ n(4) disp(4) {2e} ]", mnemonic="JZ_T")
def tricore_ji(obj, n, disp):
    obj.operands = [env.D[15][n:n+1], env.cst(disp,32)]
    obj.type = type_control_flow

@ispec("32<[ 1 ~disp(15) n(4) a(4) h 1101111 ]", mnemonic="JNZ_T")
@ispec("32<[ 0 ~disp(15) n(4) a(4) h 1101111 ]", mnemonic="JZ_T")
def tricore_jcc(obj, disp, n, a, h):
    i = n+(h<<4)
    src = env.D[a][i:i+1]
    obj.operands = [src, env.cst(disp.int(-1),32)]
    obj.type = type_control_flow

@ispec("32<[ ~off2(4) 10 ~off3(4) ~off1(6) ~off4(4) a(4) {85} ]", mnemonic="LD_A", mode="Absolute")
@ispec("32<[ ~off2(4) 00 ~off3(4) ~off1(6) ~off4(4) a(4) {05} ]", mnemonic="LD_B", mode="Absolute")
@ispec("32<[ ~off2(4) 01 ~off3(4) ~off1(6) ~off4(4) a(4) {05} ]", mnemonic="LD_BU", mode="Absolute")
@ispec("32<[ ~off2(4) 01 ~off3(4) ~off1(6) ~off4(4) a(4) {85} ]", mnemonic="LD_D", mode="Absolute")
@ispec("32<[ ~off2(4) 11 ~off3(4) ~off1(6) ~off4(4) a(4) {85} ]", mnemonic="LD_DA", mode="Absolute")
@ispec("32<[ ~off2(4) 10 ~off3(4) ~off1(6) ~off4(4) a(4) {05} ]", mnemonic="LD_H", mode="Absolute")
@ispec("32<[ ~off2(4) 11 ~off3(4) ~off1(6) ~off4(4) a(4) {05} ]", mnemonic="LD_HU", mode="Absolute")
@ispec("32<[ ~off2(4) 00 ~off3(4) ~off1(6) ~off4(4) a(4) {45} ]", mnemonic="LD_Q", mode="Absolute")
@ispec("32<[ ~off2(4) 00 ~off3(4) ~off1(6) ~off4(4) a(4) {85} ]", mnemonic="LD_W", mode="Absolute")
@ispec("32<[ ~off2(4) 00 ~off3(4) ~off1(6) ~off4(4) a(4) {c5} ]", mnemonic="LEA", mode="Absolute")
def tricore_ld(obj, off2, off3, off1, off4, a):
    dst = env.D[a]
    if obj.mnemonic in ("LD_A", "LEA")  : dst = env.A[a]
    if obj.mnemonic in ("LD_D","LDMST") : dst = env.E[a]
    if obj.mnemonic=="LD_DA": dst = env.P[a]
    src = off1//off2//off3
    obj.operands = [dst, composer([env.cst(src.int(),28),env.cst(off4,4)])]
    obj.type = type_data_processing

@ispec("32<[ ~off2(4) 01 ~off3(4) ~off1(6) ~off4(4) a(4) {c5} ]", mnemonic="LHA", mode="Absolute")
def tricore_ld(obj, off2, off3, off1, off4, a):
    dst = env.A[a]
    src = off1//off2//off3//off4
    obj.operands = [dst, composer([env.cst(0,14),env.cst(src.int(),18)])]
    obj.type = type_data_processing

@ispec("32<[ ~off2(4) 10 ~off3(4) ~off1(6) ~off4(4) a(4) {a5} ]", mnemonic="ST_A", mode="Absolute")
@ispec("32<[ ~off2(4) 00 ~off3(4) ~off1(6) ~off4(4) a(4) {25} ]", mnemonic="ST_B", mode="Absolute")
@ispec("32<[ ~off2(4) 01 ~off3(4) ~off1(6) ~off4(4) a(4) {a5} ]", mnemonic="ST_D", mode="Absolute")
@ispec("32<[ ~off2(4) 11 ~off3(4) ~off1(6) ~off4(4) a(4) {a5} ]", mnemonic="ST_DA", mode="Absolute")
@ispec("32<[ ~off2(4) 10 ~off3(4) ~off1(6) ~off4(4) a(4) {25} ]", mnemonic="ST_H", mode="Absolute")
@ispec("32<[ ~off2(4) 00 ~off3(4) ~off1(6) ~off4(4) a(4) {65} ]", mnemonic="ST_Q", mode="Absolute")
@ispec("32<[ ~off2(4) 00 ~off3(4) ~off1(6) ~off4(4) a(4) {a5} ]", mnemonic="ST_W", mode="Absolute")
@ispec("32<[ ~off2(4) 00 ~off3(4) ~off1(6) ~off4(4) a(4) {e5} ]", mnemonic="SWAP_W", mode="Absolute")
@ispec("32<[ ~off2(4) 01 ~off3(4) ~off1(6) ~off4(4) a(4) {e5} ]", mnemonic="LDMST", mode="Absolute")
def tricore_st(obj, off2, off3, off1, off4, a):
    src = env.D[a]
    if obj.mnemonic in ("ST_A",)  : src = env.A[a]
    if obj.mnemonic in ("ST_D","LDMST") : src = env.E[a]
    if obj.mnemonic=="ST_DA": src = env.P[a]
    addr = off1//off2//off3
    obj.operands = [composer([env.cst(addr.int(),28),env.cst(off4,4)]), src]
    obj.type = type_data_processing

@ispec("32<[ ~off2(4) 00 ~off3(4) ~off1(6) ~off4(4) b bpos(3) {d5} ]", mnemonic="ST_T", mode="Absolute")
def tricore_st(obj, off2, off3, off1, off4, b, bpos):
    obj.operands = [composer([env.cst(src.int(),28),env.cst(off4,4)]), env.cst(bpos,3), env.cst(b,1)]
    obj.type = type_data_processing

@ispec("32<[ ~off2(4) 00 ~off3(4) ~off1(6) ~off4(4) ---- {15} ]", mnemonic="STLCX", mode="Absolute")
def tricore_st(obj, off2, off3, off1, off4):
    obj.operands = [composer([env.cst(src.int(),28),env.cst(off4,4)])]
    obj.type = type_data_processing

@ispec("32<[ ~off2(4) 10 ~off3(4) ~off1(6) ~off4(4) a(4) {15} ]", mnemonic="LDLCX", mode="Absolute")
@ispec("32<[ ~off2(4) 11 ~off3(4) ~off1(6) ~off4(4) a(4) {15} ]", mnemonic="LDUCX", mode="Absolute")
def tricore_ld(obj, off2, off3, off1, off4, a):
    src = off1//off2//off3
    obj.operands = [composer([env.cst(src.int(),28),env.cst(off4,4)])]
    obj.type = type_data_processing

@ispec("32<[ ~off2(4) 10 0110 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_A", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0110 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_A", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0110 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_A", mode="Circular")
@ispec("32<[ ~off2(4) 00 0110 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_A", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0110 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_A", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0000 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_B", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0000 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_B", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0000 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_B", mode="Circular")
@ispec("32<[ ~off2(4) 00 0000 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_B", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0000 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_B", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0001 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_BU", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0001 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_BU", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0001 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_BU", mode="Circular")
@ispec("32<[ ~off2(4) 00 0001 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_BU", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0001 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_BU", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0101 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_D", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0101 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_D", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0101 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_D", mode="Circular")
@ispec("32<[ ~off2(4) 00 0101 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_D", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0101 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_D", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0111 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_DA", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0111 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_DA", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0111 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_DA", mode="Circular")
@ispec("32<[ ~off2(4) 00 0111 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_DA", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0111 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_DA", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0010 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_H", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0010 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_H", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0010 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_H", mode="Circular")
@ispec("32<[ ~off2(4) 00 0010 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_H", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0010 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_H", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0011 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_HU", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0011 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_HU", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0011 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_HU", mode="Circular")
@ispec("32<[ ~off2(4) 00 0011 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_HU", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0011 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_HU", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 1000 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_Q", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 1000 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_Q", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 1000 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_Q", mode="Circular")
@ispec("32<[ ~off2(4) 00 1000 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_Q", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 1000 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_Q", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0100 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_W", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0100 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_W", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0100 ~off1(6) b(4) a(4) {29} ]", mnemonic="LD_W", mode="Circular")
@ispec("32<[ ~off2(4) 00 0100 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_W", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0100 ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_W", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 1000 ~off1(6) b(4) a(4) {49} ]", mnemonic="LEA", mode="Short-offset")
def tricore_ld(obj, off2, off1, b, a):
    dst = env.D[a]
    if   obj.mnemonic=="LD_A"  : dst = env.A[a]
    elif obj.mnemonic=="LEA"   : dst = env.A[a]
    elif obj.mnemonic=="LD_D"  : dst = env.E[a]
    elif obj.mnemonic=="LDMST" : dst = env.E[a]
    elif obj.mnemonic=="LD_DA" : dst = env.P[a]
    obj.b = b
    src1 = env.A[b]
    off10 = off1//off2
    src2 = env.cst(off10.int(-1),10)
    obj.operands = [dst, src1, src2]
    if obj.mode == "Bit-Reverse":
        obj.operands.pop()
    obj.type = type_data_processing

@ispec("32<[ ~off2(4) 10 0110 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_A", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0110 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_A", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0110 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_A", mode="Circular")
@ispec("32<[ ~off2(4) 00 0110 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_A", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0110 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_A", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0000 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_B", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0000 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_B", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0000 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_B", mode="Circular")
@ispec("32<[ ~off2(4) 00 0000 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_B", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0000 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_B", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0101 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_D", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0101 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_D", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0101 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_D", mode="Circular")
@ispec("32<[ ~off2(4) 00 0101 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_D", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0101 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_D", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0111 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_DA", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0111 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_DA", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0111 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_DA", mode="Circular")
@ispec("32<[ ~off2(4) 00 0111 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_DA", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0111 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_DA", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0010 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_H", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0010 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_H", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0010 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_H", mode="Circular")
@ispec("32<[ ~off2(4) 00 0010 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_H", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0010 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_H", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 1000 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_Q", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 1000 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_Q", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 1000 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_Q", mode="Circular")
@ispec("32<[ ~off2(4) 00 1000 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_Q", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 1000 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_Q", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0100 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_W", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0100 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_W", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0100 ~off1(6) b(4) a(4) {a9} ]", mnemonic="ST_W", mode="Circular")
@ispec("32<[ ~off2(4) 00 0100 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_W", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0100 ~off1(6) b(4) a(4) {89} ]", mnemonic="ST_W", mode="Pre-increment")
@ispec("32<[ ~off2(4) 10 0001 ~off1(6) b(4) a(4) {49} ]", mnemonic="LDMST", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 0001 ~off1(6) b(4) a(4) {69} ]", mnemonic="LDMST", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 0001 ~off1(6) b(4) a(4) {69} ]", mnemonic="LDMST", mode="Circular")
@ispec("32<[ ~off2(4) 00 0001 ~off1(6) b(4) a(4) {49} ]", mnemonic="LDMST", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 0001 ~off1(6) b(4) a(4) {49} ]", mnemonic="LDMST", mode="Pre-increment")
def tricore_st(obj, off2, off1, b, a):
    dst = env.D[a]
    if   obj.mnemonic=="ST_A"  : dst = env.A[a]
    elif obj.mnemonic=="ST_D"  : dst = env.E[a]
    elif obj.mnemonic=="ST_DA" : dst = env.P[a]
    elif obj.mnemonic=="LDMST" : dst = env.E[a]
    obj.b = b
    src1 = env.A[b]
    off10 = off1//off2
    src2 = env.cst(off10.int(-1),10)
    obj.operands = [src1, src2, dst]
    if obj.mode == "Bit-Reverse":
        obj.operands.pop()
    obj.type = type_data_processing

@ispec("32<[ ~off2(4) 10 1000 ~off1(6) b(4) a(4) {49} ]", mnemonic="SWAP_W", mode="Short-offset")
@ispec("32<[ ~off2(4) 00 1000 ~off1(6) b(4) a(4) {69} ]", mnemonic="SWAP_W", mode="Bit-reverse")
@ispec("32<[ ~off2(4) 01 1000 ~off1(6) b(4) a(4) {69} ]", mnemonic="SWAP_W", mode="Circular")
@ispec("32<[ ~off2(4) 00 1000 ~off1(6) b(4) a(4) {49} ]", mnemonic="SWAP_W", mode="Post-increment")
@ispec("32<[ ~off2(4) 01 1000 ~off1(6) b(4) a(4) {49} ]", mnemonic="SWAP_W", mode="Pre-increment")
def tricore_ld(obj, off2, off1, b, a):
    dst = env.D[a]
    src1 = env.P[b]
    off10 = off1//off2
    src2 = env.cst(off10.int(-1),10)
    obj.operands = [src1, src2, dst]
    obj.type = type_data_processing


@ispec("32<[ ~off2(4) 10 0100 ~off1(6) b(4) ---- {49} ]", mnemonic="LDLCX", mode="Short-offset")
@ispec("32<[ ~off2(4) 10 0101 ~off1(6) b(4) ---- {49} ]", mnemonic="LDUCX", mode="Short-offset")
@ispec("32<[ ~off2(4) 10 0110 ~off1(6) b(4) ---- {49} ]", mnemonic="STLCX", mode="Short-offset")
@ispec("32<[ ~off2(4) 10 0111 ~off1(6) b(4) ---- {49} ]", mnemonic="STUCX", mode="Short-offset")
def tricore_ld(obj, off2, off1, b):
    src1 = env.A[b]
    off10 = off1//off2
    src2 = env.cst(off10.int(-1),10)
    obj.operands = [src1, src2]
    obj.type = type_data_processing

@ispec("32<[ ~off2(4) ~off3(6) ~off1(6) b(4) a(4) {99} ]", mnemonic="LD_A", mode="Long-offset")
@ispec("32<[ ~off2(4) ~off3(6) ~off1(6) b(4) a(4) {79} ]", mnemonic="LD_B", mode="Long-offset")
@ispec("32<[ ~off2(4) ~off3(6) ~off1(6) b(4) a(4) {39} ]", mnemonic="LD_BU", mode="Long-offset")
@ispec("32<[ ~off2(4) ~off3(6) ~off1(6) b(4) a(4) {09} ]", mnemonic="LD_H", mode="Long-offset")
@ispec("32<[ ~off2(4) ~off3(6) ~off1(6) b(4) a(4) {b9} ]", mnemonic="LD_HU", mode="Long-offset")
@ispec("32<[ ~off2(4) ~off3(6) ~off1(6) b(4) a(4) {19} ]", mnemonic="LD_W", mode="Long-offset")
@ispec("32<[ ~off2(4) ~off3(6) ~off1(6) b(4) a(4) {d9} ]", mnemonic="LEA", mode="Long-offset")
def tricore_ld(obj, off2, off3, off1, b, a):
    dst = env.D[a]
    if obj.mnemonic in ("LD_A", "LEA"): dst = env.A[a]
    if obj.mnemonic=="LD_D": dst = env.E[a]
    src1 = env.A[b]
    off16 = off1//off2//off3
    src2 = env.cst(off16.int(-1),32)
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ ~off2(4) ~off3(6) ~off1(6) b(4) a(4) {b5} ]", mnemonic="ST_A", mode="Long-offset")
@ispec("32<[ ~off2(4) ~off3(6) ~off1(6) b(4) a(4) {e9} ]", mnemonic="ST_B", mode="Long-offset")
@ispec("32<[ ~off2(4) ~off3(6) ~off1(6) b(4) a(4) {f9} ]", mnemonic="ST_H", mode="Long-offset")
@ispec("32<[ ~off2(4) ~off3(6) ~off1(6) b(4) a(4) {59} ]", mnemonic="ST_W", mode="Long-offset")
def tricore_st(obj, off2, off3, off1, b, a):
    dst = env.D[a]
    if obj.mnemonic=="ST_A": dst = env.A[a]
    if obj.mnemonic=="ST_D": dst = env.E[a]
    src1 = env.A[b]
    off16 = off1//off2//off3
    src2 = env.cst(off16.int(-1),32)
    obj.operands = [src1, src2, dst]
    obj.type = type_data_processing

@ispec("16<[ const(8) {d8} ]", mnemonic="LD_A", mode="SC")
@ispec("16<[ const(8) {58} ]", mnemonic="LD_W", mode="SC")
def tricore_ld(obj, const):
    dst = env.D[15]
    if obj.mnemonic=="LD_A": dst=env.A[15]
    src1 = env.A[10]
    src2 = env.cst(4*const,32)
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ const(8) {f8} ]", mnemonic="ST_A", mode="SC")
@ispec("16<[ const(8) {78} ]", mnemonic="ST_W", mode="SC")
def tricore_st(obj, const):
    dst = env.D[15]
    if obj.mnemonic=="ST_A": dst=env.A[15]
    src1 = env.A[10]
    src2 = env.cst(4*const,32)
    obj.operands = [src1, src2, dst]
    obj.type = type_data_processing

@ispec("16<[ b(4) c(4) {d4} ]", mnemonic="LD_A", mode="SLR")
@ispec("16<[ b(4) c(4) {c4} ]", mnemonic="LD_A", mode="Post-increment")
@ispec("16<[ b(4) c(4) {14} ]", mnemonic="LD_BU", mode="SLR")
@ispec("16<[ b(4) c(4) {04} ]", mnemonic="LD_BU", mode="Post-increment")
@ispec("16<[ b(4) c(4) {94} ]", mnemonic="LD_H", mode="SLR")
@ispec("16<[ b(4) c(4) {84} ]", mnemonic="LD_H", mode="Post-increment")
@ispec("16<[ b(4) c(4) {54} ]", mnemonic="LD_W", mode="SLR")
@ispec("16<[ b(4) c(4) {44} ]", mnemonic="LD_W", mode="Post-increment")
def tricore_ld(obj, b, c):
    dst = env.D[c]
    if obj.mnemonic=="LD_A": dst = env.A[c]
    if obj.mnemonic=="LD_D": dst = env.E[c]
    src1 = env.A[b]
    src2 = env.cst(0,32)
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ b(4) c(4) {f4} ]", mnemonic="ST_A", mode="SSR")
@ispec("16<[ b(4) c(4) {e4} ]", mnemonic="ST_A", mode="Post-increment")
@ispec("16<[ b(4) c(4) {b4} ]", mnemonic="ST_H", mode="SSR")
@ispec("16<[ b(4) c(4) {a4} ]", mnemonic="ST_H", mode="Post-increment")
@ispec("16<[ b(4) c(4) {74} ]", mnemonic="ST_W", mode="SSR")
@ispec("16<[ b(4) c(4) {64} ]", mnemonic="ST_W", mode="Post-increment")
def tricore_st(obj, b, c):
    dst = env.D[c]
    if obj.mnemonic=="ST_A": dst = env.A[c]
    if obj.mnemonic=="ST_D": dst = env.E[c]
    src1 = env.A[b]
    src2 = env.cst(0,32)
    obj.operands = [src1, src2, dst]
    obj.type = type_data_processing

@ispec("16<[ off(4) c(4) {c8} ]", mnemonic="LD_A", mode="SLRO")
@ispec("16<[ off(4) c(4) {08} ]", mnemonic="LD_BU", mode="SLRO")
@ispec("16<[ off(4) c(4) {88} ]", mnemonic="LD_H", mode="SLRO")
@ispec("16<[ off(4) c(4) {48} ]", mnemonic="LD_W", mode="SLRO")
def tricore_ld(obj, off, c):
    dst = env.A[c] if obj.mnemonic=="LD_A" else env.D[c]
    src1 = env.A[15]
    src2 = env.cst(4*off,32)
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ off(4) c(4) {e8} ]", mnemonic="ST_A", mode="SSRO")
@ispec("16<[ off(4) c(4) {a8} ]", mnemonic="ST_H", mode="SSRO")
@ispec("16<[ off(4) c(4) {68} ]", mnemonic="ST_W", mode="SSRO")
def tricore_st(obj, off, c):
    dst = env.A[c] if obj.mnemonic=="ST_A" else env.D[c]
    src1 = env.A[15]
    src2 = env.cst(4*off,32)
    obj.operands = [src1, src2, dst]
    obj.type = type_data_processing

@ispec("16<[ b(4) off(4) {cc} ]", mnemonic="LD_A", mode="SRO")
@ispec("16<[ b(4) off(4) {0c} ]", mnemonic="LD_BU", mode="SRO")
@ispec("16<[ b(4) off(4) {8c} ]", mnemonic="LD_H", mode="SRO")
@ispec("16<[ b(4) off(4) {4c} ]", mnemonic="LD_W", mode="SRO")
def tricore_ld(obj, b, off):
    dst = env.A[15] if obj.mnemonic=="LD_A" else env.D[15]
    src1 = env.A[b]
    src2 = env.cst(4*off,32)
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("16<[ b(4) off(4) {ec} ]", mnemonic="ST_A", mode="SRO")
@ispec("16<[ b(4) off(4) {ac} ]", mnemonic="ST_H", mode="SRO")
@ispec("16<[ b(4) off(4) {6c} ]", mnemonic="ST_W", mode="SRO")
def tricore_st(obj, b, off):
    dst = env.A[15] if obj.mnemonic=="ST_A" else env.D[15]
    src1 = env.A[b]
    src2 = env.cst(4*off,32)
    obj.operands = [src1, src2, dst]
    obj.type = type_data_processing

@ispec("32<[ c(4) const16(16) ---- {4d} ]", mnemonic="MFCR")
def tricore_mfcr(obj, c, const16):
    src = env.cst(const16,16)
    dst = env.D[c]
    obj.operands = [dst, src]
    obj.type = type_system

@ispec("32<[ ---- const16(16) a(4) {cd} ]", mnemonic="MTCR")
def tricore_mtcr(obj, const16, a):
    src1 = env.cst(const16,16)
    src2 = env.D[a]
    obj.operands = [src1, src2]
    obj.type = type_system

@ispec("32<[ c(4) const16(16) ---- {bb} ]", mnemonic="MOV_U")
def tricore_mov(obj, c, const16):
    src = env.cst(const16,32)
    dst = env.D[c]
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("32<[ c(4) ~const16(16) ---- {3b} ]", mnemonic="MOV")
def tricore_mov(obj, c, const16):
    src = env.cst(const16.int(-1),32)
    dst = env.D[c]
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("32<[ c(4) const16(16) ---- {7b} ]", mnemonic="MOVH")
def tricore_mov(obj, c, const16):
    src = env.cst(const16,16)
    dst = env.D[c]
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("32<[ c(4) const16(16) ---- {91} ]", mnemonic="MOVH_A")
def tricore_mov(obj, c, const16):
    src = env.cst(const16,16)
    dst = env.A[c]
    obj.operands = [dst, src]
    obj.type = type_data_processing

@ispec("32<[ c(4) ~const16(16) ---- {fb} ]", mnemonic="MOV")
def tricore_mov(obj, c, const16):
    src = env.cst(const16.int(-1),64)
    dst = env.E[c]
    obj.operands = [dst, src]
    obj.type = type_data_processing

