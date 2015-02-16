# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.arch.core import *

from amoco.arch.arm.v7 import env
from .utils import *

#------------------------------------------------------
# amoco THUMB2  instruction specs:
#------------------------------------------------------

ISPECS = []

@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 0000 S Rn(4) ]", mnemonic="AND")
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 0001 S Rn(4) ]", mnemonic="BIC")
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 0010 S Rn(4) ]", mnemonic="ORR")
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 0011 S Rn(4) ]", mnemonic="ORN")
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 0100 S Rn(4) ]", mnemonic="EOR")
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 1000 S Rn(4) ]", mnemonic="ADD")
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 1010 S Rn(4) ]", mnemonic="ADC")
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 1011 S Rn(4) ]", mnemonic="SBC")
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 1101 S Rn(4) ]", mnemonic="SUB")
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 1110 S Rn(4) ]", mnemonic="RSB")
def A_default(obj,i,S,Rn,imm3,Rd,imm8):
  obj.setflags = (S==1)
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  if BadReg(Rd) or Rn==15: raise InstructionError(obj)
  obj.imm32 = ThumbExpandImm(i+imm3+imm8)
  obj.operands = [obj.d,obj.n,obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 1 0000 0 Rn(4) ]", mnemonic="ADD")
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 1 0101 0 Rn(4) ]", mnemonic="SUB")
def A_default(obj,i,Rn,imm3,Rd,imm8):
  obj.setflags = False
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  if BadReg(Rd) : raise InstructionError(obj)
  obj.imm32 = ThumbExpandImm(i+imm3+imm8)
  obj.operands = [obj.d,obj.n,obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) 11101 01 0000 S Rn(4) ]", mnemonic="AND")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) 11101 01 0001 S Rn(4) ]", mnemonic="BIC")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) 11101 01 0010 S Rn(4) ]", mnemonic="ORR")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) 11101 01 0011 S Rn(4) ]", mnemonic="ORN")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) 11101 01 0100 S Rn(4) ]", mnemonic="EOR")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) 11101 01 1000 S Rn(4) ]", mnemonic="ADD")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) 11101 01 1010 S Rn(4) ]", mnemonic="ADC")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) 11101 01 1101 S Rn(4) ]", mnemonic="SUB")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) 11101 01 1110 S Rn(4) ]", mnemonic="RSB")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) 11101 01 1011 S Rn(4) ]", mnemonic="SBC")
def A_sreg(obj,S,Rn,imm3,Rd,imm2,stype,Rm):
  obj.setflags = (S==1)
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  obj.m = DecodeShift(stype,env.regs[Rm],imm3<<2+imm2)
  if Rn==15 or BadReg(Rd) or BadReg(Rm): raise InstructionError(obj)
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 10101 0 1111 ]", mnemonic="ADR", add=False )
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 10000 0 1111 ]", mnemonic="ADR", add=True )
def A_adr(obj,i,imm3,Rd,imm8):
  obj.d = env.regs[Rd]
  if BadReg(Rd) : raise InstructionError(obj)
  obj.imm32 = ThumbExpandImm(i+imm3+imm8)
  obj.operands = [obj.d,obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 imm3(3) Rd(4) imm2(2) 10 Rm(4) 11101 01 0010 S 1111 ]", mnemonic="ASR")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) 00 Rm(4) 11101 01 0010 S 1111 ]", mnemonic="LSL")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) 01 Rm(4) 11101 01 0010 S 1111 ]", mnemonic="LSR")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) 11 Rm(4) 11101 01 0010 S 1111 ]", mnemonic="ROR")
def A_default(obj,S,imm3,Rd,imm2,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  if BadReg(Rd) or BadReg(Rm): raise InstructionError(obj)
  obj.imm5 = env.cst(imm3<<2+imm2,5)
  obj.operands = [obj.d,obj.n,obj.imm5]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 010 0 10 S Rn(4) ]", mnemonic="ASR")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 010 0 00 S Rn(4) ]", mnemonic="LSL")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 010 0 01 S Rn(4) ]", mnemonic="LSR")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 010 0 11 S Rn(4) ]", mnemonic="ROR")
def A_default(obj,S,Rn,Rd,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  if BadReg(Rd) or BadReg(Rm) or BadReg(Rn): raise InstructionError(obj)
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 1 0 #J1 0 #J2 #imm11(11) 11110 #S .cond(4) #imm6(6) ]", mnemonic="B")
def A_label(obj,S,imm6,J1,J2,imm11):
  v = int(S+J2+J1+imm6+imm11+'0',2)
  obj.imm32 = env.cst(v,21).signextend(32)
  obj.operands = [obj.imm32]
  obj.type = type_control_flow

@ispec("32[ 10 #J1 1 #J2 #imm11(11) 11110 #S #imm10(10) ]", mnemonic="B")
@ispec("32[ 11 #J1 1 #J2 #imm11(11) 11110 #S #imm10(10) ]", mnemonic="BL")
def A_label(obj,S,imm10,J1,J2,imm11):
  I1 = '1' if J1==S else '0'
  I2 = '1' if J2==S else '0'
  v = int(S+I1+I2+imm10+imm11+'0',2)
  obj.imm32 = env.cst(v,25).signextend(32)
  obj.operands = [obj.imm32]
  obj.type = type_control_flow
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 imm3(3) Rd(4) imm2(2) 0 msb(5) 11110 0 11 011 0 1111 ]", mnemonic="BFC")
def A_bits(obj,imm3,Rd,imm2,msb):
  obj.d = env.regs[Rd]
  if BadReg(Rd) : raise InstructionError(obj)
  obj.msbit = msb
  obj.lsbit = imm3<<2+imm2
  obj.operands = [obj.d, obj.lsbit, obj.msbit-obj.lsbit+1]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 imm3(3) Rd(4) imm2(2) 0 msb(5) 11110 0 11 011 0 Rn(4) ]", mnemonic="BFI")
