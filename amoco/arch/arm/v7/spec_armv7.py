# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.

from amoco.arch.arm.v7 import env

from amoco.arch.core import *
from .utils import *

#------------------------------------------------------
# amoco ARMv7++ instruction specs:
#------------------------------------------------------

ISPECS = []

@ispec("32[ .cond(4) 00 1 0000 S Rn(4) Rd(4) imm12(12) ]", mnemonic="AND")
@ispec("32[ .cond(4) 00 1 0001 S Rn(4) Rd(4) imm12(12) ]", mnemonic="EOR")
@ispec("32[ .cond(4) 00 1 0010 S Rn(4) Rd(4) imm12(12) ]", mnemonic="SUB")
@ispec("32[ .cond(4) 00 1 0011 S Rn(4) Rd(4) imm12(12) ]", mnemonic="RSB")
@ispec("32[ .cond(4) 00 1 0100 S Rn(4) Rd(4) imm12(12) ]", mnemonic="ADD")
@ispec("32[ .cond(4) 00 1 0101 S Rn(4) Rd(4) imm12(12) ]", mnemonic="ADC")
@ispec("32[ .cond(4) 00 1 0110 S Rn(4) Rd(4) imm12(12) ]", mnemonic="SBC")
@ispec("32[ .cond(4) 00 1 0111 S Rn(4) Rd(4) imm12(12) ]", mnemonic="RSC")
@ispec("32[ .cond(4) 00 1 1100 S Rn(4) Rd(4) imm12(12) ]", mnemonic="ORR")
@ispec("32[ .cond(4) 00 1 1110 S Rn(4) Rd(4) imm12(12) ]", mnemonic="BIC")
def A_default(obj,S,Rn,Rd,imm12):
  obj.setflags = (S==1)
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  obj.imm32 = ARMExpandImm(imm12)
  obj.operands = [obj.d,obj.n,obj.imm32]
  obj.type = type_data_processing
  if obj.d is env.pc: obj.type = type_control_flow

