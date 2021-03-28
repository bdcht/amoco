# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from . import env

from amoco.arch.core import *

# -------------------------------------------------------
# instruction MIPS-R3000 decoders
# ref:
#   IDT R30xx Family
#   Software Reference Manual
#   Revision 1.0
# -------------------------------------------------------

ISPECS = []

@ispec("32<[ 000000 .code(20) 001101]", mnemonic="BREAK")
@ispec("32<[ 000000 .code(20) 001100]", mnemonic="SYSCALL")
def mips1_noop(obj):
    obj.operands = []
    obj.type = type_control_flow

@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 100000]", mnemonic="ADD")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 100010]", mnemonic="SUB")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 100001]", mnemonic="ADDU")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 100011]", mnemonic="SUBU")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 100100]", mnemonic="AND")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 100111]", mnemonic="NOR")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 100101]", mnemonic="OR")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 100110]", mnemonic="XOR")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 000100]", mnemonic="SLLV")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 000111]", mnemonic="SRAV")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 000110]", mnemonic="SRLV")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 101010]", mnemonic="SLT")
@ispec("32<[ 000000 rs(5) rt(5) rd(5) 00000 101011]", mnemonic="SLTU")
def mips1_drr(obj, rs, rt, rd):
    src1 = env.R[rs]
    src2 = env.R[rt]
    dst = env.R[rd]
    if obj.mnemonic in ('SLLV','SRAV','SRLV'):
        src1,src2 = src2,src1
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ 000000 rs(5) rt(5) 00000 00000 011010]", mnemonic="DIV")
@ispec("32<[ 000000 rs(5) rt(5) 00000 00000 011011]", mnemonic="DIVU")
@ispec("32<[ 000000 rs(5) rt(5) 00000 00000 011000]", mnemonic="MULT")
@ispec("32<[ 000000 rs(5) rt(5) 00000 00000 011001]", mnemonic="MULTU")
def mips1_rr(obj, rs, rt):
    src1 = env.R[rs]
    src2 = env.R[rt]
    obj.operands = [src1, src2]
    obj.type = type_data_processing

@ispec("32<[ 000010 t(26)]", mnemonic="J")
@ispec("32<[ 000011 t(26)]", mnemonic="JAL")
def mips1_jump_rel(obj, t):
    obj.operands = [env.cst(t,26)]
    obj.misc["delayed"] = True
    obj.type = type_control_flow

@ispec("32<[ 000000 rs(5) 00000 rd(5) 00000 001001]", mnemonic="JALR")
def mips1_jump_abs(obj, rs, rd):
    obj.operands = [env.R[rd],env.R[rs]]
    obj.misc["delayed"] = True
    obj.type = type_control_flow

@ispec("32<[ 000000 rs(5) 00000 00000 00000 001000]", mnemonic="JR")
def mips1_jump_abs(obj, rs):
    obj.operands = [env.R[rs]]
    obj.misc["delayed"] = True
    obj.type = type_control_flow


@ispec("32<[ 001000 rs(5) rt(5) ~imm(16) ]", mnemonic="ADDI")
@ispec("32<[ 001001 rs(5) rt(5) ~imm(16) ]", mnemonic="ADDIU")
@ispec("32<[ 001010 rs(5) rt(5) ~imm(16) ]", mnemonic="SLTI")
@ispec("32<[ 001011 rs(5) rt(5) ~imm(16) ]", mnemonic="SLTIU")
def mips1_dri(obj, rs, rt, imm):
    src1 = env.R[rs]
    imm = env.cst(imm.int(-1), 32)
    dst = env.R[rt]
    obj.operands = [dst, src1, imm]
    obj.type = type_data_processing

@ispec("32<[ 001100 rs(5) rt(5) imm(16) ]", mnemonic="ANDI")
@ispec("32<[ 001101 rs(5) rt(5) imm(16) ]", mnemonic="ORI")
@ispec("32<[ 001110 rs(5) rt(5) imm(16) ]", mnemonic="XORI")
def mips1_dri(obj, rs, rt, imm):
    src1 = env.R[rs]
    imm = env.cst(imm, 32)
    dst = env.R[rt]
    obj.operands = [dst, src1, imm]
    obj.type = type_data_processing