def A_bits(obj,Rn,imm3,Rd,imm2,msb):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  if BadReg(Rd) or Rn==13: raise InstructionError(obj)
  obj.msbit = msb
  obj.lsbit = imm3<<2+imm2
  obj.operands = [obj.d, obj.n, obj.lsbit, obj.msbit-obj.lsbit+1]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 11 J1 0 J2 #imm10L(10) 0 11110 S #imm10H(10) ]", mnemonic="BLX")
def A_label(obj,S,imm10H,J1,J2,imm10L):
  I1, I2 = str(~(J1^S)&0x1), str(~(J2^S)&0x1)
  v = int(str(S)+I1+I2+imm10H+imm10L+'00',2)
  obj.imm32 = env.cst(v,25).signextend(32)
  obj.operands = [obj.imm32]
  obj.type = type_control_flow
  obj.cond = env.CONDITION_AL

@ispec("32[ 10 0 0 1111 00000000 11110 0 1111 00 Rm(4) ]", mnemonic="BXJ")
def A_default(obj,Rm):
  obj.m = env.regs[Rm]
  obj.operands = [obj.m]
  obj.type = type_control_flow
  obj.cond = env.CONDITION_AL

@ispec("32[ 10 0 0 1111 0010 1111 11110 0 111 01 1 1111 ]", mnemonic="CLREX")
@ispec("32[ 10 0 0 0000 0000 0000 11110 0 111 01 0 1111 ]", mnemonic="NOP")
@ispec("32[ 10 0 0 0000 0000 0100 11110 0 111 01 0 1111 ]", mnemonic="SEV")
@ispec("32[ 10 0 0 0000 0000 0010 11110 0 111 01 0 1111 ]", mnemonic="WFE")
@ispec("32[ 10 0 0 0000 0000 0011 11110 0 111 01 0 1111 ]", mnemonic="WFI")
@ispec("32[ 10 0 0 0000 0000 0001 11110 0 111 01 0 1111 ]", mnemonic="YIELD")
def A_default(obj):
  obj.type = type_cpu_state
  obj.cond = env.CONDITION_AL

@ispec("32[ 1111 Rd(4) 1 000 Rm(4) 11111 010 1 011 rm(4) ]", mnemonic="CLZ")
@ispec("32[ 1111 Rd(4) 1 010 Rm(4) 11111 010 1 001 rm(4) ]", mnemonic="RBIT")
@ispec("32[ 1111 Rd(4) 1 000 Rm(4) 11111 010 1 001 rm(4) ]", mnemonic="REV")
@ispec("32[ 1111 Rd(4) 1 001 Rm(4) 11111 010 1 001 rm(4) ]", mnemonic="REV16")
@ispec("32[ 1111 Rd(4) 1 011 Rm(4) 11111 010 1 001 rm(4) ]", mnemonic="REVSH")
def A_default(obj,rm,Rd,Rm):
  assert rm==Rm
  obj.d = env.regs[Rn]
  obj.m = env.regs[Rm]
  if BadReg(Rd) or BadReg(Rm) : raise InstructionError(obj)
  obj.operands = [obj.d,obj.m]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 #imm3(3) 1111 #imm8(8) 11110 #i 0 1000 1 Rn(4) ]", mnemonic="CMN")
@ispec("32[ 0 #imm3(3) 1111 #imm8(8) 11110 #i 0 1101 1 Rn(4) ]", mnemonic="CMP")
@ispec("32[ 0 #imm3(3) 1111 #imm8(8) 11110 #i 0 0100 1 Rn(4) ]", mnemonic="TEQ")
@ispec("32[ 0 #imm3(3) 1111 #imm8(8) 11110 #i 0 0000 1 Rn(4) ]", mnemonic="TST")
def A_default(obj,i,Rn,imm3,imm8):
  obj.n = env.regs[Rn]
  if Rn==15: raise InstructionError(obj)
  obj.imm32 = ThumbExpandImm(i+imm3+imm8)
  obj.operands = [obj.n, obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 #imm3(3) 1111 #imm2(2) stype(2) Rm(4) 11101 01 1000 1 Rn(4) ]", mnemonic="CMN")
@ispec("32[ 0 #imm3(3) 1111 #imm2(2) stype(2) Rm(4) 11101 01 1101 1 Rn(4) ]", mnemonic="CMP")
@ispec("32[ 0 #imm3(3) 1111 #imm2(2) stype(2) Rm(4) 11101 01 0100 1 Rn(4) ]", mnemonic="TEQ")
@ispec("32[ 0 #imm3(3) 1111 #imm2(2) stype(2) Rm(4) 11101 01 0000 1 Rn(4) ]", mnemonic="TST")
def A_sreg(obj,i,Rn,imm3,imm2,stype,Rm):
  obj.n = env.regs[Rn]
  obj.m = DecodeShift(stype,env.regs[Rm],imm3<<2+imm2)
  if Rn==15 or BadReg(Rm): raise InstructionError(obj)
  obj.operands = [obj.n, obj.m]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 10 000 000 1111 .option(4) 11110 0 111 01 0 1111 ]", mnemonic="DBG")
@ispec("32[ 10 00 1111 0101 .option(4) 11110 0 111 01 1 1111 ]", mnemonic="DMB")
@ispec("32[ 10 00 1111 0100 .option(4) 11110 0 111 01 1 1111 ]", mnemonic="DSB")
@ispec("32[ 10 00 1111 0110 .option(4) 11110 0 111 01 1 1111 ]", mnemonic="ISB")
def A_default(obj):
  obj.type = type_cpu_state

@ispec("32[ #P #M 0 #register_list(13) 11101 00 010 W 1 Rn(4) ]", mnemonic="LDM")
@ispec("32[ #P #M 0 #register_list(13) 11101 00 100 W 1 Rn(4) ]", mnemonic="LDMDB")
def A_reglist(obj,W,Rn,P,M,register_list):
  obj.n = env.regs[Rn]
  obj.registers = [env.regs[i] for i,r in enumerate(register_list[::-1]+'0'+M+P) if r=='1']
  if Rn==15 or len(obj.registers)<2 or (P=='1' and M=='1'): raise InstructionError(obj)
  obj.wback = (W==1)
  obj.operands = [obj.n, obj.registers]
  obj.type = type_data_processing
  if env.pc in obj.registers: obj.type = type_control_flow
  obj.cond = env.CONDITION_AL

