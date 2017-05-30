# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.arch.riscv import env

from amoco.arch.core import *

#-------------------------------------------------------
# instruction RISC-V decoders
#-------------------------------------------------------

ISPECS = []

@ispec("32<[ 0000000 rs2(5) rs1(5) 000 rd(5) 0110011 ]", mnemonic='ADD')
@ispec("32<[ 0100000 rs2(5) rs1(5) 000 rd(5) 0110011 ]", mnemonic='SUB')
@ispec("32<[ 0000000 rs2(5) rs1(5) 111 rd(5) 0110011 ]", mnemonic='AND')
@ispec("32<[ 0000000 rs2(5) rs1(5) 110 rd(5) 0110011 ]", mnemonic='OR')
@ispec("32<[ 0000000 rs2(5) rs1(5) 100 rd(5) 0110011 ]", mnemonic='XOR')
@ispec("32<[ 0000000 rs2(5) rs1(5) 010 rd(5) 0110011 ]", mnemonic='SLT')
@ispec("32<[ 0000000 rs2(5) rs1(5) 011 rd(5) 0110011 ]", mnemonic='SLTU')
@ispec("32<[ 0100000 rs2(5) rs1(5) 101 rd(5) 0110011 ]", mnemonic='SRA')
@ispec("32<[ 0000000 rs2(5) rs1(5) 101 rd(5) 0110011 ]", mnemonic='SRL')
@ispec("32<[ 0000000 rs2(5) rs1(5) 001 rd(5) 0110011 ]", mnemonic='SLL')
@ispec("32<[ 0000001 rs2(5) rs1(5) 000 rd(5) 0110011 ]", mnemonic='MUL')
def riscv_rr_arithmetic(obj,rs2,rs1,rd):
    src1 = env.x[rs1]
    src2 = env.x[rs2]
    dst = env.x[rd]
    obj.operands = [dst, src1, src2]
    obj.type = type_data_processing

@ispec("32<[ ~imm(12) rs1(5) 000 rd(5) 0010011 ]", mnemonic='ADDI')
@ispec("32<[ ~imm(12) rs1(5) 111 rd(5) 0010011 ]", mnemonic='ANDI')
@ispec("32<[ ~imm(12) rs1(5) 110 rd(5) 0010011 ]", mnemonic='ORI')
@ispec("32<[ ~imm(12) rs1(5) 100 rd(5) 0010011 ]", mnemonic='XORI')
@ispec("32<[ ~imm(12) rs1(5) 010 rd(5) 0010011 ]", mnemonic='SLTI')
@ispec("32<[ ~imm(12) rs1(5) 011 rd(5) 0010011 ]", mnemonic='SLTIU')
def riscv_ri_arithmetic1(obj,imm,rs1,rd):
    src1 = env.x[rs1]
    imm = env.cst(imm.int(-1),32)
    dst = env.x[rd]
    obj.operands = [dst, src1, imm]
    obj.type = type_data_processing

@ispec("32<[ 0100000 imm(5) rs1(5) 101 rd(5) 0010011 ]", mnemonic='SRAI')
@ispec("32<[ 0000000 imm(5) rs1(5) 101 rd(5) 0010011 ]", mnemonic='SRLI')
@ispec("32<[ 0000000 imm(5) rs1(5) 001 rd(5) 0010011 ]", mnemonic='SLLI')
def riscv_ri_shifts(obj,imm,rs1,rd):
    src1 = env.x[rs1]
    imm = env.cst(imm,32)
    dst = env.x[rd]
    obj.operands = [dst, src1, imm]
    obj.type = type_data_processing

@ispec("32<[ imm(20) rd(5) 0110111 ]", mnemonic='LUI')
@ispec("32<[ imm(20) rd(5) 0010111 ]", mnemonic='AUIPC')
def riscv_ri_arithmetic2(obj,imm,rd):
    dst = env.x[rd]
    imm = env.cst(imm<<12,32)
    obj.operands = [dst, imm]
    obj.type = type_data_processing

@ispec("32<[ ~imm4 ~imm1(10) ~imm2 ~imm3(8) rd(5) 1101111 ]", mnemonic='JAL')
def riscv_jal(obj,imm1,imm2,imm3,imm4,rd):
    dst = env.x[rd]
    imm = imm1//imm2//imm3//imm4
    obj.operands = [dst, env.cst(imm.int(-1),32)<<1]
    obj.type = type_control_flow

