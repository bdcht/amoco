#!/usr/bin/env python

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.arch.core import *

from amoco.arch.arm.v7 import env
from .utils import *

ISPECS = []

#------------------------------------------------------
# amoco THUMB-1  instruction specs:
#------------------------------------------------------

@ispec("16[ 010000 0000 Rm(3) Rdn(3) ]", mnemonic="AND")
@ispec("16[ 010000 0001 Rm(3) Rdn(3) ]", mnemonic="EOR")
@ispec("16[ 010000 0010 Rm(3) Rdn(3) ]", mnemonic="LSL")
@ispec("16[ 010000 0011 Rm(3) Rdn(3) ]", mnemonic="LSR")
@ispec("16[ 010000 0100 Rm(3) Rdn(3) ]", mnemonic="ASR")
@ispec("16[ 010000 0101 Rm(3) Rdn(3) ]", mnemonic="ADC")
@ispec("16[ 010000 0110 Rm(3) Rdn(3) ]", mnemonic="SBC")
@ispec("16[ 010000 0111 Rm(3) Rdn(3) ]", mnemonic="ROR")
@ispec("16[ 010000 1100 Rm(3) Rdn(3) ]", mnemonic="ORR")
@ispec("16[ 010000 1110 Rm(3) Rdn(3) ]", mnemonic="BIC")
def T1_ADC_r(obj,Rm,Rdn):
  obj.setflags = ~InITBlock(env.internals['itstate'])
  obj.n = env.regs[Rdn]
  obj.d = obj.n
  obj.m = env.regs[Rm]
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("16[ 000 11 1 0 imm3(3) Rn(3) Rd(3) ]", mnemonic="ADD")
@ispec("16[ 000 11 1 1 imm3(3) Rn(3) Rd(3) ]", mnemonic="SUB")
def T1_ADD_i(obj,imm3,Rn,Rd):
  obj.setflags = ~InITBlock(env.internals['itstate'])
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  obj.imm32 = env.cst(imm3,32)
  obj.operands = [obj.d,obj.n,obj.imm32]
  obj.type = type_data_processing

@ispec("16[ 001 10 Rdn(3) imm8(8) ]", mnemonic="ADD")
@ispec("16[ 001 11 Rdn(3) imm8(8) ]", mnemonic="SUB")
def T2_ADD_i(obj,Rdn,imm8):
  obj.setflags = ~InITBlock(env.internals['itstate'])
  obj.n = env.regs[Rdn]
  obj.d = obj.n
  obj.imm32 = env.cst(imm8,32)
  obj.operands = [obj.d,obj.n,obj.imm32]
  obj.type = type_data_processing

@ispec("16[ 000 11 0 0 Rm(3) Rn(3) Rd(3) ]", mnemonic="ADD")
@ispec("16[ 000 11 0 1 Rm(3) Rn(3) Rd(3) ]", mnemonic="SUB")
def T1_ADD_r(obj,Rm,Rn,Rd):
  obj.setflags = ~InITBlock(env.internals['itstate'])
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("16[ 010001 00 DN Rm(4) Rdn(3) ]", mnemonic="ADD")
def T2_ADD_r(obj,DN,Rm,Rdn):
  obj.setflags = False
  obj.n = env.regs[DN<<3+Rdn]
  obj.d = obj.n
  obj.m = env.regs[Rm]
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("16[ 1010 1 Rd(3) imm8(8) ]", mnemonic="ADD")
def T1_ADD_SP_i(obj,Rd,imm8):
  obj.d = env.regs[Rd]
  obj.n = env.sp
  obj.imm32 = env.cst(imm8<<2,32)
  obj.operands = [obj.d,obj.n,obj.imm32]
  obj.type = type_data_processing

@ispec("16[ 1011 0000 0 imm7(7) ]", mnemonic="ADD")
@ispec("16[ 1011 0000 1 imm7(7) ]", mnemonic="SUB")
def T2_ADD_SP_i(obj,imm7):
  obj.d = env.sp
  obj.n = env.sp
  obj.imm32 = env.cst(imm7<<2,32)
  obj.operands = [obj.d,obj.n,obj.imm32]
  obj.type = type_data_processing