@ispec("32[ 0  #M 0 #register_list(13) 11101 00 010 W 0 Rn(4) ]", mnemonic="STM")
@ispec("32[ 0  #M 0 #register_list(13) 11101 00 100 W 0 Rn(4) ]", mnemonic="STMDB")
def A_reglist(obj,W,Rn,M,register_list):
  obj.n = env.regs[Rn]
  obj.registers = [env.regs[i] for i,r in enumerate(register_list[::-1]+'0'+M) if r=='1']
  if Rn==15 or len(obj.registers)<2 : raise InstructionError(obj)
  obj.wback = (W==1)
  obj.operands = [obj.n, obj.registers]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) imm12(12) 11111 00 0 1 10 1 Rn(4) ]", mnemonic="LDR")
@ispec("32[ Rt(4) imm12(12) 11111 00 0 1 00 1 Rn(4) ]", mnemonic="LDRB")
@ispec("32[ Rt(4) imm12(12) 11111 00 0 1 01 1 Rn(4) ]", mnemonic="LDRH")
@ispec("32[ Rt(4) imm12(12) 11111 00 1 1 00 1 Rn(4) ]", mnemonic="LDRSB")
@ispec("32[ Rt(4) imm12(12) 11111 00 1 1 01 1 Rn(4) ]", mnemonic="LDRSH")
@ispec("32[ Rt(4) imm12(12) 11111 00 0 1 10 0 Rn(4) ]", mnemonic="STR")
@ispec("32[ Rt(4) imm12(12) 11111 00 0 1 00 0 Rn(4) ]", mnemonic="STRB")
@ispec("32[ Rt(4) imm12(12) 11111 00 0 1 01 0 Rn(4) ]", mnemonic="STRH")
def A_default(obj,Rn,Rt,imm12):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  if Rt==15: raise InstructionError(obj) # see PLDxx
  obj.imm32 = env.cst(imm12,32)
  obj.index = True
  obj.add = True
  obj.wback = False
  obj.operands = [obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) 1 P U W imm8(8) 11111 00 0 0 10 1 Rn(4) ]", mnemonic="LDR")
@ispec("32[ Rt(4) 1 P U W imm8(8) 11111 00 0 0 00 1 Rn(4) ]", mnemonic="LDRB")
@ispec("32[ Rt(4) 1 P U W imm8(8) 11111 00 0 0 01 1 Rn(4) ]", mnemonic="LDRH")
@ispec("32[ Rt(4) 1 P U W imm8(8) 11111 00 1 0 00 1 Rn(4) ]", mnemonic="LDRSB")
@ispec("32[ Rt(4) 1 P U W imm8(8) 11111 00 1 0 01 1 Rn(4) ]", mnemonic="LDRSH")
@ispec("32[ Rt(4) 1 P U W imm8(8) 11111 00 0 0 10 0 Rn(4) ]", mnemonic="STR")
@ispec("32[ Rt(4) 1 P U W imm8(8) 11111 00 0 0 00 0 Rn(4) ]", mnemonic="STRB")
@ispec("32[ Rt(4) 1 P U W imm8(8) 11111 00 0 0 01 0 Rn(4) ]", mnemonic="STRH")
def A_deref(obj,Rn,Rt,P,U,W,imm8):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  if Rt==15: raise InstructionError(obj) # see PLDxx
  obj.imm32 = env.cst(imm8,32)
  if P==1 and U==1 and W==0:
      obj.mnemonic += 'T'
      obj.postindex = False
      obj.register_form = False
  else:
      obj.index = (P==1)
      obj.wback = (W==1)
      if BadReg(Rt) and (Rn==Rt): raise InstructionError(obj)
  obj.add = (U==1)
  obj.operands = [obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) imm12(12) 11111 00 0 U 10 1 1111 ]", mnemonic="LDR")
@ispec("32[ Rt(4) imm12(12) 11111 00 0 U 00 1 1111 ]", mnemonic="LDRB")
@ispec("32[ Rt(4) imm12(12) 11111 00 0 U 01 1 1111 ]", mnemonic="LDRH")
@ispec("32[ Rt(4) imm12(12) 11111 00 1 U 00 1 1111 ]", mnemonic="LDRSB")
@ispec("32[ Rt(4) imm12(12) 11111 00 1 U 01 1 1111 ]", mnemonic="LDRSH")
def A_deref(obj,U,Rt,imm12):
  obj.n = env.pc
  obj.t = env.regs[Rt]
  if Rt==15: raise InstructionError(obj) # see PLDxx
  obj.imm32 = env.cst(imm12,32)
  obj.add = (U==1)
  obj.operands = [obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) 0 00000 imm2(2) Rm(4) 11111 00 0 0 10 1 Rn(4) ]", mnemonic="LDR")
@ispec("32[ Rt(4) 0 00000 imm2(2) Rm(4) 11111 00 0 0 00 1 Rn(4) ]", mnemonic="LDRB")
@ispec("32[ Rt(4) 0 00000 imm2(2) Rm(4) 11111 00 0 0 01 1 Rn(4) ]", mnemonic="LDRH")
@ispec("32[ Rt(4) 0 00000 imm2(2) Rm(4) 11111 00 1 0 00 1 Rn(4) ]", mnemonic="LDRSB")
@ispec("32[ Rt(4) 0 00000 imm2(2) Rm(4) 11111 00 1 0 01 1 Rn(4) ]", mnemonic="LDRSH")
@ispec("32[ Rt(4) 0 00000 imm2(2) Rm(4) 11111 00 0 0 10 0 Rn(4) ]", mnemonic="STR")
@ispec("32[ Rt(4) 0 00000 imm2(2) Rm(4) 11111 00 0 0 00 0 Rn(4) ]", mnemonic="STRB")
@ispec("32[ Rt(4) 0 00000 imm2(2) Rm(4) 11111 00 0 0 01 0 Rn(4) ]", mnemonic="STRH")
def A_deref(obj,Rn,Rt,imm2,Rm):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.m = env.regs[Rm]<<imm2
  if BadReg(Rm): raise InstructionError(obj)
  obj.index = True
  obj.add = True
  obj.wback = False
  obj.operands = [obj.t, obj.n, obj.m]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) Rt2(4) imm8(8) 11101 00 P U 1 W 1 Rn(4) ]", mnemonic="LDRD")