@ispec("32<[ ~imm(12) rs1(5) 000 rd(5) 0000011 ]", mnemonic='LB')
@ispec("32<[ ~imm(12) rs1(5) 001 rd(5) 0000011 ]", mnemonic='LH')
@ispec("32<[ ~imm(12) rs1(5) 010 rd(5) 0000011 ]", mnemonic='LW')
@ispec("32<[ ~imm(12) rs1(5) 100 rd(5) 0000011 ]", mnemonic='LBU')
@ispec("32<[ ~imm(12) rs1(5) 101 rd(5) 0000011 ]", mnemonic='LHU')
def riscv_load(obj,imm,rs1,rd):
    r1 = env.x[rs1]
    dst = env.x[rd]
    sz = {'B':8, 'H':16, 'W':32}[obj.mnemonic[1]]
    obj.operands = [dst, env.mem(r1,sz,disp=imm.int(-1))]
    obj.type = type_data_processing

@ispec("32<[ ~imm2(7) rs2(5) rs1(5) 000 ~imm1(5) 0100011 ]", mnemonic='SB')
@ispec("32<[ ~imm2(7) rs2(5) rs1(5) 001 ~imm1(5) 0100011 ]", mnemonic='SH')
@ispec("32<[ ~imm2(7) rs2(5) rs1(5) 010 ~imm1(5) 0100011 ]", mnemonic='SW')
def riscv_store(obj,imm2,rs1,rs2,imm1):
    r1 = env.x[rs1]
    r2 = env.x[rs2]
    imm = imm1//imm2
    sz = {'B':8, 'H':16, 'W':32}[obj.mnemonic[1]]
    obj.operands = [env.mem(r1,sz,disp=imm.int(-1)),r2]
    obj.type = type_data_processing

@ispec("32<[ ~imm(12) rs1(5) 000 rd(5) 1100111 ]", mnemonic='JALR')
def riscv_jalr(obj,imm,rs1,rd):
    r1 = env.x[rs1]
    dst = env.x[rd]
    imm = env.cst(imm.int(-1),32)
    obj.operands = [dst, r1, imm]
    obj.type = type_control_flow

@ispec("32<[ ~imm4 ~imm2(6) rs2(5) rs1(5) 000 ~imm1(4) ~imm3 1100011 ]", mnemonic='BEQ')
@ispec("32<[ ~imm4 ~imm2(6) rs2(5) rs1(5) 001 ~imm1(4) ~imm3 1100011 ]", mnemonic='BNE')
@ispec("32<[ ~imm4 ~imm2(6) rs2(5) rs1(5) 100 ~imm1(4) ~imm3 1100011 ]", mnemonic='BLT')
@ispec("32<[ ~imm4 ~imm2(6) rs2(5) rs1(5) 101 ~imm1(4) ~imm3 1100011 ]", mnemonic='BGE')
@ispec("32<[ ~imm4 ~imm2(6) rs2(5) rs1(5) 110 ~imm1(4) ~imm3 1100011 ]", mnemonic='BLTU')
@ispec("32<[ ~imm4 ~imm2(6) rs2(5) rs1(5) 111 ~imm1(4) ~imm3 1100011 ]", mnemonic='BGEU')
def riscv_b(obj,rs1,rs2,imm1,imm2,imm3,imm4):
    r1 = env.x[rs1]
    r2 = env.x[rs2]
    imm = imm1//imm2//imm3//imm4
    imm = env.cst(imm.int(-1),32)<<1
    obj.operands = [r1,r2,imm]
    obj.type = type_control_flow

@ispec("32<[ imm(12) rs1(5) 010 rd(5) 1110011 ]", mnemonic='CSRRS')
@ispec("32<[ imm(12) rs1(5) 001 rd(5) 1110011 ]", mnemonic='CSRRW')
@ispec("32<[ imm(12) rs1(5) 011 rd(5) 1110011 ]", mnemonic='CSRRC')
@ispec("32<[ imm(12) rs1(5) 110 rd(5) 1110011 ]", mnemonic='CSRRSI')
@ispec("32<[ imm(12) rs1(5) 101 rd(5) 1110011 ]", mnemonic='CSRRWI')
@ispec("32<[ imm(12) rs1(5) 111 rd(5) 1110011 ]", mnemonic='CSRRCI')
def riscv_csr(obj,imm,rs1,rd):
    r1 = env.x[rs1]
    dst = env.x[rd]
    csr = env.csr[imm]
    obj.operands = [dst, r1]
    obj.type = type_cpu_state

@ispec("32<[ 0000 .pred(4) .succ(4) 00000 000 00000 0001111 ]", mnemonic='FENCE',type=type_system)
@ispec("32<[ 0000 0000 0000 00000 001 00000 0001111 ]", mnemonic='FENCE_I', type=type_system)
@ispec("32<[ 0000 0000 0000 00000 000 00000 1110011 ]", mnemonic='ECALL', type=type_control_flow)
@ispec("32<[ 0000 0000 0001 00000 000 00000 1110011 ]", mnemonic='EBREAK', type=type_system)
def riscv_noop(obj):
    obj.operands = []