@ispec("16[ 01000100 DM 1101 Rdm(3) ]", mnemonic="ADD")
def T1_ADD_SP_r(obj,DM,Rdm):
  obj.d = env.regs[DM<<3+Rdm]
  obj.n = env.sp
  obj.m = obj.d
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("16[ 01000100 1 Rm(4) 101 ]", mnemonic="ADD")
def T2_ADD_SP_r(obj,Rm):
  obj.d = env.sp
  obj.n = env.sp
  obj.m = env.regs[Rm]
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("16[ 1010 0 Rd(3) imm8(8) ]", mnemonic="ADR")
def T1_ADR(obj,Rd,imm8):
  obj.d = env.regs[Rd]
  obj.imm32 = env.cst(imm8<<2,32)
  obj.operands = [obj.d,obj.imm32]
  obj.type = type_data_processing

@ispec("16[ 000 10 imm5(5) Rm(3) Rd(3) ]", mnemonic="ASR")
@ispec("16[ 000 00 imm5(5) Rm(3) Rd(3) ]", mnemonic="LSL")
@ispec("16[ 000 01 imm5(5) Rm(3) Rd(3) ]", mnemonic="LSR")
def T1_ASR_i(obj,imm5,Rm,Rd):
  obj.setflags = ~InITBlock(env.internals['itstate'])
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.imm5 = imm5
  obj.operands = [obj.d,obj.m,obj.imm5]
  obj.type = type_data_processing

@ispec("16[ 1101 .cond(4) imm8(8) ]", mnemonic="B")
def T1_B(obj,imm8):
  obj.imm32 = env.cst(imm8<<1,9).signextend(32)
  obj.operands = [obj.imm32]
  obj.type = type_control_flow

@ispec("16[ 11100 imm11(11) ]", mnemonic="B")
def T2_B(obj,imm11):
  obj.imm32 = env.cst(imm11<<1,12).signextend(32)
  obj.operands = [obj.imm32]
  obj.type = type_control_flow

@ispec("16[ 1101 1110 imm8(8) ]", mnemonic="BKPT")
@ispec("16[ 1101 1111 imm8(8) ]", mnemonic="SVC")
def T1_BKPT(obj,imm8):
  obj.imm32 = env.cst(imm8,32)
  obj.operands = [obj.imm32]
  obj.type = type_cpu_state

@ispec("16[ 010001 11 0 Rm(4) 000 ]", mnemonic="BX")
@ispec("16[ 010001 11 1 Rm(4) 000 ]", mnemonic="BLX")
def T1_BLX_r(obj,Rm):
  obj.m = env.regs[Rm]
  obj.operands = [obj.m]
  obj.type = type_control_flow

@ispec("16[ 1011 0 0 #i 1 #imm5(5) Rn(3) ]", mnemonic="CBZ")
@ispec("16[ 1011 1 0 #i 1 #imm5(5) Rn(3) ]", mnemonic="CBNZ")
def T1_CBNZ_CBZ(obj,i,imm5,Rn):
  obj.n = env.regs[Rn]
  obj.imm32 = env.cst(int(i+imm5+'0',2),32)
  obj.operands = [obj.n, obj.imm32]
  obj.type = type_control_flow

@ispec("16[ 010000 1011 Rm(3) Rn(3) ]", mnemonic="CMN")
@ispec("16[ 010000 1010 Rm(3) Rn(3) ]", mnemonic="CMP")
@ispec("16[ 010000 1000 Rm(3) Rn(3) ]", mnemonic="TST")
def T1_CMN_r(obj,i,Rm,Rn):
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.operands = [obj.n, obj.m]
  obj.type = type_data_processing