@ispec("32[ Rt(4) Rt2(4) imm8(8) 11101 00 P U 1 W 0 Rn(4) ]", mnemonic="STRD")
def A_deref(obj,P,U,W,Rn,Rt,Rt2,imm8):
  obj.t = env.regs[Rt]
  obj.t2 = env.regs[Rt2]
  obj.n = env.regs[Rn]
  obj.imm32 = env.cst(imm8<<2,32)
  obj.index = (P==1)
  obj.wback = (W==1)
  obj.add = (U==1)
  if obj.wback and (Rn==Rt or Rn==Rt2): raise InstructionError(obj)
  if BadReg(Rt) or BadReg(Rt2) or Rt==Rt2: raise InstructionError(obj)
  obj.operands = [obj.t, obj.t2, obj.n, obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) 1111 imm8(8) 11101 00 0 0 1 0 1 Rn(4) ]", mnemonic="LDREX")
def A_deref(obj,Rn,Rt,imm8):
  obj.t = env.regs[Rt]
  obj.n = env.regs[Rn]
  if BadReg(Rt) or Rn==15: raise InstructionError(obj)
  obj.imm32 = env.cst(imm8<<2,32)
  obj.operands = [obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) Rd(4) imm8(8) 11101 00 0 0 1 0 0 Rn(4) ]", mnemonic="STREX")
def A_deref(obj,Rn,Rt,Rd,imm8):
  obj.d = env.regs[Rd]
  obj.t = env.regs[Rt]
  obj.n = env.regs[Rn]
  if BadReg(Rd) or BadReg(Rt) or Rn==15: raise InstructionError(obj)
  obj.imm32 = env.cst(imm8<<2,32)
  obj.operands = [obj.d, obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) 1111 0100 1111 11101 0001101 Rn(4) ]", mnemonic="LDREXB")
@ispec("32[ Rt(4) 1111 0101 1111 11101 0001101 Rn(4) ]", mnemonic="LDREXH")
def A_deref(obj,Rn,Rt):
  obj.t = env.regs[Rt]
  obj.n = env.regs[Rn]
  if BadReg(Rt) or Rn==15: raise InstructionError(obj)
  obj.operands = [obj.t, obj.n]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) 1111 0100 Rd(4) 11101 0001100 Rn(4) ]", mnemonic="STREXB")
@ispec("32[ Rt(4) 1111 0101 Rd(4) 11101 0001100 Rn(4) ]", mnemonic="STREXH")
def A_deref(obj,Rn,Rt,Rd):
  obj.d = env.regs[Rd]
  obj.t = env.regs[Rt]
  obj.n = env.regs[Rn]
  if BadReg(Rd) or BadReg(Rt) or Rn==15: raise InstructionError(obj)
  obj.operands = [obj.d, obj.t, obj.n]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) Rt2(4) 0111 1111 11101 000110 1 Rn(4) ]", mnemonic="LDREXD")
def A_deref(obj,Rn,Rt,Rt2):
  obj.t = env.regs[Rt]
  obj.t2 = env.regs[Rt2]
  obj.n = env.regs[Rn]
  if BadReg(Rt2) or BadReg(Rt) or Rn==15 or Rt==Rt2: raise InstructionError(obj)
  obj.operands = [obj.t, obj.t2, obj.n]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) Rt2(4) 0111 Rd(4) 11101 000110 0 Rn(4) ]", mnemonic="STREXD")
def A_deref(obj,Rn,Rt,Rt2,Rd):
  obj.d = env.regs[Rd]
  obj.t = env.regs[Rt]
  obj.t2 = env.regs[Rt2]
  obj.n = env.regs[Rn]
  if BadReg(Rd) or BadReg(Rt2) or BadReg(Rt): raise InstructionError(obj)
  if Rd==Rn or Rd==Rt or Rd==Rt2: raise InstructionError(obj)
  obj.operands = [obj.d, obj.t, obj.t2, obj.n]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Ra(4) Rd(4) 0000 Rm(4) 11111 0110 000 Rn(4) ]", mnemonic="MLA", setflags=False)
@ispec("32[ Ra(4) Rd(4) 0001 Rm(4) 11111 0110 000 Rn(4) ]", mnemonic="MLS")
def A_default(obj,Rn,Ra,Rd,Rm):
  obj.n = env.regs[Rn]
  obj.a = env.regs[Ra]
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  if BadReg(Rn) or Ra==13 or BadReg(Rd) or BadReg(Rm): raise InstructionError(obj)
  if obj.mnemonic=="MLS" and Ra==15: raise InstructionError(obj)
  obj.operands = [obj.d, obj.n, obj.m, obj.a]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 0010 S 1111 ]", mnemonic="MOV")
@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 0 0011 S 1111 ]", mnemonic="MVN")
def A_default(obj,i,S,imm3,Rd,imm8):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  if BadReg(Rd): raise InstructionError(obj)
  obj.imm32 = ThumbExpandImm(i+imm3+imm8)
  obj.operands = [obj.d, obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 10 0 1 0 0 #imm4(4) ]", mnemonic="MOV")
def A_default(obj,i,imm4,imm3,Rd,imm8):
  obj.setflags = False
  obj.d = env.regs[Rd]
  if BadReg(Rd): raise InstructionError(obj)
  obj.imm32 = env.cst(int(imm4+i+imm3+imm8,2),32)
  obj.operands = [obj.d, obj.imm32]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 000 Rd(4) 0000 Rm(4) 11101 01 0010 S 1111 ]", mnemonic="MOV")