@ispec("32<[ 100000 base(5) rt(5) offset(16) ]", mnemonic="LB")
@ispec("32<[ 101000 base(5) rt(5) offset(16) ]", mnemonic="SB")
@ispec("32<[ 100100 base(5) rt(5) offset(16) ]", mnemonic="LBU")
@ispec("32<[ 100001 base(5) rt(5) offset(16) ]", mnemonic="LH")
@ispec("32<[ 101001 base(5) rt(5) offset(16) ]", mnemonic="SH")
@ispec("32<[ 100101 base(5) rt(5) offset(16) ]", mnemonic="LHU")
@ispec("32<[ 100011 base(5) rt(5) offset(16) ]", mnemonic="LW")
@ispec("32<[ 101011 base(5) rt(5) offset(16) ]", mnemonic="SW")
@ispec("32<[ 100010 base(5) rt(5) offset(16) ]", mnemonic="LWL")
@ispec("32<[ 101010 base(5) rt(5) offset(16) ]", mnemonic="SWL")
@ispec("32<[ 100110 base(5) rt(5) offset(16) ]", mnemonic="LWR")
@ispec("32<[ 101110 base(5) rt(5) offset(16) ]", mnemonic="SWR")
def mips1_loadstore(obj, base, rt, offset):
    rt = env.R[rt]
    obj.operands = [rt, env.R[base], env.cst(offset,16).signextend(32)]
    obj.type = type_data_processing

@ispec("32<[ 000000 00000 rt(5) rd(5) sa(5) 000000 ]", mnemonic="SLL")
@ispec("32<[ 000000 00000 rt(5) rd(5) sa(5) 000011 ]", mnemonic="SRA")
@ispec("32<[ 000000 00000 rt(5) rd(5) sa(5) 000010 ]", mnemonic="SRL")
def mips1_shifts(obj, rt, rd, sa):
    dst = env.R[rd]
    src1 = env.R[rt]
    src2 = env.cst(sa,5)
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ 001111 00000 rt(5) imm(16) ]", mnemonic="LUI")
def mips1_di(obj, rt, imm):
    dst = env.R[rt]
    obj.operands = [dst, env.cst(imm,16)]
    obj.type = type_data_processing

@ispec("32<[ 000100 rs(5) rt(5) ~imm(16) ]", mnemonic="BEQ")
@ispec("32<[ 000101 rs(5) rt(5) ~imm(16) ]", mnemonic="BNE")
def mips1_branch(obj, rs, rt, imm):
    rs = env.R[rs]
    rt = env.R[rt]
    imm = env.cst((imm<<2).int(-1), 32)
    obj.operands = [rs, rt, imm]
    obj.misc["delayed"] = True
    obj.type = type_control_flow

@ispec("32<[ 000001 rs(5) 00001 ~imm(16) ]", mnemonic="BGEZ")
@ispec("32<[ 000001 rs(5) 10001 ~imm(16) ]", mnemonic="BGEZAL")
@ispec("32<[ 000111 rs(5) 00000 ~imm(16) ]", mnemonic="BGTZ")
@ispec("32<[ 000110 rs(5) 00000 ~imm(16) ]", mnemonic="BLEZ")
@ispec("32<[ 000001 rs(5) 00000 ~imm(16) ]", mnemonic="BLTZ")
@ispec("32<[ 000001 rs(5) 10000 ~imm(16) ]", mnemonic="BLTZAL")
def mips1_branch(obj, rs, imm):
    src1 = env.R[rs]
    imm = env.cst((imm<<2).int(-1), 32)
    obj.operands = [src1, imm]
    obj.misc["delayed"] = True
    obj.type = type_control_flow

@ispec("32<[ 000000 00000 00000 rd(5) 00000 010000 ]", mnemonic="MFHI")
@ispec("32<[ 000000 00000 00000 rd(5) 00000 010010 ]", mnemonic="MFLO")
def mips1_r(obj, rd):
    dst = env.R[rd]
    obj.operands = [dst]
    obj.type = type_data_processing

@ispec("32<[ 000000 rs(5) 00000 00000 00000 010001 ]", mnemonic="MTHI")
@ispec("32<[ 000000 rs(5) 00000 00000 00000 010011 ]", mnemonic="MTLO")
def mips1_r(obj, rs):
    src = env.R[rs]
    obj.operands = [src]
    obj.type = type_data_processing

@ispec("32<[ 0100 .z(2) 00010 rt(5) rd(5) 00000000000 ]", mnemonic="CFC")
@ispec("32<[ 0100 .z(2) 00000 rt(5) rd(5) 00000000000 ]", mnemonic="MFC")
@ispec("32<[ 0100 .z(2) 00110 rt(5) rd(5) 00000000000 ]", mnemonic="CTC")
@ispec("32<[ 0100 .z(2) 00100 rt(5) rd(5) 00000000000 ]", mnemonic="MTC")
def mips1_copz_rr(obj, rt, rd):
    obj.operands = [env.R[rt], rd]
    obj.type = type_other

@ispec("32<[ 1100 .z(2) base(5) rt(5) offset(16) ]", mnemonic="LWC")
@ispec("32<[ 1110 .z(2) base(5) rt(5) offset(16) ]", mnemonic="SWC")
def mips1_copz_rbo(obj, base, rt, offset):
    obj.operands = [env.R[rt], env.R[base], env.cst(offset,16).signextend(32)]
    obj.type = type_other

@ispec("32<[ 0100 .z(2) 1 .cofun(25) ]", mnemonic="COP")
def mips1_copz_rbo(obj):
    obj.operands = []
    obj.type = type_other