@ispec("32[ .cond(4) 00 0 0000 S Rn(4) Rd(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="AND")
@ispec("32[ .cond(4) 00 0 0001 S Rn(4) Rd(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="EOR")
@ispec("32[ .cond(4) 00 0 0010 S Rn(4) Rd(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="SUB")
@ispec("32[ .cond(4) 00 0 0011 S Rn(4) Rd(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="RSB")
@ispec("32[ .cond(4) 00 0 0100 S Rn(4) Rd(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="ADD")
@ispec("32[ .cond(4) 00 0 0101 S Rn(4) Rd(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="ADC")
@ispec("32[ .cond(4) 00 0 0110 S Rn(4) Rd(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="SBC")
@ispec("32[ .cond(4) 00 0 0111 S Rn(4) Rd(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="RSC")
@ispec("32[ .cond(4) 00 0 1100 S Rn(4) Rd(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="ORR")
@ispec("32[ .cond(4) 00 0 1110 S Rn(4) Rd(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="BIC")
def A_sreg(obj,S,Rn,Rd,imm5,stype,Rm):
  obj.setflags = (S==1)
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  obj.m = DecodeShift(stype,env.regs[Rm],env.cst(imm5,5))
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing
  if obj.d is env.pc: obj.type = type_control_flow

@ispec("32[ .cond(4) 00 0 0000 S Rn(4) Rd(4) Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="AND")
@ispec("32[ .cond(4) 00 0 0001 S Rn(4) Rd(4) Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="EOR")
@ispec("32[ .cond(4) 00 0 0010 S Rn(4) Rd(4) Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="SUB")
@ispec("32[ .cond(4) 00 0 0011 S Rn(4) Rd(4) Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="RSB")
@ispec("32[ .cond(4) 00 0 0100 S Rn(4) Rd(4) Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="ADD")
@ispec("32[ .cond(4) 00 0 0101 S Rn(4) Rd(4) Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="ADC")
@ispec("32[ .cond(4) 00 0 0110 S Rn(4) Rd(4) Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="SBC")
@ispec("32[ .cond(4) 00 0 0111 S Rn(4) Rd(4) Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="RSC")
@ispec("32[ .cond(4) 00 0 1100 S Rn(4) Rd(4) Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="ORR")
@ispec("32[ .cond(4) 00 0 1110 S Rn(4) Rd(4) Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="BIC")
def A_sreg(obj,S,Rn,Rd,Rs,stype,Rm):
  obj.setflags = (S==1)
  obj.n = env.regs[Rn]
  if 15 in (Rd,Rs,Rm,Rn): raise InstructionError(obj)
  obj.d = env.regs[Rd]
  obj.m = DecodeShift(stype,env.regs[Rm],env.regs[Rs])
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00 1 0100 S 1111 Rd(4) imm12(12) ]", mnemonic="ADR", add=True )
@ispec("32[ .cond(4) 00 1 0010 S 1111 Rd(4) imm12(12) ]", mnemonic="ADR", add=False)
def A_adr(obj,S,Rd,imm12):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.imm32 = ARMExpandImm(imm12)
  obj.operands = [obj.d,obj.imm32]
  obj.type = type_data_processing
  if obj.d is env.pc: obj.type = type_control_flow

@ispec("32[ .cond(4) 00 1 1101 S 0000 Rd(4) imm12(12) ]", mnemonic="MOV")
@ispec("32[ .cond(4) 00 1 1111 S 0000 Rd(4) imm12(12) ]", mnemonic="MVN")
def A_default(obj,S,Rd,imm12):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.imm32 = ARMExpandImm(imm12)
  obj.operands = [obj.d,obj.imm32]
  obj.type = type_data_processing
  if obj.d is env.pc: obj.type = type_control_flow

@ispec("32[ .cond(4) 00 0 1101 S 0000 Rd(4) imm5(5) 100 Rm(4) ]", mnemonic="ASR")
@ispec("32[ .cond(4) 00 0 1101 S 0000 Rd(4) imm5(5) 000 Rm(4) ]", mnemonic="LSL")
@ispec("32[ .cond(4) 00 0 1101 S 0000 Rd(4) imm5(5) 010 Rm(4) ]", mnemonic="LSR")
@ispec("32[ .cond(4) 00 0 1101 S 0000 Rd(4) imm5(5) 110 Rm(4) ]", mnemonic="ROR")
def A_default(obj,S,Rd,imm5,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.type = type_data_processing
  if imm5==0:
      shift_n = 32 if obj.mnemonic in ('LSR','ASR') else imm5
      if obj.mnemonic=='ROR':
          obj.mnemonic='RRX'
          obj.operands = [obj.d,obj.m]
          return
  else:
      shift_n = imm5
  obj.operands = [obj.d,obj.m,env.cst(shift_n,5)]
  if obj.d is env.pc: obj.type = type_control_flow

@ispec("32[ .cond(4) 00 0 1101 S 0000 Rd(4) Rm(4) 0101 Rn(4) ]", mnemonic="ASR")
@ispec("32[ .cond(4) 00 0 1101 S 0000 Rd(4) Rm(4) 0001 Rn(4) ]", mnemonic="LSL")
@ispec("32[ .cond(4) 00 0 1101 S 0000 Rd(4) Rm(4) 0011 Rn(4) ]", mnemonic="LSR")
@ispec("32[ .cond(4) 00 0 0000 S Rd(4) 0000 Rm(4) 1001 Rn(4) ]", mnemonic="MUL")
@ispec("32[ .cond(4) 00 0 1101 S 0000 Rd(4) Rm(4) 0111 Rn(4) ]", mnemonic="ROR")
def A_default(obj,S,Rd,Rm,Rn):
  obj.setflags = (S==1)
  if 15 in (Rd,Rm,Rn): raise InstructionError(obj)
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.n = env.regs[Rn]
  if obj.mnemonic != 'MUL': obj.m = obj.m[0:8]
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 1010 imm24(24) ]", mnemonic="B")
def A_label(obj,imm24):
  obj.imm32 = env.cst(imm24<<2,26).signextend(32)
  obj.operands = [obj.imm32]
  obj.type = type_control_flow

@ispec("32[ .cond(4) 0111110 msb(5) Rd(4) lsb(5) 001 Rn(4) ]")
def A_bits(obj,msb,Rd,lsb,Rn):
  if Rd==15: raise InstructionError(obj)
  obj.d = env.regs[Rd]
  obj.msbit = msb
  obj.lsbit = lsb
  if Rn==15:
    obj.mnemonic = "BFC"
    obj.operands = [obj.d,obj.lsbit,obj.msbit-obj.lsbit+1]
  else:
    obj.mnemonic = "BFI"
    obj.n = env.regs[Rn]
    obj.operands = [obj.d,obj.n,obj.lsbit,obj.msbit-obj.lsbit+1]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00010010 imm12(12) 0111 imm4(4) ]", mnemonic="BKPT")
def A_default(obj,imm12,imm4):
  obj.imm32 = env.cst((imm12<<4)+imm4,32)
  obj.operands = [obj.imm32]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 101 1 imm24(24) ]", mnemonic="BL")
def A_label(obj,imm24):
  obj.imm32 = env.cst(imm24<<2,26).signextend(32)
  obj.operands = [obj.imm32]
  obj.type = type_control_flow

@ispec("32[  1111    101 H imm24(24) ]", menmonic="BLX")
def A_label(obj,H,imm24):
  H = 2*H
  obj.imm32 = env.cst((imm24<<2)+H,26).signextend(32)
  obj.operands = [obj.imm32]
  obj.type = type_control_flow

@ispec("32[ .cond(4) 00010010 1111 1111 1111 0011 Rm(4) ]", mnemonic="BLX")
@ispec("32[ .cond(4) 00010010 1111 1111 1111 0001 Rm(4) ]", mnemonic="BX")
@ispec("32[ .cond(4) 00010010 1111 1111 1111 0010 Rm(4) ]", mnemonic="BXJ")
def A_default(obj,Rm):
  if obj.mnemonic!="BX" and Rm==15: raise InstructionError(obj)
  obj.m = env.regs[Rm]
  obj.operands = [obj.m]
  obj.type = type_control_flow

@ispec("32[ 1111 01010111 1111 1111 0000 0001 1111 ]", mnemonic="CLREX")
def A_default(obj):
  obj.operands = []
  obj.type = type_data_processing

@ispec("32[ .cond(4) 0011 0010 0000 1111 0000 00000000 ]", mnemonic="NOP")
@ispec("32[ .cond(4) 0011 0010 0000 1111 0000 00000001 ]", mnemonic="YIELD")
@ispec("32[ .cond(4) 0011 0010 0000 1111 0000 00000010 ]", mnemonic="WFE")
@ispec("32[ .cond(4) 0011 0010 0000 1111 0000 00000011 ]", mnemonic="WFI")
@ispec("32[ .cond(4) 0011 0010 0000 1111 0000 00000100 ]", mnemonic="SEV")
def A_default(obj):
  obj.type = type_cpu_state

@ispec("32[ .cond(4) 00010110 1111 Rd(4) 1111 0001 Rm(4) ]", mnemonic="CLZ")
def A_default(obj,Rd,Rm):
  if 15 in (Rd,Rm): raise InstructionError(obj)
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d, obj.n]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00 1 1011 1 Rn(4) 0000 imm12(12) ]", mnemonic="CMN")
@ispec("32[ .cond(4) 00 1 1010 1 Rn(4) 0000 imm12(12) ]", mnemonic="CMP")
@ispec("32[ .cond(4) 00 1 1001 1 Rn(4) 0000 imm12(12) ]", mnemonic="TEQ")
@ispec("32[ .cond(4) 00 1 1000 1 Rn(4) 0000 imm12(12) ]", mnemonic="TST")
def A_default(obj,Rn,imm12):
  obj.n = env.regs[Rn]
  obj.imm32 = ARMExpandImm(imm12)
  obj.operands = [obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00 0 1011 1 Rn(4) 0000 imm5(5) stype(2) 0 Rm(4) ]", mnemonic="CMN")
@ispec("32[ .cond(4) 00 0 1010 1 Rn(4) 0000 imm5(5) stype(2) 0 Rm(4) ]", mnemonic="CMP")
@ispec("32[ .cond(4) 00 0 1001 1 Rn(4) 0000 imm5(5) stype(2) 0 Rm(4) ]", mnemonic="TEQ")
@ispec("32[ .cond(4) 00 0 1000 1 Rn(4) 0000 imm5(5) stype(2) 0 Rm(4) ]", mnemonic="TST")
def A_sreg(obj,Rn,imm5,stype,Rm):
  obj.n = env.regs[Rn]
  obj.m = DecodeShift(stype,env.regs[Rm],env.cst(imm5,5))
  obj.operands = [obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00 0 1011 1 Rn(4) 0000 Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="CMN")
@ispec("32[ .cond(4) 00 0 1010 1 Rn(4) 0000 Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="CMP")
@ispec("32[ .cond(4) 00 0 1001 1 Rn(4) 0000 Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="TEQ")
@ispec("32[ .cond(4) 00 0 1000 1 Rn(4) 0000 Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="TST")
def A_sreg(obj,Rn,Rs,stype,Rm):
  if 15 in (Rd,Rm,Rs): raise InstructionError(obj)
  obj.n = env.regs[Rn]
  obj.m = DecodeShift(stype,env.regs[Rm],env.regs[Rs])
  obj.operands = [obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00110010 0000 1111 0000 1111 .option(4) ]", mnemonic="DBG")
@ispec("32[  1111    01010111 1111 1111 0000 0101 .option(4) ]", mnemonic="DMB")
@ispec("32[  1111    01010111 1111 1111 0000 0100 .option(4) ]", mnemonic="DSB")
@ispec("32[  1111    01010111 1111 1111 0000 0110 .option(4) ]", mnemonic="ISB")
def A_default(obj):
  obj.operands = []
  obj.type = type_cpu_state

@ispec("32[ .cond(4) 100010 W 1 Rn(4) ~register_list(16) ]", mnemonic="LDM")
@ispec("32[ .cond(4) 100000 W 1 Rn(4) ~register_list(16) ]", mnemonic="LDMDA")
@ispec("32[ .cond(4) 100100 W 1 Rn(4) ~register_list(16) ]", mnemonic="LDMDB")
@ispec("32[ .cond(4) 100110 W 1 Rn(4) ~register_list(16) ]", mnemonic="LDMIB")
@ispec("32[ .cond(4) 100010 W 0 Rn(4) ~register_list(16) ]", mnemonic="STM")
@ispec("32[ .cond(4) 100000 W 0 Rn(4) ~register_list(16) ]", mnemonic="STMDA")
@ispec("32[ .cond(4) 100100 W 0 Rn(4) ~register_list(16) ]", mnemonic="STMDB")
@ispec("32[ .cond(4) 100110 W 0 Rn(4) ~register_list(16) ]", mnemonic="STMIB")
def A_reglist(obj,W,Rn,register_list):
  obj.n = env.regs[Rn]
  obj.registers = [env.regs[i] for i,r in enumerate(register_list) if r==1]
  obj.wback = (W==1)
  if Rn==15 or len(obj.registers)<1: raise InstructionError(obj)
  if obj.wback and (obj.n in obj.registers): raise InstructionError(obj)
  obj.operands = [obj.n,obj.registers]
  obj.type = type_data_processing
  if env.pc in obj.registers: obj.type = type_control_flow

@ispec("32[ .cond(4) 010 P U 0 W 1 Rn(4) Rt(4) imm12(12) ]", mnemonic="LDR")
@ispec("32[ .cond(4) 010 P U 1 W 1 Rn(4) Rt(4) imm12(12) ]", mnemonic="LDRB")
@ispec("32[ .cond(4) 010 P U 0 W 0 Rn(4) Rt(4) imm12(12) ]", mnemonic="STR")
@ispec("32[ .cond(4) 010 P U 1 W 0 Rn(4) Rt(4) imm12(12) ]", mnemonic="STRB")
def A_deref(obj,P,U,W,Rn,Rt,imm12):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.imm32 = env.cst(imm12,32)
  if Rn==15:
      if not (P==1 and W==0):
          raise InstructionError(obj)
  if P==0 and W==1:
    obj.mnemonic += 'T'
    obj.postindex = True
    obj.register_form = False
    if (15 in (Rt,Rn)) or (Rn==Rt): raise InstructionError(obj)
  else:
    obj.index = (P==1)
    obj.wback = (P==0)|(W==1)
    if obj.wback and Rn==Rt: raise InstructionError(obj)
  obj.add = (U==1)
  obj.operands = [obj.t,obj.n,obj.imm32]
  obj.type = type_data_processing
  if obj.t is env.pc : obj.type = type_control_flow

@ispec("32[ .cond(4) 011 P U 0 W 1 Rn(4) Rt(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="LDR")
@ispec("32[ .cond(4) 011 P U 1 W 1 Rn(4) Rt(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="LDRB")
@ispec("32[ .cond(4) 011 P U 0 W 0 Rn(4) Rt(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="STR")
@ispec("32[ .cond(4) 011 P U 1 W 0 Rn(4) Rt(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="STRB")
def A_deref(obj,P,U,W,Rn,Rt,imm5,stype,Rm):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.m = DecodeShift(stype,env.regs[Rm],imm5)
  if Rn==15:
      if not (P==1 and W==0):
          raise InstructionError(obj)
  if P==0 and W==1:
    obj.mnemonic += 'T'
    obj.postindex = True
    obj.register_form = True
    if (15 in (Rt,Rn,Rm)) or (Rn==Rt): raise InstructionError(obj)
  else:
    obj.index = (P==1)
    obj.wback = (P==0)|(W==1)
    if Rm==15: raise InstructionError(obj)
    if obj.wback and (Rn==15 or Rn==Rt): raise InstructionError(obj)
  obj.add = (U==1)
  obj.operands = [obj.t,obj.n,obj.m]
  obj.type = type_data_processing
  if obj.t is env.pc : obj.type = type_control_flow

@ispec("32[ .cond(4) 000 P U 1 W 0 Rn(4) Rt(4) imm4H(4) 1101 imm4L(4) ]", mnemonic="LDRD")
@ispec("32[ .cond(4) 000 P U 1 W 0 Rn(4) Rt(4) imm4H(4) 1111 imm4L(4) ]", mnemonic="STRD")
def A_deref(obj,P,U,W,Rn,Rt,imm4H,imm4L):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.t2 = env.regs[Rt+1]
  if Rt==14 or Rt%2==1: raise InstructionError(obj)
  obj.imm32 = env.cst(imm4H<<4+imm4L,32)
  obj.index = (P==1)
  obj.wback = (P==0)|(W==1)
  obj.add = (U==1)
  if obj.wback and (Rn==15 or Rn==Rt or Rn==Rt+1): raise InstructionError(obj)
  obj.operands = [obj.t,obj.t2,obj.n,obj.imm32]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 000 P U 0 W 0 Rn(4) Rt(4) 0000 1101 Rm(4) ]", mnemonic="LDRD")
@ispec("32[ .cond(4) 000 P U 0 W 0 Rn(4) Rt(4) 0000 1111 Rm(4) ]", mnemonic="STRD")
def A_deref(obj,P,U,W,Rn,Rt,Rm):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.m = env.regs[Rm]
  obj.t2 = env.regs[Rt+1]
  if P==0 and W==1: raise InstructionError(obj)
  if Rt==14 or Rm==15: raise InstructionError(obj)
  if Rn==15:
      if not (P==1 and W==0):
          raise InstructionError(obj)
  obj.index = (P==1)
  obj.wback = (P==0)|(W==1)
  if obj.wback and (Rn==15 or Rn==Rt or Rn==Rt+1): raise InstructionError(obj)
  obj.add = (U==1)
  obj.operands = [obj.t,obj.t2,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 0001100 1 Rn(4) Rt(4) 1111 1001 1111 ]", mnemonic="LDREX", imm32=env.cst(0,32))
@ispec("32[ .cond(4) 0001110 1 Rn(4) Rt(4) 1111 1001 1111 ]", mnemonic="LDREXB")
@ispec("32[ .cond(4) 0001101 1 Rn(4) Rt(4) 1111 1001 1111 ]", mnemonic="LDREXD")
@ispec("32[ .cond(4) 0001111 1 Rn(4) Rt(4) 1111 1001 1111 ]", mnemonic="LDREXH")
def A_default(obj,Rn,Rt):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  if Rn==15 or Rt==15: raise InstructionError(obj)
  obj.operands = [obj.t,obj.n]
  if obj.mnemonic=='LDREXD':
    obj.t2 = env.regs[Rt+1]
    obj.operands.insert(2, obj.t2)
  obj.type = type_data_processing

@ispec("32[ .cond(4) 0001100 0 Rn(4) Rd(4) 1111 1001 Rt(4) ]", mnemonic="STREX", imm32=env.cst(0,32))
@ispec("32[ .cond(4) 0001110 0 Rn(4) Rd(4) 1111 1001 Rt(4) ]", mnemonic="STREXB")
@ispec("32[ .cond(4) 0001101 0 Rn(4) Rd(4) 1111 1001 Rt(4) ]", mnemonic="STREXD")
@ispec("32[ .cond(4) 0001111 0 Rn(4) Rd(4) 1111 1001 Rt(4) ]", mnemonic="STREXH")
def A_default(obj,Rn,Rd,Rt):
  if 15 in (Rt,Rn,Rd) : raise InstructionError(obj)
  if Rn==Rd or Rd==Rt : raise InstructionError(obj)
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.operands = [obj.d, obj.t,obj.n]
  if obj.mnemonic=='STREXD':
    obj.t2 = env.regs[Rt+1]
    obj.operands.insert(2, obj.t2)
  obj.type = type_data_processing

@ispec("32[ .cond(4) 000 P U 1 W 1 Rn(4) Rt(4) imm4H(4) 1011 imm4L(4) ]", mnemonic="LDRH")
@ispec("32[ .cond(4) 000 P U 1 W 1 Rn(4) Rt(4) imm4H(4) 1101 imm4L(4) ]", mnemonic="LDRSB")
@ispec("32[ .cond(4) 000 P U 1 W 1 Rn(4) Rt(4) imm4H(4) 1111 imm4L(4) ]", mnemonic="LDRSH")
@ispec("32[ .cond(4) 000 P U 1 W 0 Rn(4) Rt(4) imm4H(4) 1011 imm4L(4) ]", mnemonic="STRH")
def A_deref(obj,P,U,W,Rn,Rt,imm4H,imm4L):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.imm32 = env.cst(imm4H<<4+imm4L,32)
  if P==0 and W==1:
    obj.mnemonic += "T"
    obj.postindex = True
    obj.register_form = False
    if (15 in (Rt,Rn)) or (Rn==Rt): raise InstructionError(obj)
  else:
    obj.index = (P==1)
    obj.wback = (P==0)|(W==1)
    if Rt==15 or (obj.wback and Rn==Rt): raise InstructionError(obj)
  obj.add = (U==1)
  obj.operands = [obj.t,obj.n,obj.imm32]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 000 P U 0 W 1 Rn(4) Rt(4) 0000 1011 Rm(4) ]", mnemonic="LDRH")
@ispec("32[ .cond(4) 000 P U 0 W 1 Rn(4) Rt(4) 0000 1101 Rm(4) ]", mnemonic="LDRSB")
@ispec("32[ .cond(4) 000 P U 0 W 1 Rn(4) Rt(4) 0000 1111 Rm(4) ]", mnemonic="LDRSH")
@ispec("32[ .cond(4) 000 P U 0 W 0 Rn(4) Rt(4) 0000 1011 Rm(4) ]", mnemonic="STRH")
def A_deref(obj,P,U,W,Rn,Rt,Rm):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.m = env.regs[Rm]
  if P==0 and W==1:
    obj.mnemonic += "T"
    obj.postindex = True
    obj.register_form = True
    if (15 in (Rt,Rn,Rm)) or (Rn==Rt): raise InstructionError(obj)
  else:
    obj.index = (P==1)
    obj.wback = (P==0)|(W==1)
    if Rt==15 or Rm==15: raise InstructionError(obj)
    if obj.wback and (Rn==15 or Rn==Rt): raise InstructionError(obj)
  obj.add = (U==1)
  obj.operands = [obj.t,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 0000001 S Rd(4) Ra(4) Rm(4) 1001 Rn(4) ]", mnemonic="MLA")
def A_default(obj,S,Rd,Ra,Rm,Rn):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.a = env.regs[Ra]
  if 15 in (Rd,Rn,Rm,Ra): raise InstructionError(obj)
  obj.operands = [obj.d,obj.n,obj.m,obj.a]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 0011 0000 imm4(4) Rd(4) imm12(12) ]", mnemonic="MOVW")
def A_default(obj,imm4,Rd,imm12):
  obj.setflags = False
  obj.d = env.regs[Rd]
  obj.imm32 = ARMExpandImm(imm4<<12+imm12)
  obj.operands = [obj.d,obj.imm32]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00 0 1101 S 0000 Rd(4) 00000 000 Rm(4) ]", mnemonic="MOV")
@ispec("32[ .cond(4) 00 0 1101 S 0000 Rd(4) 00000 110 Rm(4) ]", mnemonic="RRX")
def A_default(obj,S,Rd,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d,obj.m]
  obj.type = type_data_processing
  if obj.d is env.pc: obj.type = type_control_flow

@ispec("32[ .cond(4) 0011 0100 imm4(4) Rd(4) imm12(12) ]", mnemonic="MOVT")
def A_default(obj,imm4,Rd,imm12):
  obj.d = env.regs[Rd]
  if Rd==15: raise InstructionError(obj)
  obj.imm16 = env.cst(imm4<<12+imm12,16)
  obj.operands = [obj.d,obj.imm16]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00010000 1111 Rd(4) 0000 0000 0000 ]", mnemonic="MRS")
def A_default(obj,Rd):
  obj.d = env.regs[Rd]
  if Rd==15: raise InstructionError(obj)
  obj.operands = [obj.d, env.apsr]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00110010 ~mask(2) 00 1111 imm12(12) ]", mnemonic="MSR")
def instr_MSR(obj,mask,imm12):
  obj.imm32 = ARMExpandImm(imm12)
  obj.write_nzcvq = (mask[1]==1)
  obj.write_g     = (mask[0]==1)
  obj.operands = [obj.imm32]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00010 0 10 ~mask(2) 00 1111 0000 0000 Rn(4) ]", mnemonic="MSR")
def instr_MSR(obj,mask,Rn):
  obj.n = env.regs[Rn]
  obj.write_nzcvq = (mask[1]==1)
  obj.write_g     = (mask[0]==1)
  obj.operands = [obj.n]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00 0 1111 S 0000 Rd(4) imm5(5) stype(2) 0 Rm(4) ]", mnemonic="MVN")
def A_sreg(obj,S,Rd,imm5,stype,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.m = DecodeShift(stype,env.regs[Rm],imm5)
  obj.operands = [obj.d,obj.m]
  obj.type = type_data_processing
  if obj.d is env.pc: obj.type = type_control_flow

@ispec("32[ .cond(4) 00 0 1111 S 0000 Rd(4) Rs(4) 0 stype(2) 1 Rm(4) ]", mnemonic="MVN")
def A_sreg(obj,S,Rd,Rs,stype,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.m = DecodeShift(stype,env.regs[Rm],env.regs[Rs])
  if 15 in (Rd,Rm,Rs): raise InstructionError(obj)
  obj.operands = [obj.d,obj.m]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 01101000 Rn(4) Rd(4) imm5(5) tb 01 Rm(4) ]", mnemonic="PKH")
def A_sreg(obj,Rn,Rd,imm5,tb,Rm):
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  if 15 in (Rd,Rn,Rm): raise InstructionError(obj)
  obj.mnemonic += 'BT' if tb==0 else 'TB'
  obj.m = DecodeShift(tb<1,env.regs[Rm],env.cst(imm5,5))
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ 1111 01 0 1 U R 01 Rn(4) 1111 imm12(12) ]", mnemonic="PLD")
def instr_PLx(obj,U,R,Rn,imm12):
  obj.n = env.regs[Rn]
  obj.imm32 = cst(imm12,32)
  obj.add = (U==1)
  obj.is_pldw = (R==0)
  if obj._is_pldw: obj.mnemonic += 'W'
  obj.operands = [obj.n,obj.imm32]
  obj.type = type_cpu_state

@ispec("32[ 1111 01 1 1 U R 01 Rn(4) 1111 imm5(5) stype(2) 0 Rm(4) ]", mnemonic="PLD")
def instr_PLx(obj,U,R,Rn,imm5,stype,Rm):
  obj.n = env.regs[Rn]
  obj.m = DecodeShift(stype,env.regs[Rm],env.cst(imm5,5))
  if Rm==15: raise InstructionError(obj)
  obj.add = (U==1)
  obj.is_pldw = (R==0)
  if obj._is_pldw: obj.mnemonic += 'W'
  obj.operands = [obj.n,obj.m]
  obj.type = type_cpu_state

@ispec("32[ 1111 0100 U 101 Rn(4) 1111 imm12(12) ]", mnemonic="PLI")
def instr_PLx(obj,U,Rn,imm12):
  obj.n = env.regs[Rn]
  obj.imm32 = cst(imm12,32)
  obj.add = (U==1)
  obj.operands = [obj.n,obj.imm32]
  obj.type = type_cpu_state

@ispec("32[ 1111 0110 U 101 Rn(4) 1111 imm5(5) stype(2) 0 Rm(4) ]", mnemonic="PLI")
def instr_PLx(obj,U,Rn,imm5,stype,Rm):
  obj.n = env.regs[Rn]
  obj.m = DecodeShift(stype,env.regs[Rm],env.cst(imm5,5))
  obj.add = (U==1)
  obj.operands = [obj.n,obj.m]
  obj.type = type_cpu_state

@ispec("32[ .cond(4) 010100101101 Rt(4) 000000000100 ]", mnemonic="PUSH")
@ispec("32[ .cond(4) 010010011101 Rt(4) 000000000100 ]", mnemonic="POP")
def A_reglist(obj,Rt):
  obj.t = env.regs[Rt]
  if Rt==13: raise InstructionError(obj)
  obj.registers = [obj.t]
  obj.operands = [obj.registers]
  obj.type = type_data_processing
  if obj.mnemonic=='POP':
      if env.pc in obj.registers: obj.type = type_control_flow

@ispec("32[ .cond(4) 10010010 1101 ~register_list(16) ]", mnemonic="PUSH")
@ispec("32[ .cond(4) 10001011 1101 ~register_list(16) ]", mnemonic="POP")
def A_reglist(obj,register_list):
  obj.registers = [env.regs[i] for i,r in enumerate(register_list) if r==1]
  if env.regs[13] in obj.registers: raise InstructionError(obj)
  obj.operands = [obj.registers]
  obj.type = type_data_processing
  if obj.mnemonic=='POP':
      if env.pc in obj.registers: obj.type = type_control_flow

@ispec("32[ .cond(4) 00010000 Rn(4) Rd(4) 0000 0101 Rm(4) ]", mnemonic="QADD")
@ispec("32[ .cond(4) 00010010 Rn(4) Rd(4) 0000 0101 Rm(4) ]", mnemonic="QSUB")
@ispec("32[ .cond(4) 00010100 Rn(4) Rd(4) 0000 0101 Rm(4) ]", mnemonic="QDADD")
@ispec("32[ .cond(4) 00010110 Rn(4) Rd(4) 0000 0101 Rm(4) ]", mnemonic="QDSUB")
def A_default(obj,Rn,Rd,Rm):
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  if 15 in (Rd,Rm,Rn): raise InstructionError(obj)
  obj.operands = [obj.d,obj.m,obj.n]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 01100001 Rn(4) Rd(4) 1111 0001 Rm(4) ]", mnemonic="SADD16")
@ispec("32[ .cond(4) 01100001 Rn(4) Rd(4) 1111 1001 Rm(4) ]", mnemonic="SADD8")
@ispec("32[ .cond(4) 01100001 Rn(4) Rd(4) 1111 0011 Rm(4) ]", mnemonic="SASX")
@ispec("32[ .cond(4) 01100001 Rn(4) Rd(4) 1111 0101 Rm(4) ]", mnemonic="SSASX")
@ispec("32[ .cond(4) 01100001 Rn(4) Rd(4) 1111 0111 Rm(4) ]", mnemonic="SSUB16")
@ispec("32[ .cond(4) 01100001 Rn(4) Rd(4) 1111 1111 Rm(4) ]", mnemonic="SSUB8")
@ispec("32[ .cond(4) 01100010 Rn(4) Rd(4) 1111 0001 Rm(4) ]", mnemonic="QADD16")
@ispec("32[ .cond(4) 01100010 Rn(4) Rd(4) 1111 1001 Rm(4) ]", mnemonic="QADD8")
@ispec("32[ .cond(4) 01100010 Rn(4) Rd(4) 1111 0011 Rm(4) ]", mnemonic="QASX")
@ispec("32[ .cond(4) 01100010 Rn(4) Rd(4) 1111 0101 Rm(4) ]", mnemonic="QSAX")
@ispec("32[ .cond(4) 01100010 Rn(4) Rd(4) 1111 0111 Rm(4) ]", mnemonic="QSUB16")
@ispec("32[ .cond(4) 01100010 Rn(4) Rd(4) 1111 1111 Rm(4) ]", mnemonic="QSUB8")
@ispec("32[ .cond(4) 01100011 Rn(4) Rd(4) 1111 0001 Rm(4) ]", mnemonic="SHADD16")
@ispec("32[ .cond(4) 01100011 Rn(4) Rd(4) 1111 1001 Rm(4) ]", mnemonic="SHADD8")
@ispec("32[ .cond(4) 01100011 Rn(4) Rd(4) 1111 0011 Rm(4) ]", mnemonic="SHASX")
@ispec("32[ .cond(4) 01100011 Rn(4) Rd(4) 1111 0101 Rm(4) ]", mnemonic="SHSAX")
@ispec("32[ .cond(4) 01100011 Rn(4) Rd(4) 1111 0111 Rm(4) ]", mnemonic="SHSUB16")
@ispec("32[ .cond(4) 01100011 Rn(4) Rd(4) 1111 1111 Rm(4) ]", mnemonic="SHSUB8")
@ispec("32[ .cond(4) 01100101 Rn(4) Rd(4) 1111 0001 Rm(4) ]", mnemonic="UADD16")
@ispec("32[ .cond(4) 01100101 Rn(4) Rd(4) 1111 1001 Rm(4) ]", mnemonic="UADD8")
@ispec("32[ .cond(4) 01100101 Rn(4) Rd(4) 1111 0011 Rm(4) ]", mnemonic="UASX")
@ispec("32[ .cond(4) 01100110 Rn(4) Rd(4) 1111 0001 Rm(4) ]", mnemonic="UQADD16")
@ispec("32[ .cond(4) 01100110 Rn(4) Rd(4) 1111 0011 Rm(4) ]", mnemonic="UQASX")
@ispec("32[ .cond(4) 01100110 Rn(4) Rd(4) 1111 0101 Rm(4) ]", mnemonic="UQSAX")
@ispec("32[ .cond(4) 01100110 Rn(4) Rd(4) 1111 0111 Rm(4) ]", mnemonic="UQSUB16")
@ispec("32[ .cond(4) 01100110 Rn(4) Rd(4) 1111 1111 Rm(4) ]", mnemonic="UQSUB8")
@ispec("32[ .cond(4) 01100110 Rn(4) Rd(4) 1111 1001 Rm(4) ]", mnemonic="UQADD8")
@ispec("32[ .cond(4) 01100111 Rn(4) Rd(4) 1111 0001 Rm(4) ]", mnemonic="UHADD16")
@ispec("32[ .cond(4) 01100111 Rn(4) Rd(4) 1111 1001 Rm(4) ]", mnemonic="UHADD8")
@ispec("32[ .cond(4) 01100111 Rn(4) Rd(4) 1111 0011 Rm(4) ]", mnemonic="UHASX")
@ispec("32[ .cond(4) 01100111 Rn(4) Rd(4) 1111 0101 Rm(4) ]", mnemonic="UHSAX")
@ispec("32[ .cond(4) 01100111 Rn(4) Rd(4) 1111 0111 Rm(4) ]", mnemonic="UHSUB16")
@ispec("32[ .cond(4) 01100111 Rn(4) Rd(4) 1111 1111 Rm(4) ]", mnemonic="UHSUB8")
@ispec("32[ .cond(4) 01101000 Rn(4) Rd(4) 1111 1011 Rm(4) ]", mnemonic="SEL")
@ispec("32[ .cond(4) 01100101 Rn(4) Rd(4) 1111 0101 Rm(4) ]", mnemonic="USAX")
@ispec("32[ .cond(4) 01100101 Rn(4) Rd(4) 1111 0111 Rm(4) ]", mnemonic="USUB16")
@ispec("32[ .cond(4) 01100101 Rn(4) Rd(4) 1111 1111 Rm(4) ]", mnemonic="USUB8")
def A_default(obj,Rn,Rd,Rm):
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  if 15 in (Rd,Rm,Rn): raise InstructionError(obj)
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 01101111 1111 Rd(4) 1111 0011 Rm(4) ]", mnemonic="RBIT")
@ispec("32[ .cond(4) 01101011 1111 Rd(4) 1111 0011 Rm(4) ]", mnemonic="REV")
@ispec("32[ .cond(4) 01101011 1111 Rd(4) 1111 1011 Rm(4) ]", mnemonic="REV16")
@ispec("32[ .cond(4) 01101111 1111 Rd(4) 1111 1011 Rm(4) ]", mnemonic="REVSH")
def A_default(obj,Rd,Rm):
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  if 15 in (Rd,Rm): raise InstructionError(obj)
  obj.operands = [obj.d,obj.m]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 01111 01 widthm1(5) Rd(4) lsb(5) 101 Rn(4) ]", mnemonic="SBFX")
@ispec("32[ .cond(4) 01111 11 widthm1(5) Rd(4) lsb(5) 101 Rn(4) ]", mnemonic="UBFX")
def A_default(obj,widthm1,Rd,lsb,Rn):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  if 15 in (Rd,Rn): raise InstructionError(obj)
  obj.lsbit = env.cst(lsb,5)
  obj.widthminus1 = env.cst(widthm1,5)
  obj.operands = [obj.d,obj.n, obj.lsbit, obj.widthminus1+1]
  obj.type = type_data_processing

@ispec("32[ 1111 00010000 000 1 000000 E 0 0000 0000 ]", mnemonic="SETEND")
def instr_SETEND(obj,E):
  obj.set_bigend = (E==1)
  obj.type = type_cpu_state

@ispec("32[ .cond(4) 00000110 Rd(4) Ra(4) Rm(4) 1001 Rn(4) ]", mnemonic="MLS")
@ispec("32[ .cond(4) 00010000 Rd(4) Ra(4) Rm(4) 1000 Rn(4) ]", mnemonic="SMLABB")
@ispec("32[ .cond(4) 00010000 Rd(4) Ra(4) Rm(4) 1010 Rn(4) ]", mnemonic="SMLATB")
@ispec("32[ .cond(4) 00010000 Rd(4) Ra(4) Rm(4) 1100 Rn(4) ]", mnemonic="SMLABT")
@ispec("32[ .cond(4) 00010000 Rd(4) Ra(4) Rm(4) 1110 Rn(4) ]", mnemonic="SMLATT")
@ispec("32[ .cond(4) 01110000 Rd(4) Ra(4) Rm(4) 0001 Rn(4) ]", mnemonic="SMLAD")
@ispec("32[ .cond(4) 01110000 Rd(4) Ra(4) Rm(4) 0011 Rn(4) ]", mnemonic="SMLADX")
@ispec("32[ .cond(4) 00010010 Rd(4) Ra(4) Rm(4) 1000 Rn(4) ]", mnemonic="SMLAWB")
@ispec("32[ .cond(4) 00010010 Rd(4) Ra(4) Rm(4) 1100 Rn(4) ]", mnemonic="SMLAWT")
@ispec("32[ .cond(4) 01110000 Rd(4) Ra(4) Rm(4) 0101 Rn(4) ]", mnemonic="SMLSD")
@ispec("32[ .cond(4) 01110000 Rd(4) Ra(4) Rm(4) 0111 Rn(4) ]", mnemonic="SMLSDX")
@ispec("32[ .cond(4) 01110101 Rd(4) Ra(4) Rm(4) 0001 Rn(4) ]", mnemonic="SMMLA")
@ispec("32[ .cond(4) 01110101 Rd(4) Ra(4) Rm(4) 0011 Rn(4) ]", mnemonic="SMMLAR")
@ispec("32[ .cond(4) 01110101 Rd(4) Ra(4) Rm(4) 1101 Rn(4) ]", mnemonic="SMMLS")
@ispec("32[ .cond(4) 01110101 Rd(4) Ra(4) Rm(4) 1111 Rn(4) ]", mnemonic="SMMLSR")
@ispec("32[ .cond(4) 01111000 Rd(4) Ra(4) Rm(4) 0001 Rn(4) ]", mnemonic="USADA8")
def A_default(obj,Rd,Ra,Rm,Rn):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.a = env.regs[Ra]
  if 15 in (Rd,Rn,Rm,Ra): raise InstructionError(obj)
  obj.operands = [obj.d,obj.n,obj.m,obj.a]
  obj.type = type_data_processing

@ispec("32[ .cond(4) 0000111 S RdHi(4) RdLo(4) Rm(4) 1001 Rn(4) ]", mnemonic="SMLAL")
@ispec("32[ .cond(4) 0000110 S RdHi(4) RdLo(4) Rm(4) 1001 Rn(4) ]", mnemonic="SMULL")
@ispec("32[ .cond(4) 0000101 S RdHi(4) RdLo(4) Rm(4) 1001 Rn(4) ]", mnemonic="UMLAL")
@ispec("32[ .cond(4) 0000100 S RdHi(4) RdLo(4) Rm(4) 1001 Rn(4) ]", mnemonic="UMULL")
def A_default(obj,S,RdHi,RdLo,Rm,Rn):
  obj.setflags = (S==1)
  obj.dLo = env.regs[RdLo]
  obj.dHi = env.regs[RdHi]
  obj.m = env.regs[Rm]
  obj.n = env.regs[Rn]
  obj.operands = [obj.dLo,obj.dHi,obj.n,obj.m]
  if env.pc in obj.operands: raise InstructionError(obj)
  obj.type = type_data_processing

@ispec("32[ .cond(4) 00010100 RdHi(4) RdLo(4) Rm(4) 1000 Rn(4) ]", mnemonic="SMLALBB")
@ispec("32[ .cond(4) 00010100 RdHi(4) RdLo(4) Rm(4) 1010 Rn(4) ]", mnemonic="SMLALTB")
@ispec("32[ .cond(4) 00010100 RdHi(4) RdLo(4) Rm(4) 1100 Rn(4) ]", mnemonic="SMLALBT")
@ispec("32[ .cond(4) 00010100 RdHi(4) RdLo(4) Rm(4) 1110 Rn(4) ]", mnemonic="SMLALTT")
@ispec("32[ .cond(4) 01110100 RdHi(4) RdLo(4) Rm(4) 0001 Rn(4) ]", mnemonic="SMLALD" )
@ispec("32[ .cond(4) 01110100 RdHi(4) RdLo(4) Rm(4) 0011 Rn(4) ]", mnemonic="SMLALDX")
@ispec("32[ .cond(4) 01110100 RdHi(4) RdLo(4) Rm(4) 0101 Rn(4) ]", mnemonic="SMLSLD")
@ispec("32[ .cond(4) 01110100 RdHi(4) RdLo(4) Rm(4) 0111 Rn(4) ]", mnemonic="SMLSLDX")
@ispec("32[ .cond(4) 00000100 RdHi(4) RdLo(4) Rm(4) 1001 Rn(4) ]", mnemonic="UMAAL")
def A_default(obj,RdHi,RdLo,Rm,Rn):
  obj.dLo = env.regs[RdLo]
  obj.dHi = env.regs[RdHi]
  obj.m = env.regs[Rm]
  obj.n = env.regs[Rn]
  obj.operands = [obj.dLo,obj.dHi,obj.n,obj.m]
  if env.pc in obj.operands: raise InstructionError(obj)
  obj.type = type_data_processing

@ispec("32[ .cond(4) 01110101 Rd(4) 1111 Rm(4) 0001 Rn(4) ]", mnemonic="SMMUL")
@ispec("32[ .cond(4) 01110101 Rd(4) 1111 Rm(4) 0011 Rn(4) ]", mnemonic="SMMULR")
@ispec("32[ .cond(4) 01110000 Rd(4) 1111 Rm(4) 0001 Rn(4) ]", mnemonic="SMUAD")
@ispec("32[ .cond(4) 01110000 Rd(4) 1111 Rm(4) 0011 Rn(4) ]", mnemonic="SMUADX")
@ispec("32[ .cond(4) 01110000 Rd(4) 1111 Rm(4) 0101 Rn(4) ]", mnemonic="SMUSD")
@ispec("32[ .cond(4) 01110000 Rd(4) 1111 Rm(4) 0111 Rn(4) ]", mnemonic="SMUSDX")
@ispec("32[ .cond(4) 00010110 Rd(4) 1111 Rm(4) 1000 Rn(4) ]", mnemonic="SMULBB")
@ispec("32[ .cond(4) 00010110 Rd(4) 1111 Rm(4) 1010 Rn(4) ]", mnemonic="SMULTB")
@ispec("32[ .cond(4) 00010110 Rd(4) 1111 Rm(4) 1100 Rn(4) ]", mnemonic="SMULBT")
@ispec("32[ .cond(4) 00010110 Rd(4) 1111 Rm(4) 1110 Rn(4) ]", mnemonic="SMULTT")
@ispec("32[ .cond(4) 00010010 Rd(4) 0000 Rm(4) 1010 Rn(4) ]", mnemonic="SMULWB")
@ispec("32[ .cond(4) 00010010 Rd(4) 0000 Rm(4) 1110 Rn(4) ]", mnemonic="SMULWT")
@ispec("32[ .cond(4) 01111000 Rd(4) 1111 Rm(4) 0001 Rn(4) ]", mnemonic="USAD8")
def A_default(obj,Rd,Rm,Rn):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d,obj.n,obj.m]
  if env.pc in obj.operands: raise InstructionError(obj)
  obj.type = type_data_processing

@ispec("32[ .cond(4) 0110101 sat_imm(5) Rd(4) imm5(5) sh 01 Rn(4) ]", mnemonic="SSAT")
@ispec("32[ .cond(4) 0110111 sat_imm(5) Rd(4) imm5(5) sh 01 Rn(4) ]", mnemonic="USAT")
def A_sreg(obj,sat_imm,Rd,imm5,sh,Rn):
  obj.d = env.regs[Rd]
  obj.n = DecodeShift(sh<<1,env.regs[Rn],env.cst(imm5,5))
  obj.saturate_to = sat_imm+1
  obj.operands = [obj.d,obj.saturate_to,obj.n]
  if env.pc in obj.operands: raise InstructionError(obj)
  obj.type = type_data_processing

@ispec("32[ .cond(4) 01101010 sat_imm(4) Rd(4) 1111 0001 Rn(4) ]", mnemonic="SSAT16")
@ispec("32[ .cond(4) 01101110 sat_imm(4) Rd(4) 1111 0011 Rn(4) ]", mnemonic="USAT16")
def A_default(obj,sat_imm,Rd,Rn):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.saturate_to = sat_imm+1
  obj.operands = [obj.d,obj.saturate_to,obj.n]
  if env.pc in obj.operands: raise InstructionError(obj)
  obj.type = type_data_processing

@ispec("32[ .cond(4) 1111 imm24(24) ]", mnemonic="SVC")
def A_default(obj,imm24):
  obj.imm32 = env.cst(imm24,32)
  obj.operands = [obj.imm32]
  obj.type = type_cpu_state

@ispec("32[ .cond(4) 00010 0 00 Rn(4) Rt(4) 0000 1001 Rt2(4) ]", mnemonic="SWP")
@ispec("32[ .cond(4) 00010 1 00 Rn(4) Rt(4) 0000 1001 Rt2(4) ]", mnemonic="SWPB")
def A_default(obj,Rn,Rt,Rt2):
  obj.n  = env.regs[Rn]
  obj.t  = env.regs[Rt]
  obj.t2 = env.regs[Rt2]
  obj.operands = [obj.t,obj.t2,obj.n]
  if env.pc in obj.operands: raise InstructionError(obj)
  if (Rn==Rt) or (Rn==Rt2): raise InstructionError(obj)
  obj.type = type_data_processing

@ispec("32[ .cond(4) 01101000 Rn(4) Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="SXTAB16")
@ispec("32[ .cond(4) 01101010 Rn(4) Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="SXTAB")
@ispec("32[ .cond(4) 01101011 Rn(4) Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="SXTAH")
@ispec("32[ .cond(4) 01101100 Rn(4) Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="UXTAB16")
@ispec("32[ .cond(4) 01101110 Rn(4) Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="UXTAB")
@ispec("32[ .cond(4) 01101111 Rn(4) Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="UXTAH")
def A_default(obj,Rn,Rd,rotate,Rm):
  obj.n  = env.regs[Rn]
  obj.d  = env.regs[Rd]
  obj.m  = env.ror(env.regs[Rm],rotate*8)
  obj.operands = [obj.d,obj.n,obj.m]
  if env.pc in obj.operands: raise InstructionError(obj)
  obj.type = type_data_processing

@ispec("32[ .cond(4) 01101000 1111 Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="SXTB16")
@ispec("32[ .cond(4) 01101010 1111 Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="SXTB")
@ispec("32[ .cond(4) 01101011 1111 Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="SXTH")
@ispec("32[ .cond(4) 01101100 1111 Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="UXTB16")
@ispec("32[ .cond(4) 01101110 1111 Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="UXTB")
@ispec("32[ .cond(4) 01101111 1111 Rd(4) rotate(2) 00 0111 Rm(4) ]", mnemonic="UXTH")
def A_default(obj,Rd,rotate,Rm):
  obj.d  = env.regs[Rd]
  obj.m  = env.ror(env.regs[Rm],rotate*8)
  obj.operands = [obj.d,obj.m]
  if env.pc in obj.operands: raise InstructionError(obj)
  obj.type = type_data_processing