@ispec("32[ 0 000 Rd(4) 0011 Rm(4) 11101 01 0010 S 1111 ]", mnemonic="RRX")
def A_default(obj,S,Rd,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d, obj.m]
  obj.type = type_data_processing
  if obj.mnemonic=="MOV" and (obj.d is env.pc):
    obj.type = type_control_flow
  if obj.mnemonic=="RRX":
      if BadReg(Rd) or BadReg(Rm): raise InstructionError(obj)
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 #imm3(3) Rd(4) #imm8(8) 11110 #i 10 1 1 0 0 #imm4(4) ]", mnemonic="MOVT")
def A_default(obj,i,imm4,imm3,Rd,imm8):
  obj.d = env.regs[Rd]
  if BadReg(Rd): raise InstructionError(obj)
  obj.imm16 = env.cst(int(imm4+i+imm3+imm8,2),16)
  obj.operands = [obj.d, obj.imm16]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 10 0 0 Rd(4) 00000000 11110 0 1111 1 0 1111 ]", mnemonic="MRS")
def A_default(obj,Rd):
  obj.d = env.regs[Rd]
  if BadReg(Rd): raise InstructionError(obj)
  obj.operands = [obj.d, env.apsr]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 10 0 0 mask(2) 00 00000000 11110 0 1110 0 0 Rn(4) ]", mnemonic="MSR")
def instr_MSR(obj,Rn,mask):
  obj.n = env.regs[Rn]
  if mask==0: raise InstructionError(obj)
  obj.write_nzcvq = (mask&2)==2
  obj.write_g = (mask&1)==1
  obj.operands = [obj.n]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 1111 Rd(4) 0000 Rm(4) 11111 0110 000 Rn(4) ]", mnemonic="MUL")
def A_default(obj,Rn,Rd,Rm):
  obj.setflags = False
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  if BadReg(Rd) or BadReg(Rn) or BadReg(Rm): raise InstructionError(obj)
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 #imm3(3) Rd(4) #imm2(2) stype(2) Rm(4) 11101 01 0011 S 1111 ]", mnemonic="MVN")
def A_default(obj,S,imm3,Rd,imm2,stype,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.m = DecodeShift(stype,env.regs[Rm],imm3<<2+imm2)
  if BadReg(Rd) or BadReg(Rm): raise InstructionError(obj)
  obj.operands = [obj.d,obj.m]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 #imm3(3) Rd(4) #imm2(2) tb 0 Rm(4) 11101 01 0110 0 Rn(4) ]", mnemonic="PKH")
def A_default(obj,Rn,imm3,Rd,imm2,tb,Rm):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = DecodeShift(tb<<1,env.regs[Rm],imm3<<2+imm2)
  if BadReg(Rd) or BadReg(Rn) or BadReg(Rm): raise InstructionError(obj)
  obj.tbform = (tb==1)
  obj.operands = [obj.d, obj.n, obj.m]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 1111 imm(12) 11111 00 0 1 0 0 1 Rn(4) ]", mnemonic="PLD", add=True)
@ispec("32[ 1111 imm(12) 11111 00 0 1 0 1 1 Rn(4) ]", mnemonic="PLDW", add=True)
@ispec("32[ 1111 1100 imm(8) 11111 00 0 0 0 0 1 Rn(4) ]", mnemonic="PLD", add=False)
@ispec("32[ 1111 1100 imm(8) 11111 00 0 0 0 1 1 Rn(4) ]", mnemonic="PLDW", add=False)
@ispec("32[ 1111 imm(12) 11111 00 1 1 0 0 1 Rn(4) ]", mnemonic="PLI", add=True)
@ispec("32[ 1111 imm(12) 11111 00 1 1 0 1 1 Rn(4) ]", mnemonic="PLIW", add=True)
@ispec("32[ 11111 1100 imm(8) 1111 00 1 0 0 0 1 Rn(4) ]", mnemonic="PLI", add=False)
@ispec("32[ 11111 1100 imm(8) 1111 00 1 0 0 1 1 Rn(4) ]", mnemonic="PLIW", add=False)
def instr_PLx(obj,Rn,imm):
  obj.n = env.regs[Rn]
  obj.imm32 = env.cst(imm,32)
  obj.operands = [obj.n, obj.imm32]
  obj.type = type_cpu_state
  obj.cond = env.CONDITION_AL

@ispec("32[ 1111 imm12(12) 11111 00 0 U 00 1 1111 ]", mnemonic="PLD")
@ispec("32[ 1111 imm12(12) 11111 00 1 U 00 1 1111 ]", mnemonic="PLI")
def instr_PLx(obj,U,Rt,imm12):
  obj.n = env.pc
  obj.add = (U==1)
  obj.imm32 = env.cst(imm12,32)
  obj.operands = [obj.n, obj.imm32]
  obj.type = type_cpu_state
  obj.cond = env.CONDITION_AL

@ispec("32[ 1111 0 00000 imm2(2) Rm(4) 11111 00 0 0 00 1 Rn(4) ]", mnemonic="PLD", add=True)
@ispec("32[ 1111 0 00000 imm2(2) Rm(4) 11111 00 0 0 01 1 Rn(4) ]", mnemonic="PLDW", add=True)
@ispec("32[ 1111 0 00000 imm2(2) Rm(4) 11111 00 1 0 00 1 Rn(4) ]", mnemonic="PLI", add=True)
@ispec("32[ 1111 0 00000 imm2(2) Rm(4) 11111 00 1 0 01 1 Rn(4) ]", mnemonic="PLIW", add=True)
def instr_PLx(obj,W,Rn,imm2,Rm):
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]<<imm2
  obj.operands = [obj.n,obj.m]
  obj.type = type_cpu_state
  obj.cond = env.CONDITION_AL