@ispec("16[ 001 01 Rn(3) imm8(8) ]", mnemonic="CMP")
def T1_CMP_i(obj,Rn,imm8):
  obj.n = env.regs[Rn]
  obj.imm32 = env.cst(imm8,32)
  obj.operands = [obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("16[ 010001 01 N Rm(4) Rn(3) ]", mnemonic="CMP")
def T2_CMP_r(obj,N,Rm,Rn):
  obj.n = env.regs[N<<3+Rn]
  obj.m = env.regs[Rm]
  obj.operands = [obj.n, obj.m]
  obj.type = type_data_processing

@ispec("16[ 1011 1111 .firstcond(4) .mask(4) ]", mnemonic="IT")
def T1_IT(obj):
  obj.type = type_cpu_state

@ispec("16[ 1100 1 Rn(3) ~register_list(8) ]", mnemonic="LDM")
def T1_LDM(obj,Rn,register_list):
  obj.n = env.regs[Rn]
  obj.registers = [env.regs[i] for i,r in enumerate(register_list) if r==1]
  obj.wback = (obj.n in obj.registers)
  obj.operands = [obj.n, obj.registers]
  obj.type = type_data_processing

@ispec("16[ 1100 0 Rn(3) ~register_list(8) ]", mnemonic="STM")
def T1_STM(obj,Rn,register_list):
  obj.n = env.regs[Rn]
  obj.registers = [env.regs[i] for i,r in enumerate(register_list) if r==1]
  obj.wback = True
  obj.operands = [obj.n, obj.registers]
  obj.type = type_data_processing

@ispec("16[ 011 1 1 imm5(5) Rn(3) Rt(3) ]", mnemonic="LDRB",_s=0)
@ispec("16[ 100 0 1 imm5(5) Rn(3) Rt(3) ]", mnemonic="LDRH",_s=1)
@ispec("16[ 011 0 1 imm5(5) Rn(3) Rt(3) ]", mnemonic="LDR", _s=2)
@ispec("16[ 011 1 0 imm5(5) Rn(3) Rt(3) ]", mnemonic="STRB",_s=0)
@ispec("16[ 100 0 0 imm5(5) Rn(3) Rt(3) ]", mnemonic="STRH",_s=1)
@ispec("16[ 011 0 0 imm5(5) Rn(3) Rt(3) ]", mnemonic="STR", _s=2)
def T1_LDRx(obj,imm5,Rn,Rt,_s):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.imm32 = env.cst(imm5<<_s,32)
  obj.index = True
  obj.add = True
  obj.wback = False
  obj.operands = [obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("16[ 1001 1 Rt(3) imm8(8) ]", mnemonic="LDR")
@ispec("16[ 1001 0 Rt(3) imm8(8) ]", mnemonic="STR")
def T2_LDR(obj,Rt,imm8):
  obj.n = env.sp
  obj.t = env.regs[Rt]
  obj.imm32 = env.cst(imm8<<2,32)
  obj.index = True
  obj.add = True
  obj.wback = False
  obj.operands = [obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("16[ 01001 Rt(3) imm8(8) ]", mnemonic="LDR")
def T1_LDR_literal(obj,Rt,imm8):
  obj.n = env.pc
  obj.t = env.regs[Rt]
  obj.imm32 = env.cst(imm8<<2,32)
  obj.add = True
  obj.operands = [obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("16[ 0101 100 Rm(3) Rn(3) Rt(3) ]", mnemonic="LDR")
@ispec("16[ 0101 110 Rm(3) Rn(3) Rt(3) ]", mnemonic="LDRB")
@ispec("16[ 0101 101 Rm(3) Rn(3) Rt(3) ]", mnemonic="LDRH")
@ispec("16[ 0101 011 Rm(3) Rn(3) Rt(3) ]", mnemonic="LDRSB")
@ispec("16[ 0101 111 Rm(3) Rn(3) Rt(3) ]", mnemonic="LDRSH")
@ispec("16[ 0101 000 Rm(3) Rn(3) Rt(3) ]", mnemonic="STR")
@ispec("16[ 0101 010 Rm(3) Rn(3) Rt(3) ]", mnemonic="STRB")
@ispec("16[ 0101 001 Rm(3) Rn(3) Rt(3) ]", mnemonic="STRH")
def T1_LDR_r(obj,Rm,Rn,Rt):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.m = env.regs[Rm]
  obj.index = True
  obj.add = True
  obj.wback = False
  obj.operands = [obj.t, obj.n, obj.m]
  obj.type = type_data_processing

@ispec("16[ 001 00 Rd(3) imm8(8) ]", mnemonic="MOV")
def T1_MOV_i(obj,Rd,imm8):
  obj.setflags = ~InITBlock(env.internals['itstate'])
  obj.d = env.regs[Rd]
  obj.imm32 = env.cst(imm8,32)
  obj.operands = [obj.d, obj.imm32]
  obj.type = type_data_processing

@ispec("16[ 010001 10 D Rm(4) Rd(3) ]", mnemonic="MOV")
def T1_MOV_r(obj,D,Rm,Rd):
  obj.setflags = False
  obj.d = env.regs[D<<3+Rd]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d, obj.m]
  obj.type = type_data_processing

@ispec("16[ 000 00 00000 Rm(3) Rd(3) ]", mnemonic="MOV")
@ispec("16[ 1011 1010 00 Rm(3) Rd(3) ]", mnemonic="REV")
@ispec("16[ 1011 1010 01 Rm(3) Rd(3) ]", mnemonic="REV16")
@ispec("16[ 1011 1010 11 Rm(3) Rd(3) ]", mnemonic="REVSH")
@ispec("16[ 1011 0010 01 Rm(3) Rd(3) ]", mnemonic="SXTB", rotation=0)
@ispec("16[ 1011 0010 00 Rm(3) Rd(3) ]", mnemonic="SXTH", rotation=0)
@ispec("16[ 1011 0010 11 Rm(3) Rd(3) ]", mnemonic="UXTB", rotation=0)
@ispec("16[ 1011 0010 10 Rm(3) Rd(3) ]", mnemonic="UXTH", rotation=0)
def T2_MOV_r(obj,Rm,Rd):
  obj.setflags = True
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d, obj.m]
  obj.type = type_data_processing

@ispec("16[ 010000 1101 Rn(3)  Rdm(3) ]", mnemonic="MUL")
def T1_MUL(obj,Rn,Rdm):
  obj.setflags = ~InITBlock(env.internals['itstate'])
  obj.d = env.regs[Rdm]
  obj.n = env.regs[Rn]
  obj.m = obj.d
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("16[ 010000 1111 Rm(3) Rd(3) ]", mnemonic="MVN")
def T1_MVN_r(obj,Rm,Rd):
  obj.setflags = ~InITBlock(env.internals['itstate'])
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d, obj.m]
  obj.type = type_data_processing

@ispec("16[ 1011 1111 0000 0000 ]", mnemonic="NOP")
@ispec("16[ 1011 1111 0100 0000 ]", mnemonic="SEV")
@ispec("16[ 1011 1111 0010 0000 ]", mnemonic="WFE")
@ispec("16[ 1011 1111 0011 0000 ]", mnemonic="WFI")
@ispec("16[ 1011 1111 0001 0000 ]", mnemonic="YIELD")
def T1_NOP(obj):
  obj.type = type_cpu_state

@ispec("16[ 1011 1 10 #P #register_list(8) ]", mnemonic="POP")
def T1_POP(obj,P,register_list):
  obj.registers = [env.regs[i] for i,r in enumerate(register_list[::-1]+'0'*7+P) if r=='1']
  obj.operands = [obj.registers]
  obj.type = type_data_processing

@ispec("16[ 1011 0 10 #M #register_list(8) ]", mnemonic="PUSH")
def T1_PUSH(obj,M,register_list):
  obj.registers = [env.regs[i] for i,r in enumerate(register_list[::-1]+'0'*6+M+'0') if r=='1']
  obj.operands = [obj.registers]
  obj.type = type_data_processing

@ispec("16[ 010000 1001 Rn(3) Rd(3) ]", mnemonic="RSB")
def T1_RSB(obj,Rn,Rd):
  obj.setflags = ~InITBlock(env.internals['itstate'])
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.imm32 = env.cst(0,32)
  obj.operands = [obj.d,obj.n,obj.imm32]
  obj.type = type_data_processing

@ispec("16[ 1011 0110 010 1 E 000 ]", mnemonic="SETEND")
def T1_SETEND(obj,E):
  obj.set_bigend = (E==1)
  obj.operands = [obj.set_bigend]
  obj.type = type_cpu_state

# add THUMB-2 instructions:
from amoco.arch.arm.v7 import spec_thumb2

ISPECS += spec_thumb2.ISPECS