@ispec("32[ #P #M 0 #register_list(13) 11101 00 010 1 1 1101 ]", mnemonic="POP")
def A_reglist(obj,P,M,register_list):
  obj.registers = [env.regs[i] for i,r in enumerate(register_list[::-1]+'0'+M+P) if r=='1']
  obj.operands = [obj.registers]
  obj.type = type_data_processing
  if env.pc in obj.registers:
      if env.sp in obj.registers: raise InstructionError(obj)
      obj.type = type_control_flow
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) 1 011 00000000 11111 00 0 0 10 1 1101 ]", mnemonic="POP")
def A_reglist(obj,Rt):
  obj.registers = [env.regs[Rt]]
  obj.operands = [obj.registers]
  obj.type = type_data_processing
  if env.pc in obj.registers:
      if env.sp in obj.registers: raise InstructionError(obj)
      obj.type = type_control_flow
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 #M 0 #register_list(13) 11101 00 100 1 0 1101 ]", mnemonic="PUSH")
def A_reglist(obj,M,register_list):
  obj.registers = [env.regs[i] for i,r in enumerate(register_list[::-1]+'0'+M+'0') if r=='1']
  if len(obj.registers)<2: raise InstructionError(obj)
  obj.operands = [obj.registers]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Rt(4) 1 101 00000000 11111 00 0 0 10 0 1101 ]", mnemonic="PUSH")
def A_reglist(obj,Rt):
  obj.registers = [env.regs[Rt]]
  if BadReg(Rt): raise InstructionError(obj)
  obj.operands = [obj.registers]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 1111 Rd(4) 1 000 Rm(4) 11111 010 1 000 Rn(4) ]", mnemonic="QADD")
@ispec("32[ 1111 Rd(4) 1 001 Rm(4) 11111 010 1 000 Rn(4) ]", mnemonic="QDADD")
@ispec("32[ 1111 Rd(4) 1 011 Rm(4) 11111 010 1 000 Rn(4) ]", mnemonic="QDSUB")
@ispec("32[ 1111 Rd(4) 1 010 Rm(4) 11111 010 1 000 Rn(4) ]", mnemonic="QSUB")
def A_default(obj,S,Rn,Rd,Rm):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  if BadReg(Rd) or BadReg(Rn) or BadReg(Rm): raise InstructionError(obj)
  obj.operands = [obj.d,obj.m,obj.n]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 1111 Rd(4) 0 001 Rm(4) 11111 010 1 001 Rn(4) ]", mnemonic="QADD16")
@ispec("32[ 1111 Rd(4) 0 001 Rm(4) 11111 010 1 000 Rn(4) ]", mnemonic="QADD8")
@ispec("32[ 1111 Rd(4) 0 001 Rm(4) 11111 010 1 010 Rn(4) ]", mnemonic="QASX")
@ispec("32[ 1111 Rd(4) 0 001 Rm(4) 11111 010 1 110 Rn(4) ]", mnemonic="QSAX")
@ispec("32[ 1111 Rd(4) 0 001 Rm(4) 11111 010 1 101 Rn(4) ]", mnemonic="QSUB16")
@ispec("32[ 1111 Rd(4) 0 001 Rm(4) 11111 010 1 100 Rn(4) ]", mnemonic="QSUB8")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 010 1 001 Rn(4) ]", mnemonic="SADD16")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 010 1 000 Rn(4) ]", mnemonic="SADD8")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 010 1 010 Rn(4) ]", mnemonic="SASX")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 010 1 110 Rn(4) ]", mnemonic="SSAX")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 010 1 101 Rn(4) ]", mnemonic="SSUB16")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 010 1 100 Rn(4) ]", mnemonic="SSUB8")
@ispec("32[ 1111 Rd(4) 0 010 Rm(4) 11111 010 1 001 Rn(4) ]", mnemonic="SHADD16")
@ispec("32[ 1111 Rd(4) 0 010 Rm(4) 11111 010 1 000 Rn(4) ]", mnemonic="SHADD8")
@ispec("32[ 1111 Rd(4) 0 010 Rm(4) 11111 010 1 010 Rn(4) ]", mnemonic="SHASX")
@ispec("32[ 1111 Rd(4) 0 010 Rm(4) 11111 010 1 110 Rn(4) ]", mnemonic="SHSAX")
@ispec("32[ 1111 Rd(4) 0 010 Rm(4) 11111 010 1 101 Rn(4) ]", mnemonic="SHSUB16")
@ispec("32[ 1111 Rd(4) 0 010 Rm(4) 11111 010 1 100 Rn(4) ]", mnemonic="SHSUB8")
@ispec("32[ 1111 Rd(4) 1 000 Rm(4) 11111 010 1 010 Rn(4) ]", mnemonic="SEL")
@ispec("32[ 1111 Rd(4) 1 000 Rm(4) 11111 011 0 101 Rn(4) ]", mnemonic="SMMUL")
@ispec("32[ 1111 Rd(4) 1 001 Rm(4) 11111 011 0 101 Rn(4) ]", mnemonic="SMMULR")
@ispec("32[ 1111 Rd(4) 1 000 Rm(4) 11111 011 0 010 Rn(4) ]", mnemonic="SMUAD")
@ispec("32[ 1111 Rd(4) 1 001 Rm(4) 11111 011 0 010 Rn(4) ]", mnemonic="SMUADX")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 011 0 001 Rn(4) ]", mnemonic="SMULBB")
@ispec("32[ 1111 Rd(4) 0 010 Rm(4) 11111 011 0 001 Rn(4) ]", mnemonic="SMULTB")
@ispec("32[ 1111 Rd(4) 0 001 Rm(4) 11111 011 0 001 Rn(4) ]", mnemonic="SMULBT")
@ispec("32[ 1111 Rd(4) 0 011 Rm(4) 11111 011 0 001 Rn(4) ]", mnemonic="SMULTT")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 011 0 011 Rn(4) ]", mnemonic="SMULWB")
@ispec("32[ 1111 Rd(4) 0 001 Rm(4) 11111 011 0 011 Rn(4) ]", mnemonic="SMULWT")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 011 0 100 Rn(4) ]", mnemonic="SMUSD")
@ispec("32[ 1111 Rd(4) 0 001 Rm(4) 11111 011 0 100 Rn(4) ]", mnemonic="SMUSDX")
@ispec("32[ 1111 Rd(4) 0 100 Rm(4) 11111 010 1 001 Rn(4) ]", mnemonic="UADD16")
@ispec("32[ 1111 Rd(4) 0 100 Rm(4) 11111 010 1 000 Rn(4) ]", mnemonic="UADD8")
@ispec("32[ 1111 Rd(4) 0 100 Rm(4) 11111 010 1 010 Rn(4) ]", mnemonic="UASX")
@ispec("32[ 1111 Rd(4) 0 100 Rm(4) 11111 010 1 110 Rn(4) ]", mnemonic="USAX")
@ispec("32[ 1111 Rd(4) 0 100 Rm(4) 11111 010 1 101 Rn(4) ]", mnemonic="USUB16")
@ispec("32[ 1111 Rd(4) 0 100 Rm(4) 11111 010 1 100 Rn(4) ]", mnemonic="USUB8")
@ispec("32[ 1111 Rd(4) 0 110 Rm(4) 11111 010 1 001 Rn(4) ]", mnemonic="UHADD16")
@ispec("32[ 1111 Rd(4) 0 110 Rm(4) 11111 010 1 000 Rn(4) ]", mnemonic="UHADD8")
@ispec("32[ 1111 Rd(4) 0 110 Rm(4) 11111 010 1 010 Rn(4) ]", mnemonic="UHASX")
@ispec("32[ 1111 Rd(4) 0 110 Rm(4) 11111 010 1 110 Rn(4) ]", mnemonic="UHSAX")
@ispec("32[ 1111 Rd(4) 0 110 Rm(4) 11111 010 1 101 Rn(4) ]", mnemonic="UHSUB16")
@ispec("32[ 1111 Rd(4) 0 110 Rm(4) 11111 010 1 100 Rn(4) ]", mnemonic="UHSUB8")
@ispec("32[ 1111 Rd(4) 0 101 Rm(4) 11111 010 1 001 Rn(4) ]", mnemonic="UQADD16")
@ispec("32[ 1111 Rd(4) 0 101 Rm(4) 11111 010 1 000 Rn(4) ]", mnemonic="UQADD8")
@ispec("32[ 1111 Rd(4) 0 101 Rm(4) 11111 010 1 010 Rn(4) ]", mnemonic="UQASX")
@ispec("32[ 1111 Rd(4) 0 101 Rm(4) 11111 010 1 110 Rn(4) ]", mnemonic="UQSAX")
@ispec("32[ 1111 Rd(4) 0 101 Rm(4) 11111 010 1 101 Rn(4) ]", mnemonic="UQSUB16")
@ispec("32[ 1111 Rd(4) 0 101 Rm(4) 11111 010 1 100 Rn(4) ]", mnemonic="UQSUB8")
@ispec("32[ 1111 Rd(4) 0 000 Rm(4) 11111 011 0 111 Rn(4) ]", mnemonic="USAD8")
@ispec("32[ 1111 Rd(4) 1 111 Rm(4) 11111 011 1 001 Rn(4) ]", mnemonic="SDIV")
@ispec("32[ 1111 Rd(4) 1 111 Rm(4) 11111 011 1 011 Rn(4) ]", mnemonic="UDIV")
def A_default(obj,Rn,Rd,Rm):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  if BadReg(Rd) or BadReg(Rn) or BadReg(Rm): raise InstructionError(obj)
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 imm3(3) Rd(4) imm2(2) 0 widthm1(5) 11110 0 11 010 0 Rn(4) ]", mnemonic="SBFX")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) 0 widthm1(5) 11110 0 11 110 0 Rn(4) ]", mnemonic="UBFX")
def A_default(obj,Rn,imm3,Rd,imm2,widthm1):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  if BadReg(Rd) or BadReg(Rn) : raise InstructionError(obj)
  obj.lsbit = imm3<<2+imm2
  obj.widthminus1 = widthm1
  obj.operands = [obj.d,obj.n,obj.lsb,obj.widthminus1+1]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ Ra(4) Rd(4) 0000 Rm(4) 11111 0110 001 Rn(4) ]", mnemonic="SMLABB")
@ispec("32[ Ra(4) Rd(4) 0010 Rm(4) 11111 0110 001 Rn(4) ]", mnemonic="SMLATB")
@ispec("32[ Ra(4) Rd(4) 0001 Rm(4) 11111 0110 001 Rn(4) ]", mnemonic="SMLABT")
@ispec("32[ Ra(4) Rd(4) 0011 Rm(4) 11111 0110 001 Rn(4) ]", mnemonic="SMLATT")
@ispec("32[ Ra(4) Rd(4) 0000 Rm(4) 11111 0110 010 Rn(4) ]", mnemonic="SMLAD")
@ispec("32[ Ra(4) Rd(4) 0001 Rm(4) 11111 0110 010 Rn(4) ]", mnemonic="SMLADX")
@ispec("32[ Ra(4) Rd(4) 0000 Rm(4) 11111 0110 011 Rn(4) ]", mnemonic="SMLAWB")
@ispec("32[ Ra(4) Rd(4) 0001 Rm(4) 11111 0110 011 Rn(4) ]", mnemonic="SMLAWT")
@ispec("32[ Ra(4) Rd(4) 0000 Rm(4) 11111 0110 100 Rn(4) ]", mnemonic="SMLSD")
@ispec("32[ Ra(4) Rd(4) 0001 Rm(4) 11111 0110 100 Rn(4) ]", mnemonic="SMLSDX")
@ispec("32[ Ra(4) Rd(4) 0000 Rm(4) 11111 0110 101 Rn(4) ]", mnemonic="SMMLA")
@ispec("32[ Ra(4) Rd(4) 0001 Rm(4) 11111 0110 101 Rn(4) ]", mnemonic="SMMLAR")
@ispec("32[ Ra(4) Rd(4) 0000 Rm(4) 11111 0110 110 Rn(4) ]", mnemonic="SMMLS")
@ispec("32[ Ra(4) Rd(4) 0001 Rm(4) 11111 0110 110 Rn(4) ]", mnemonic="SMMLSR")
@ispec("32[ Ra(4) Rd(4) 0000 Rm(4) 11111 0110 111 Rn(4) ]", mnemonic="USADA8")
def A_default(obj,Rd,Ra,Rm,Rn):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.a = env.regs[Ra]
  if BadReg(Rd) or BadReg(Rn) or BadReg(Rm) or Ra==13: raise InstructionError(obj)
  obj.operands = [obj.d,obj.n,obj.m,obj.a]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ RdLo(4) RdHi(4) 0000 Rm(4) 11111 0111 1 00 Rn(4) ]", mnemonic="SMLAL")
@ispec("32[ RdLo(4) RdHi(4) 0000 Rm(4) 11111 0111 0 00 Rn(4) ]", mnemonic="SMULL")
@ispec("32[ RdLo(4) RdHi(4) 0000 Rm(4) 11111 0111 1 10 Rn(4) ]", mnemonic="UMLAL")
@ispec("32[ RdLo(4) RdHi(4) 0000 Rm(4) 11111 0111 0 10 Rn(4) ]", mnemonic="UMULL")
@ispec("32[ RdLo(4) RdHi(4) 1000 Rm(4) 11111 0111 1 00 Rn(4) ]", mnemonic="SMLALBB")
@ispec("32[ RdLo(4) RdHi(4) 1010 Rm(4) 11111 0111 1 00 Rn(4) ]", mnemonic="SMLALTB")
@ispec("32[ RdLo(4) RdHi(4) 1001 Rm(4) 11111 0111 1 00 Rn(4) ]", mnemonic="SMLALBT")
@ispec("32[ RdLo(4) RdHi(4) 1011 Rm(4) 11111 0111 1 00 Rn(4) ]", mnemonic="SMLALTT")
@ispec("32[ RdLo(4) RdHi(4) 1100 Rm(4) 11111 0111 1 00 Rn(4) ]", mnemonic="SMLALD")
@ispec("32[ RdLo(4) RdHi(4) 1101 Rm(4) 11111 0111 1 00 Rn(4) ]", mnemonic="SMLALDX")
@ispec("32[ RdLo(4) RdHi(4) 1100 Rm(4) 11111 0111 1 01 Rn(4) ]", mnemonic="SMLSLD")
@ispec("32[ RdLo(4) RdHi(4) 1101 Rm(4) 11111 0111 1 01 Rn(4) ]", mnemonic="SMLSLDX")
@ispec("32[ RdLo(4) RdHi(4) 0110 Rm(4) 11111 0111 1 10 Rn(4) ]", mnemonic="UMAAL")
def A_default(obj,Rn,RdLo,RdHi,Rm):
  obj.setflags = False
  obj.dLo = env.regs[RdLo]
  obj.dHi = env.regs[RdHi]
  obj.m = env.regs[Rm]
  obj.n = env.regs[Rn]
  obj.operands = [obj.dLo,obj.dHi,obj.n,obj.m]
  if any(map(BadReg,(Rn,RdLo,RdHi,Rm))): raise InstructionError(obj)
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0 imm3(3) Rd(4) imm2(2) 0 sat_imm(5) 11110 0 11 00 sh 0 Rn(4) ]", mnemonic="SSAT")
@ispec("32[ 0 imm3(3) Rd(4) imm2(2) 0 sat_imm(5) 11110 0 11 10 sh 0 Rn(4) ]", mnemonic="USAT")
def A_default(obj,sh,Rn,imm3,Rd,imm2,sat_imm):
  obj.d = env.regs[Rd]
  obj.n = DecodeShift(sh<<1,env.regs[Rn],imm3<<2+imm2)
  if BadReg(Rd) or BadReg(Rn) : raise InstructionError(obj)
  obj.saturate_to = sat_imm+1
  obj.operands = [obj.d,obj.saturate_to,obj.n]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 0000 Rd(4) 00 00 sat_imm(4) 11110 0 11 00 1 0 Rn(4) ]", mnemonic="SSAT16")
@ispec("32[ 0000 Rd(4) 00 00 sat_imm(4) 11110 0 11 10 1 0 Rn(4) ]", mnemonic="USAT16")
def A_default(obj,Rn,Rd,sat_imm):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  if BadReg(Rd) or BadReg(Rn) : raise InstructionError(obj)
  obj.saturate_to = sat_imm+1
  obj.operands = [obj.d,obj.saturate_to,obj.n]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 100 Rn(4) ]", mnemonic="SXTAB")
@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 010 Rn(4) ]", mnemonic="SXTAB16")
@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 000 Rn(4) ]", mnemonic="SXTAH")
@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 101 Rn(4) ]", mnemonic="UXTAB")
@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 011 Rn(4) ]", mnemonic="UXTAB16")
@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 001 Rn(4) ]", mnemonic="UXTAH")
def A_default(obj,Rn,Rd,rotate,Rm):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  if BadReg(Rd) or BadReg(Rm) or Rn==13: raise InstructionError(obj)
  obj.rotation = rotate<<3
  obj.m = env.ror(env.regs[Rm],obj.rotation)
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 100 1111 ]", mnemonic="SXTB")
@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 010 1111 ]", mnemonic="SXTB16")
@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 000 1111 ]", mnemonic="SXTH")
@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 101 1111 ]", mnemonic="UXTB")
@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 011 1111 ]", mnemonic="UXTB16")
@ispec("32[ 1111 Rd(4) 1 0 rotate(2) Rm(4) 11111 010 0 001 1111 ]", mnemonic="UXTH")
def A_default(obj,Rd,rotate,Rm):
  obj.d = env.regs[Rd]
  if BadReg(Rd) or BadReg(Rm) : raise InstructionError(obj)
  obj.rotation = rotate<<3
  obj.m = env.ror(env.regs[Rm],obj.rotation)
  obj.operands = [obj.d,obj.m]
  obj.type = type_data_processing
  obj.cond = env.CONDITION_AL

@ispec("32[ 1111 0000 000 0 Rm(4) 11101 00 0 1 1 0 1 Rn(4) ]", mnemonic="TBB", is_tbh=False)
@ispec("32[ 1111 0000 000 1 Rm(4) 11101 00 0 1 1 0 1 Rn(4) ]", mnemonic="TBH", is_tbh=True)
def A_default(obj,Rn,Rm):
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  if Rn==13 or BadReg(Rm) : raise InstructionError(obj)
  obj.operands = [obj.n,obj.m]
  obj.type = type_control_flow
  obj.cond = env.CONDITION_AL

