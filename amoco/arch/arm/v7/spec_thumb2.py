# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.arch.core import *

from amoco.arch.arm.v7 import env
from .utils import *

#------------------------------------------------------
# amoco THUMB(1&2)  instruction specs:
#------------------------------------------------------

ISPECS = []

@ispec("32[ 11110 #i 0 0000 S Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="AND")
@ispec("32[ 11110 #i 0 0001 S Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="BIC")
@ispec("32[ 11110 #i 0 0010 S Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="ORR")
@ispec("32[ 11110 #i 0 0011 S Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="ORN")
@ispec("32[ 11110 #i 0 0100 S Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="EOR")
@ispec("32[ 11110 #i 0 1000 S Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="ADD")
@ispec("32[ 11110 #i 0 1010 S Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="ADC")
@ispec("32[ 11110 #i 0 1011 S Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="SBC")
@ispec("32[ 11110 #i 0 1101 S Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="SUB")
@ispec("32[ 11110 #i 0 1110 S Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="RSB")
def Tx_immediate(obj,i,S,Rn,imm3,Rd,imm8):
  obj.setflags = (S==1)
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  obj.imm32 = ThumbExpandImm(i+imm3+imm8)
  obj.operands = [obj.d,obj.n,obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11110 #i 1 0000 0 Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="ADD")
@ispec("32[ 11110 #i 1 0101 0 Rn(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="SUB")
def T4_ADD_i(obj,i,Rn,imm3,Rd,imm8):
  obj.setflags = False
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  obj.imm32 = ThumbExpandImm(i+imm3+imm8)
  obj.operands = [obj.d,obj.n,obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11101 01 0000 S Rn(4) 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) ]", mnemonic="AND")
@ispec("32[ 11101 01 0001 S Rn(4) 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) ]", mnemonic="BIC")
@ispec("32[ 11101 01 0010 S Rn(4) 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) ]", mnemonic="ORR")
@ispec("32[ 11101 01 0011 S Rn(4) 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) ]", mnemonic="ORN")
@ispec("32[ 11101 01 0100 S Rn(4) 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) ]", mnemonic="EOR")
@ispec("32[ 11101 01 1000 S Rn(4) 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) ]", mnemonic="ADD")
@ispec("32[ 11101 01 1010 S Rn(4) 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) ]", mnemonic="ADC")
@ispec("32[ 11101 01 1101 S Rn(4) 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) ]", mnemonic="SUB")
@ispec("32[ 11101 01 1110 S Rn(4) 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) ]", mnemonic="RSB")
@ispec("32[ 11101 01 1011 S Rn(4) 0 imm3(3) Rd(4) imm2(2) stype(2) Rm(4) ]", mnemonic="SBC")
def Tx_register(obj,S,Rn,imm3,Rd,imm2,stype,Rm):
  obj.setflags = (S==1)
  obj.n = env.regs[Rn]
  obj.d = env.regs[Rd]
  obj.m = DecodeShift(stype,env.regs[Rm],imm3<<2+imm2)
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ 11110 #i 10101 0 1111 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="ADR", add=False )
@ispec("32[ 11110 #i 10000 0 1111 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="ADR", add=True )
def T23_ADR(obj,i,imm3,Rd,imm8):
  obj.d = env.regs[Rd]
  obj.imm32 = ThumbExpandImm(i+imm3+imm8)
  obj.operands = [obj.d,obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11101 01 0010 S 1111 0 imm3(3) Rd(4) imm2(2) 10 Rm(4) ]", mnemonic="ASR")
@ispec("32[ 11101 01 0010 S 1111 0 imm3(3) Rd(4) imm2(2) 00 Rm(4) ]", mnemonic="LSL")
@ispec("32[ 11101 01 0010 S 1111 0 imm3(3) Rd(4) imm2(2) 01 Rm(4) ]", mnemonic="LSR")
@ispec("32[ 11101 01 0010 S 1111 0 imm3(3) Rd(4) imm2(2) 11 Rm(4) ]", mnemonic="ROR")
def T2_ASR_i(obj,S,imm3,Rd,imm2,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.imm5 = imm3<<2+imm2
  obj.operands = [obj.d,obj.n,obj.imm5]
  obj.type = type_data_processing

@ispec("32[ 11111 010 0 10 S Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="ASR")
@ispec("32[ 11111 010 0 00 S Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="LSL")
@ispec("32[ 11111 010 0 01 S Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="LSR")
@ispec("32[ 11111 010 0 11 S Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="ROR")
def T2_ASR_r(obj,S,Rn,Rd,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ 11110 #S .cond(4) #imm6(6) 1 0 #J1 0 #J2 #imm11(11) ]", mnemonic="B")
def T3_B(obj,S,imm6,J1,J2,imm11):
  v = int(S+J2+J1+imm6+imm11+'0',2)
  obj.imm32 = env.cst(v,21).signextend(32)
  obj.operands = [obj.imm32]
  obj.type = type_control_flow

@ispec("32[ 11110 S #imm10(10) 10 J1 1 J2 #imm11(11) ]", mnemonic="B")
@ispec("32[ 11110 S #imm10(10) 11 J1 1 J2 #imm11(11) ]", mnemonic="BL")
def T4_B(obj,S,imm10,J1,J2,imm11):
  I1, I2 = str(~(J1^S)), str(~(J2^S))
  v = int(S+I1+I2+imm10+imm11+'0',2)
  obj.imm32 = env.cst(v,25).signextend(32)
  obj.operands = [obj.imm32]
  obj.type = type_control_flow

@ispec("32[ 11110 0 11 011 0 1111 0 imm3(3) Rd(4) imm2(2) 0 msb(5) ]", mnemonic="BFC")
def T1_BFC(obj,imm3,Rd,imm2,msb):
  obj.d = env.regs[Rd]
  obj.msbit = msb
  obj.lsbit = imm3<<2+imm2
  obj.operands = [obj.d, obj.lsbit, obj.msbit-obj.lsbit+1]
  obj.type = type_data_processing

@ispec("32[ 11110 0 11 011 0 Rn(4) 0 imm3(3) Rd(4) imm2(2) 0 msb(5) ]", mnemonic="BFI")
def T1_BFI(obj,Rn,imm3,Rd,imm2,msb):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.msbit = msb
  obj.lsbit = imm3<<2+imm2
  obj.operands = [obj.d, obj.n, obj.lsbit, obj.msbit-obj.lsbit+1]
  obj.type = type_data_processing

@ispec("32[ 11110 S #imm10H(10) 11 J1 0 J2 #imm10L(10) 0 ]", mnemonic="BLX")
def T2_BLX(obj,S,imm10H,J1,J2,imm10L):
  I1, I2 = str(~(J1^S)), str(~(J2^S))
  v = int(S+I1+I2+imm10H+imm10L+'00',2)
  obj.imm32 = env.cst(v,25).signextend(32)
  obj.operands = [obj.imm32]
  obj.type = type_control_flow

@ispec("32[ 11110 0 1111 00 Rm(4) 10 0 0 1111 00000000 ]", mnemonic="BXJ")
def T1_BXJ(obj,Rm):
  obj.m = env.regs[Rm]
  obj.operands = [obj.m]
  obj.type = type_control_flow

@ispec("32[ 11110 0 111 01 1 1111 10 0 0 1111 0010 1111 ]", mnemonic="CLREX")
@ispec("32[ 11110 0 111 01 0 1111 10 0 0 0000 0000 0000 ]", mnemonic="NOP")
@ispec("32[ 11110 0 111 01 0 1111 10 0 0 0000 0000 0100 ]", mnemonic="SEV")
@ispec("32[ 11110 0 111 01 0 1111 10 0 0 0000 0000 0010 ]", mnemonic="WFE")
@ispec("32[ 11110 0 111 01 0 1111 10 0 0 0000 0000 0011 ]", mnemonic="WFI")
@ispec("32[ 11110 0 111 01 0 1111 10 0 0 0000 0000 0001 ]", mnemonic="YIELD")
def T1_CLREX_NOP(obj):
  obj.type = type_cpu_state

@ispec("32[ 11111 010 1 011 rm(4) 1111 Rd(4) 1 000 Rm(4) ]", mnemonic="CLZ")
@ispec("32[ 11111 010 1 001 rm(4) 1111 Rd(4) 1 010 Rm(4) ]", mnemonic="RBIT")
@ispec("32[ 11111 010 1 001 rm(4) 1111 Rd(4) 1 000 Rm(4) ]", mnemonic="REV")
@ispec("32[ 11111 010 1 001 rm(4) 1111 Rd(4) 1 001 Rm(4) ]", mnemonic="REV16")
@ispec("32[ 11111 010 1 001 rm(4) 1111 Rd(4) 1 011 Rm(4) ]", mnemonic="REVSH")
def T1_CLZ(obj,rm,Rd,Rm):
  assert rm==Rm
  obj.d = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d,obj.m]
  obj.type = type_data_processing

@ispec("32[ 11110 #i 0 1000 1 Rn(4) 0 #imm3(3) 1111 #imm8(8) ]", mnemonic="CMN")
@ispec("32[ 11110 #i 0 1101 1 Rn(4) 0 #imm3(3) 1111 #imm8(8) ]", mnemonic="CMP")
@ispec("32[ 11110 #i 0 0100 1 Rn(4) 0 #imm3(3) 1111 #imm8(8) ]", mnemonic="TEQ")
@ispec("32[ 11110 #i 0 0000 1 Rn(4) 0 #imm3(3) 1111 #imm8(8) ]", mnemonic="TST")
def T1_CMN_i(obj,i,Rn,imm3,imm8):
  obj.n = env.regs[Rn]
  obj.imm32 = ThumbExpandImm(i+imm3+imm8)
  obj.operands = [obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11101 01 1000 1 Rn(4) 0 #imm3(3) 1111 #imm2(2) stype(2) Rm(4) ]", mnemonic="CMN")
@ispec("32[ 11101 01 1101 1 Rn(4) 0 #imm3(3) 1111 #imm2(2) stype(2) Rm(4) ]", mnemonic="CMP")
@ispec("32[ 11101 01 0100 1 Rn(4) 0 #imm3(3) 1111 #imm2(2) stype(2) Rm(4) ]", mnemonic="TEQ")
@ispec("32[ 11101 01 0000 1 Rn(4) 0 #imm3(3) 1111 #imm2(2) stype(2) Rm(4) ]", mnemonic="TST")
def T2_CMN_r(obj,i,Rn,imm3,imm2,stype,Rm):
  obj.n = env.regs[Rn]
  obj.m = DecodeShift(stype,env.regs[Rm],imm3<<2+imm2)
  obj.operands = [obj.n, obj.m]
  obj.type = type_data_processing

@ispec("32[ 11110 0 111 01 0 1111 10 000 000 1111 .option(4) ]", mnemonic="DBG")
@ispec("32[ 11110 0 111 01 1 1111 10 00 1111 0101 .option(4) ]", mnemonic="DMB")
@ispec("32[ 11110 0 111 01 1 1111 10 00 1111 0100 .option(4) ]", mnemonic="DSB")
@ispec("32[ 11110 0 111 01 1 1111 10 00 1111 0110 .option(4) ]", mnemonic="ISB")
def T1_Dxx(obj):
  obj.type = type_cpu_state

@ispec("32[ 11101 00 010 W 1 Rn(4) #P #M 0 #register_list(13) ]", mnemonic="LDM")
@ispec("32[ 11101 00 100 W 1 Rn(4) #P #M 0 #register_list(13) ]", mnemonic="LDMDB")
def T2_LDM(obj,W,Rn,P,M,register_list):
  obj.n = env.regs[Rn]
  obj.registers = [env.regs[i] for i,r in enumerate(register_list[::-1]+'0'+M+P) if r=='1']
  obj.wback = (W==1)
  obj.operands = [obj.n, obj.registers]
  obj.type = type_data_processing

@ispec("32[ 11101 00 010 W 0 Rn(4) 0  #M 0 #register_list(13) ]", mnemonic="STM")
@ispec("32[ 11101 00 100 W 0 Rn(4) 0  #M 0 #register_list(13) ]", mnemonic="STMDB")
def T2_STM(obj,W,Rn,M,register_list):
  obj.n = env.regs[Rn]
  obj.registers = [env.regs[i] for i,r in enumerate(register_list[::-1]+'0'+M) if r=='1']
  obj.wback = (W==1)
  obj.operands = [obj.n, obj.registers]
  obj.type = type_data_processing

@ispec("32[ 11111 00 0 1 10 1 Rn(4) Rt(4) imm12(12) ]", mnemonic="LDR")
@ispec("32[ 11111 00 0 1 00 1 Rn(4) Rt(4) imm12(12) ]", mnemonic="LDRB")
@ispec("32[ 11111 00 0 1 01 1 Rn(4) Rt(4) imm12(12) ]", mnemonic="LDRH")
@ispec("32[ 11111 00 1 1 00 1 Rn(4) Rt(4) imm12(12) ]", mnemonic="LDRSB")
@ispec("32[ 11111 00 1 1 01 1 Rn(4) Rt(4) imm12(12) ]", mnemonic="LDRSH")
@ispec("32[ 11111 00 0 1 10 0 Rn(4) Rt(4) imm12(12) ]", mnemonic="STR")
@ispec("32[ 11111 00 0 1 00 0 Rn(4) Rt(4) imm12(12) ]", mnemonic="STRB")
@ispec("32[ 11111 00 0 1 01 0 Rn(4) Rt(4) imm12(12) ]", mnemonic="STRH")
def T3_LDR(obj,Rn,Rt,imm12):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.imm32 = env.cst(imm12,32)
  obj.index = True
  obj.add = True
  obj.wback = False
  obj.operands = [obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11111 00 0 0 10 1 Rn(4) Rt(4) 1 P U W imm8(8) ]", mnemonic="LDR")
@ispec("32[ 11111 00 0 0 00 1 Rn(4) Rt(4) 1 P U W imm8(8) ]", mnemonic="LDRB")
@ispec("32[ 11111 00 0 0 01 1 Rn(4) Rt(4) 1 P U W imm8(8) ]", mnemonic="LDRH")
@ispec("32[ 11111 00 1 0 00 1 Rn(4) Rt(4) 1 P U W imm8(8) ]", mnemonic="LDRSB")
@ispec("32[ 11111 00 1 0 01 1 Rn(4) Rt(4) 1 P U W imm8(8) ]", mnemonic="LDRSH")
@ispec("32[ 11111 00 0 0 10 0 Rn(4) Rt(4) 1 P U W imm8(8) ]", mnemonic="STR")
@ispec("32[ 11111 00 0 0 00 0 Rn(4) Rt(4) 1 P U W imm8(8) ]", mnemonic="STRB")
@ispec("32[ 11111 00 0 0 01 0 Rn(4) Rt(4) 1 P U W imm8(8) ]", mnemonic="STRH")
def T4_LDR(obj,Rn,Rt,P,U,W,imm8):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.imm32 = env.cst(imm8,32)
  if P==1 and U==1 and W==0:
      obj.mnemonic += 'T'
      obj.postindex = False
      obj.register_form = False
  else:
      obj.index = (P==1)
      obj.wback = (W==1)
  obj.add = (U==1)
  obj.operands = [obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11111 00 0 U 10 1 1111 Rt(4) imm12(12) ]", mnemonic="LDR")
@ispec("32[ 11111 00 0 U 00 1 1111 Rt(4) imm12(12) ]", mnemonic="LDRB")
@ispec("32[ 11111 00 0 U 01 1 1111 Rt(4) imm12(12) ]", mnemonic="LDRH")
@ispec("32[ 11111 00 1 U 00 1 1111 Rt(4) imm12(12) ]", mnemonic="LDRSB")
@ispec("32[ 11111 00 1 U 01 1 1111 Rt(4) imm12(12) ]", mnemonic="LDRSH")
def T2_LDR_literal(obj,U,Rt,imm12):
  obj.n = env.pc
  obj.t = env.regs[Rt]
  obj.imm32 = env.cst(imm12,32)
  obj.add = (U==1)
  obj.operands = [obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11111 00 0 0 10 1 Rn(4) Rt(4) 0 00000 imm2(2) Rm(4) ]", mnemonic="LDR")
@ispec("32[ 11111 00 0 0 00 1 Rn(4) Rt(4) 0 00000 imm2(2) Rm(4) ]", mnemonic="LDRB")
@ispec("32[ 11111 00 0 0 01 1 Rn(4) Rt(4) 0 00000 imm2(2) Rm(4) ]", mnemonic="LDRH")
@ispec("32[ 11111 00 1 0 00 1 Rn(4) Rt(4) 0 00000 imm2(2) Rm(4) ]", mnemonic="LDRSB")
@ispec("32[ 11111 00 1 0 01 1 Rn(4) Rt(4) 0 00000 imm2(2) Rm(4) ]", mnemonic="LDRSH")
@ispec("32[ 11111 00 0 0 10 0 Rn(4) Rt(4) 0 00000 imm2(2) Rm(4) ]", mnemonic="STR")
@ispec("32[ 11111 00 0 0 00 0 Rn(4) Rt(4) 0 00000 imm2(2) Rm(4) ]", mnemonic="STRB")
@ispec("32[ 11111 00 0 0 01 0 Rn(4) Rt(4) 0 00000 imm2(2) Rm(4) ]", mnemonic="STRH")
def T2_LDR_r(obj,Rn,Rt,imm2,Rm):
  obj.n = env.regs[Rn]
  obj.t = env.regs[Rt]
  obj.m = env.regs[Rm]<<imm2
  obj.index = True
  obj.add = True
  obj.wback = False
  obj.operands = [obj.t, obj.n, obj.m]
  obj.type = type_data_processing

@ispec("32[ 11101 00 P U 1 W 1 Rn(4) Rt(4) Rt2(4) imm8(8) ]", mnemonic="LDRD")
@ispec("32[ 11101 00 P U 1 W 0 Rn(4) Rt(4) Rt2(4) imm8(8) ]", mnemonic="STRD")
def T1_LDRD_i(obj,P,U,W,Rn,Rt,Rt2,imm8):
  obj.t = env.regs[Rt]
  obj.t2 = env.regs[Rt2]
  obj.n = env.regs[Rn]
  obj.imm32 = env.cst(imm8<<2,32)
  obj.index = (P==1)
  obj.wback = (W==1)
  obj.add = (U==1)
  obj.operands = [obj.t, obj.t2, obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11101 00 0 0 1 0 1 Rn(4) Rt(4) 1111 imm8(8) ]", mnemonic="LDREX")
def T1_LDREX(obj,Rn,Rt,imm8):
  obj.t = env.regs[Rt]
  obj.n = env.regs[Rn]
  obj.imm32 = env.cst(imm8<<2,32)
  obj.operands = [obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11101 00 0 0 1 0 0 Rn(4) Rt(4) Rd(4) imm8(8) ]", mnemonic="STREX")
def T1_STREX(obj,Rn,Rt,Rd,imm8):
  obj.d = env.regs[Rd]
  obj.t = env.regs[Rt]
  obj.n = env.regs[Rn]
  obj.imm32 = env.cst(imm8<<2,32)
  obj.operands = [obj.d, obj.t, obj.n, obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11101 0001101 Rn(4) Rt(4) 1111 0100 1111 ]", mnemonic="LDREXB")
@ispec("32[ 11101 0001101 Rn(4) Rt(4) 1111 0101 1111 ]", mnemonic="LDREXH")
def T1_LDREXB(obj,Rn,Rt):
  obj.t = env.regs[Rt]
  obj.n = env.regs[Rn]
  obj.operands = [obj.t, obj.n]
  obj.type = type_data_processing

@ispec("32[ 11101 0001100 Rn(4) Rt(4) 1111 0100 Rd(4) ]", mnemonic="STREXB")
@ispec("32[ 11101 0001100 Rn(4) Rt(4) 1111 0101 Rd(4) ]", mnemonic="STREXH")
def T1_STREXB(obj,Rn,Rt,Rd):
  obj.d = env.regs[Rd]
  obj.t = env.regs[Rt]
  obj.n = env.regs[Rn]
  obj.operands = [obj.d, obj.t, obj.n]
  obj.type = type_data_processing

@ispec("32[ 11101 000110 1 Rn(4) Rt(4) Rt2(4) 0111 1111 ]", mnemonic="LDREXD")
def T1_LDREXD(obj,Rn,Rt,Rt2):
  obj.t = env.regs[Rt]
  obj.t2 = env.regs[Rt2]
  obj.n = env.regs[Rn]
  obj.operands = [obj.t, obj.t2, obj.n]
  obj.type = type_data_processing

@ispec("32[ 11101 000110 0 Rn(4) Rt(4) Rt2(4) 0111 Rd(4) ]", mnemonic="STREXD")
def T1_STREXD(obj,Rn,Rt,Rt2,Rd):
  obj.d = env.regs[Rd]
  obj.t = env.regs[Rt]
  obj.t2 = env.regs[Rt2]
  obj.n = env.regs[Rn]
  obj.operands = [obj.d, obj.t, obj.t2, obj.n]
  obj.type = type_data_processing

@ispec("32[ 11111 0110 000 Rn(4) Ra(4) Rd(4) 0000 Rm(4) ]", mnemonic="MLA", setflags=False)
@ispec("32[ 11111 0110 000 Rn(4) Ra(4) Rd(4) 0001 Rm(4) ]", mnemonic="MLS")
def T1_MLA(obj,Rn,Ra,Rd,Rm):
  obj.n = env.regs[Rn]
  obj.a = env.regs[Ra]
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d, obj.n, obj.m, obj.a]
  obj.type = type_data_processing

@ispec("32[ 11110 #i 0 0010 S 1111 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="MOV")
@ispec("32[ 11110 #i 0 0011 S 1111 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="MVN")
def T2_MOV_i(obj,i,S,imm3,Rd,imm8):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.imm32 = ThumbExpandImm(i+imm3+imm8)
  obj.operands = [obj.d, obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11110 #i 10 0 1 0 0 #imm4(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="MOV")
def T3_MOV_i(obj,i,imm4,imm3,Rd,imm8):
  obj.setflags = False
  obj.d = env.regs[Rd]
  obj.imm32 = env.cst(int(imm4+i+imm3+imm8,2),32)
  obj.operands = [obj.d, obj.imm32]
  obj.type = type_data_processing

@ispec("32[ 11101 01 0010 S 1111 0 000 Rd(4) 0000 Rm(4) ]", mnemonic="MOV")
@ispec("32[ 11101 01 0010 S 1111 0 000 Rd(4) 0011 Rm(4) ]", mnemonic="RRX")
def T3_MOV_r(obj,S,Rd,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d, obj.m]
  obj.type = type_data_processing

@ispec("32[ 11110 #i 10 1 1 0 0 #imm4(4) 0 #imm3(3) Rd(4) #imm8(8) ]", mnemonic="MOVT")
def T1_MOVT(obj,i,imm4,imm3,Rd,imm8):
  obj.d = env.regs[Rd]
  obj.imm16 = env.cst(int(imm4+i+imm3+imm8,2),16)
  obj.operands = [obj.d, obj.imm16]
  obj.type = type_data_processing

@ispec("32[ 11110 0 1111 1 0 1111 10 0 0 Rd(4) 00000000 ]", mnemonic="MRS")
def T1_MRS(obj,Rd):
  obj.d = env.regs[Rd]
  obj.operands = [obj.d]
  obj.type = type_data_processing

@ispec("32[ 11110 0 1110 0 0 Rn(4) 10 0 0 mask(2) 00 00000000 ]", mnemonic="MSR")
def T1_MSR_r(obj,Rn,mask):
  obj.n = env.regs[Rn]
  obj.write_nzcvq = (mask&2)==2
  obj.write_g = (mask&1)==1
  obj.operands = [obj.n]
  obj.type = type_data_processing

@ispec("32[ 11111 0110 000 Rn(4) 1111 Rd(4) 0000 Rm(4) ]", mnemonic="MUL")
def T2_MUL(obj,Rn,Rd,Rm):
  obj.setflags = False
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ 11101 01 0011 S 1111 0 #imm3(3) Rd(4) #imm2(2) stype(2) Rm(4) ]", mnemonic="MVN")
def T2_MVN_r(obj,S,imm3,Rd,imm2,stype,Rm):
  obj.setflags = (S==1)
  obj.d = env.regs[Rd]
  obj.m = DecodeShift(stype,env.regs[Rm],imm3<<2+imm2)
  obj.operands = [obj.d,obj.m]
  obj.type = type_data_processing

@ispec("32[ 11101 01 0110 0 Rn(4) 0 #imm3(3) Rd(4) #imm2(2) tb 0 Rm(4) ]", mnemonic="PKH")
def T1_PKH(obj,Rn,imm3,Rd,imm2,tb,Rm):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = DecodeShift(tb<<1,env.regs[Rm],imm3<<2+imm2)
  obj.tbform = (tb==1)
  obj.operands = [obj.d, obj.n, obj.m]
  obj.type = type_data_processing

@ispec("32[ 11111 00 0 1 0 0 1 Rn(4) 1111 imm(12) ]", mnemonic="PLD", add=True)
@ispec("32[ 11111 00 0 1 0 1 1 Rn(4) 1111 imm(12) ]", mnemonic="PLDW", add=True)
@ispec("32[ 11111 00 0 0 0 0 1 Rn(4) 1111 1100 imm(8) ]", mnemonic="PLD", add=False)
@ispec("32[ 11111 00 0 0 0 1 1 Rn(4) 1111 1100 imm(8) ]", mnemonic="PLDW", add=False)
@ispec("32[ 11111 00 1 1 0 0 1 Rn(4) 1111 imm(12) ]", mnemonic="PLI", add=True)
@ispec("32[ 11111 00 1 1 0 1 1 Rn(4) 1111 imm(12) ]", mnemonic="PLIW", add=True)
@ispec("32[ 11111 00 1 0 0 0 1 Rn(4) 1111 1100 imm(8) ]", mnemonic="PLI", add=False)
@ispec("32[ 11111 00 1 0 0 1 1 Rn(4) 1111 1100 imm(8) ]", mnemonic="PLIW", add=False)
def T12_PLDw(obj,Rn,imm):
  obj.n = env.regs[Rn]
  obj.imm32 = env.cst(imm,32)
  obj.operands = [obj.n, obj.imm32]
  obj.type = type_cpu_state

@ispec("32[ 11111 00 0 U 00 1 1111 1111 imm12(12) ]", mnemonic="PLD")
@ispec("32[ 11111 00 1 U 00 1 1111 1111 imm12(12) ]", mnemonic="PLI")
def T1_PLD_literal(obj,U,Rt,imm12):
  obj.n = env.pc
  obj.add = (U==1)
  obj.imm32 = env.cst(imm12,32)
  obj.operands = [obj.n, obj.imm32]
  obj.type = type_cpu_state

@ispec("32[ 11111 00 0 0 00 1 Rn(4) 1111 0 00000 imm2(2) Rm(4) ]", mnemonic="PLD", add=True)
@ispec("32[ 11111 00 0 0 01 1 Rn(4) 1111 0 00000 imm2(2) Rm(4) ]", mnemonic="PLDW", add=True)
@ispec("32[ 11111 00 1 0 00 1 Rn(4) 1111 0 00000 imm2(2) Rm(4) ]", mnemonic="PLI", add=True)
@ispec("32[ 11111 00 1 0 01 1 Rn(4) 1111 0 00000 imm2(2) Rm(4) ]", mnemonic="PLIW", add=True)
def T1_PLD_r(obj,W,Rn,imm2,Rm):
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]<<imm2
  obj.operands = [obj.n,obj.m]
  obj.type = type_cpu_state

@ispec("32[ 11101 00 010 1 1 1101 #P #M 0 #register_list(13) ]", mnemonic="POP")
def T2_POP(obj,P,M,register_list):
  obj.registers = [env.regs[i] for i,r in enumerate(register_list[::-1]+'0'+M+P) if r=='1']
  obj.operands = [obj.registers]
  obj.type = type_data_processing

@ispec("32[ 11111 00 0 0 10 1 1101 Rt(4) 1 011 00000000 ]", mnemonic="POP")
def T3_POP(obj,Rt):
  obj.registers = [env.regs[Rt]]
  obj.operands = [obj.registers]
  obj.type = type_data_processing

@ispec("32[ 11101 00 100 1 0 1101 0 #M 0 #register_list(13) ]", mnemonic="PUSH")
def T2_PUSH(obj,P,M,register_list):
  obj.registers = [env.regs[i] for i,r in enumerate(register_list[::-1]+'0'+M+'0') if r=='1']
  obj.operands = [obj.registers]
  obj.type = type_data_processing

@ispec("32[ 11111 00 0 0 10 0 1101 Rt(4) 1 101 00000000 ]", mnemonic="PUSH")
def T3_PUSH(obj,Rt):
  obj.registers = [env.regs[Rt]]
  obj.operands = [obj.registers]
  obj.type = type_data_processing

@ispec("32[ 11111 010 1 000 Rn(4) 1111 Rd(4) 1 000 Rm(4) ]", mnemonic="QADD")
@ispec("32[ 11111 010 1 000 Rn(4) 1111 Rd(4) 1 001 Rm(4) ]", mnemonic="QDADD")
@ispec("32[ 11111 010 1 000 Rn(4) 1111 Rd(4) 1 011 Rm(4) ]", mnemonic="QDSUB")
@ispec("32[ 11111 010 1 000 Rn(4) 1111 Rd(4) 1 010 Rm(4) ]", mnemonic="QSUB")
def T1_QADD(obj,S,Rn,Rd,Rm):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d,obj.m,obj.n]
  obj.type = type_data_processing

@ispec("32[ 11111 010 1 001 Rn(4) 1111 Rd(4) 0 001 Rm(4) ]", mnemonic="QADD16")
@ispec("32[ 11111 010 1 000 Rn(4) 1111 Rd(4) 0 001 Rm(4) ]", mnemonic="QADD8")
@ispec("32[ 11111 010 1 010 Rn(4) 1111 Rd(4) 0 001 Rm(4) ]", mnemonic="QASX")
@ispec("32[ 11111 010 1 110 Rn(4) 1111 Rd(4) 0 001 Rm(4) ]", mnemonic="QSAX")
@ispec("32[ 11111 010 1 101 Rn(4) 1111 Rd(4) 0 001 Rm(4) ]", mnemonic="QSUB16")
@ispec("32[ 11111 010 1 100 Rn(4) 1111 Rd(4) 0 001 Rm(4) ]", mnemonic="QSUB8")
@ispec("32[ 11111 010 1 001 Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="SADD16")
@ispec("32[ 11111 010 1 000 Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="SADD8")
@ispec("32[ 11111 010 1 010 Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="SASX")
@ispec("32[ 11111 010 1 110 Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="SSAX")
@ispec("32[ 11111 010 1 101 Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="SSUB16")
@ispec("32[ 11111 010 1 100 Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="SSUB8")
@ispec("32[ 11111 010 1 001 Rn(4) 1111 Rd(4) 0 010 Rm(4) ]", mnemonic="SHADD16")
@ispec("32[ 11111 010 1 000 Rn(4) 1111 Rd(4) 0 010 Rm(4) ]", mnemonic="SHADD8")
@ispec("32[ 11111 010 1 010 Rn(4) 1111 Rd(4) 0 010 Rm(4) ]", mnemonic="SHASX")
@ispec("32[ 11111 010 1 110 Rn(4) 1111 Rd(4) 0 010 Rm(4) ]", mnemonic="SHSAX")
@ispec("32[ 11111 010 1 101 Rn(4) 1111 Rd(4) 0 010 Rm(4) ]", mnemonic="SHSUB16")
@ispec("32[ 11111 010 1 100 Rn(4) 1111 Rd(4) 0 010 Rm(4) ]", mnemonic="SHSUB8")
@ispec("32[ 11111 010 1 010 Rn(4) 1111 Rd(4) 1 000 Rm(4) ]", mnemonic="SEL")
@ispec("32[ 11111 011 0 101 Rn(4) 1111 Rd(4) 1 000 Rm(4) ]", mnemonic="SMMUL")
@ispec("32[ 11111 011 0 101 Rn(4) 1111 Rd(4) 1 001 Rm(4) ]", mnemonic="SMMULR")
@ispec("32[ 11111 011 0 010 Rn(4) 1111 Rd(4) 1 000 Rm(4) ]", mnemonic="SMUAD")
@ispec("32[ 11111 011 0 010 Rn(4) 1111 Rd(4) 1 001 Rm(4) ]", mnemonic="SMUADX")
@ispec("32[ 11111 011 0 001 Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="SMULBB")
@ispec("32[ 11111 011 0 001 Rn(4) 1111 Rd(4) 0 010 Rm(4) ]", mnemonic="SMULTB")
@ispec("32[ 11111 011 0 001 Rn(4) 1111 Rd(4) 0 001 Rm(4) ]", mnemonic="SMULBT")
@ispec("32[ 11111 011 0 001 Rn(4) 1111 Rd(4) 0 011 Rm(4) ]", mnemonic="SMULTT")
@ispec("32[ 11111 011 0 011 Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="SMULWB")
@ispec("32[ 11111 011 0 011 Rn(4) 1111 Rd(4) 0 001 Rm(4) ]", mnemonic="SMULWT")
@ispec("32[ 11111 011 0 100 Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="SMUSD")
@ispec("32[ 11111 011 0 100 Rn(4) 1111 Rd(4) 0 001 Rm(4) ]", mnemonic="SMUSDX")
@ispec("32[ 11111 010 1 001 Rn(4) 1111 Rd(4) 0 100 Rm(4) ]", mnemonic="UADD16")
@ispec("32[ 11111 010 1 000 Rn(4) 1111 Rd(4) 0 100 Rm(4) ]", mnemonic="UADD8")
@ispec("32[ 11111 010 1 010 Rn(4) 1111 Rd(4) 0 100 Rm(4) ]", mnemonic="UASX")
@ispec("32[ 11111 010 1 110 Rn(4) 1111 Rd(4) 0 100 Rm(4) ]", mnemonic="USAX")
@ispec("32[ 11111 010 1 101 Rn(4) 1111 Rd(4) 0 100 Rm(4) ]", mnemonic="USUB16")
@ispec("32[ 11111 010 1 100 Rn(4) 1111 Rd(4) 0 100 Rm(4) ]", mnemonic="USUB8")
@ispec("32[ 11111 010 1 001 Rn(4) 1111 Rd(4) 0 110 Rm(4) ]", mnemonic="UHADD16")
@ispec("32[ 11111 010 1 000 Rn(4) 1111 Rd(4) 0 110 Rm(4) ]", mnemonic="UHADD8")
@ispec("32[ 11111 010 1 010 Rn(4) 1111 Rd(4) 0 110 Rm(4) ]", mnemonic="UHASX")
@ispec("32[ 11111 010 1 110 Rn(4) 1111 Rd(4) 0 110 Rm(4) ]", mnemonic="UHSAX")
@ispec("32[ 11111 010 1 101 Rn(4) 1111 Rd(4) 0 110 Rm(4) ]", mnemonic="UHSUB16")
@ispec("32[ 11111 010 1 100 Rn(4) 1111 Rd(4) 0 110 Rm(4) ]", mnemonic="UHSUB8")
@ispec("32[ 11111 010 1 001 Rn(4) 1111 Rd(4) 0 101 Rm(4) ]", mnemonic="UQADD16")
@ispec("32[ 11111 010 1 000 Rn(4) 1111 Rd(4) 0 101 Rm(4) ]", mnemonic="UQADD8")
@ispec("32[ 11111 010 1 010 Rn(4) 1111 Rd(4) 0 101 Rm(4) ]", mnemonic="UQASX")
@ispec("32[ 11111 010 1 110 Rn(4) 1111 Rd(4) 0 101 Rm(4) ]", mnemonic="UQSAX")
@ispec("32[ 11111 010 1 101 Rn(4) 1111 Rd(4) 0 101 Rm(4) ]", mnemonic="UQSUB16")
@ispec("32[ 11111 010 1 100 Rn(4) 1111 Rd(4) 0 101 Rm(4) ]", mnemonic="UQSUB8")
@ispec("32[ 11111 011 0 111 Rn(4) 1111 Rd(4) 0 000 Rm(4) ]", mnemonic="USAD8")
@ispec("32[ 11111 011 1 001 Rn(4) 1111 Rd(4) 1 111 Rm(4) ]", mnemonic="SDIV")
@ispec("32[ 11111 011 1 011 Rn(4) 1111 Rd(4) 1 111 Rm(4) ]", mnemonic="UDIV")
def T1_QADD(obj,Rn,Rd,Rm):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.operands = [obj.d,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ 11110 0 11 010 0 Rn(4) 0 imm3(3) Rd(4) imm2(2) 0 widthm1(5) ]", mnemonic="SBFX")
@ispec("32[ 11110 0 11 110 0 Rn(4) 0 imm3(3) Rd(4) imm2(2) 0 widthm1(5) ]", mnemonic="UBFX")
def T1_SBFX(obj,Rn,imm3,Rd,imm2,widthm1):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.lsbit = imm3<<2+imm2
  obj.widthminus1 = widthm1
  obj.operands = [obj.d,obj.n,obj.lsb,obj.widthminus1+1]
  obj.type = type_data_processing

@ispec("32[ 11111 0110 001 Rn(4) Ra(4) Rd(4) 0000 Rm(4) ]", mnemonic="SMLABB")
@ispec("32[ 11111 0110 001 Rn(4) Ra(4) Rd(4) 0010 Rm(4) ]", mnemonic="SMLATB")
@ispec("32[ 11111 0110 001 Rn(4) Ra(4) Rd(4) 0001 Rm(4) ]", mnemonic="SMLABT")
@ispec("32[ 11111 0110 001 Rn(4) Ra(4) Rd(4) 0011 Rm(4) ]", mnemonic="SMLATT")
@ispec("32[ 11111 0110 010 Rn(4) Ra(4) Rd(4) 0000 Rm(4) ]", mnemonic="SMLAD")
@ispec("32[ 11111 0110 010 Rn(4) Ra(4) Rd(4) 0001 Rm(4) ]", mnemonic="SMLADX")
@ispec("32[ 11111 0110 011 Rn(4) Ra(4) Rd(4) 0000 Rm(4) ]", mnemonic="SMLAWB")
@ispec("32[ 11111 0110 011 Rn(4) Ra(4) Rd(4) 0001 Rm(4) ]", mnemonic="SMLAWT")
@ispec("32[ 11111 0110 100 Rn(4) Ra(4) Rd(4) 0000 Rm(4) ]", mnemonic="SMLSD")
@ispec("32[ 11111 0110 100 Rn(4) Ra(4) Rd(4) 0001 Rm(4) ]", mnemonic="SMLSDX")
@ispec("32[ 11111 0110 101 Rn(4) Ra(4) Rd(4) 0000 Rm(4) ]", mnemonic="SMMLA")
@ispec("32[ 11111 0110 101 Rn(4) Ra(4) Rd(4) 0001 Rm(4) ]", mnemonic="SMMLAR")
@ispec("32[ 11111 0110 110 Rn(4) Ra(4) Rd(4) 0000 Rm(4) ]", mnemonic="SMMLS")
@ispec("32[ 11111 0110 110 Rn(4) Ra(4) Rd(4) 0001 Rm(4) ]", mnemonic="SMMLSR")
@ispec("32[ 11111 0110 111 Rn(4) Ra(4) Rd(4) 0000 Rm(4) ]", mnemonic="USADA8")
def T1_SMLAxy(obj,Rd,Ra,Rm,Rn):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.a = env.regs[Ra]
  obj.operands = [obj.d,obj.n,obj.m,obj.a]
  obj.type = type_data_processing

@ispec("32[ 11111 0111 1 00 Rn(4) RdLo(4) RdHi(4) 0000 Rm(4) ]", mnemonic="SMLAL")
@ispec("32[ 11111 0111 0 00 Rn(4) RdLo(4) RdHi(4) 0000 Rm(4) ]", mnemonic="SMULL")
@ispec("32[ 11111 0111 1 10 Rn(4) RdLo(4) RdHi(4) 0000 Rm(4) ]", mnemonic="UMLAL")
@ispec("32[ 11111 0111 0 10 Rn(4) RdLo(4) RdHi(4) 0000 Rm(4) ]", mnemonic="UMULL")
@ispec("32[ 11111 0111 1 00 Rn(4) RdLo(4) RdHi(4) 1000 Rm(4) ]", mnemonic="SMLALBB")
@ispec("32[ 11111 0111 1 00 Rn(4) RdLo(4) RdHi(4) 1010 Rm(4) ]", mnemonic="SMLALTB")
@ispec("32[ 11111 0111 1 00 Rn(4) RdLo(4) RdHi(4) 1001 Rm(4) ]", mnemonic="SMLALBT")
@ispec("32[ 11111 0111 1 00 Rn(4) RdLo(4) RdHi(4) 1011 Rm(4) ]", mnemonic="SMLALTT")
@ispec("32[ 11111 0111 1 00 Rn(4) RdLo(4) RdHi(4) 1100 Rm(4) ]", mnemonic="SMLALD")
@ispec("32[ 11111 0111 1 00 Rn(4) RdLo(4) RdHi(4) 1101 Rm(4) ]", mnemonic="SMLALDX")
@ispec("32[ 11111 0111 1 01 Rn(4) RdLo(4) RdHi(4) 1100 Rm(4) ]", mnemonic="SMLSLD")
@ispec("32[ 11111 0111 1 01 Rn(4) RdLo(4) RdHi(4) 1101 Rm(4) ]", mnemonic="SMLSLDX")
@ispec("32[ 11111 0111 1 10 Rn(4) RdLo(4) RdHi(4) 0110 Rm(4) ]", mnemonic="UMAAL")
def T1_SMLALxx(obj,Rn,RdLo,RdHi,Rm):
  obj.setflags = False
  obj.dLo = env.regs[RdLo]
  obj.dHi = env.regs[RdHi]
  obj.m = env.regs[Rm]
  obj.n = env.regs[Rn]
  obj.operands = [obj.dLo,obj.dHi,obj.n,obj.m]
  obj.type = type_data_processing

@ispec("32[ 11110 0 11 00 sh 0 Rn(4) 0 imm3(3) Rd(4) imm2(2) 0 sat_imm(5) ]", mnemonic="SSAT")
@ispec("32[ 11110 0 11 10 sh 0 Rn(4) 0 imm3(3) Rd(4) imm2(2) 0 sat_imm(5) ]", mnemonic="USAT")
def T1_SSAT(obj,sh,Rn,imm3,Rd,imm2,sat_imm):
  obj.d = env.regs[Rd]
  obj.n = DecodeShift(sh<<1,env.regs[Rn],imm3<<2+imm2)
  obj.saturate_to = sat_imm+1
  obj.operands = [obj.d,obj.saturate_to,obj.n]
  obj.type = type_data_processing

@ispec("32[ 11110 0 11 00 1 0 Rn(4) 0000 Rd(4) 00 00 sat_imm(4) ]", mnemonic="SSAT16")
@ispec("32[ 11110 0 11 10 1 0 Rn(4) 0000 Rd(4) 00 00 sat_imm(4) ]", mnemonic="USAT16")
def T1_SSAT16(obj,Rn,Rd,sat_imm):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.saturate_to = sat_imm+1
  obj.operands = [obj.d,obj.saturate_to,obj.n]
  obj.type = type_data_processing

@ispec("32[ 11111 010 0 100 Rn(4) 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="SXTAB")
@ispec("32[ 11111 010 0 010 Rn(4) 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="SXTAB16")
@ispec("32[ 11111 010 0 000 Rn(4) 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="SXTAH")
@ispec("32[ 11111 010 0 101 Rn(4) 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="UXTAB")
@ispec("32[ 11111 010 0 011 Rn(4) 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="UXTAB16")
@ispec("32[ 11111 010 0 001 Rn(4) 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="UXTAH")
def T1_SXTAB(obj,Rn,Rd,rotate,Rm):
  obj.d = env.regs[Rd]
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.rotation = rotate<<3
  obj.operands = [obj.d,obj.n,obj.m,obj.rotation]
  obj.type = type_data_processing

@ispec("32[ 11111 010 0 100 1111 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="SXTB")
@ispec("32[ 11111 010 0 010 1111 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="SXTB16")
@ispec("32[ 11111 010 0 000 1111 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="SXTH")
@ispec("32[ 11111 010 0 101 1111 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="UXTB")
@ispec("32[ 11111 010 0 011 1111 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="UXTB16")
@ispec("32[ 11111 010 0 001 1111 1111 Rd(4) 1 0 rotate(2) Rm(4) ]", mnemonic="UXTH")
def T2_SXTB(obj,Rd,rotate,Rm):
  obj.d = env.regs[Rd]
  obj.m = env.regs[Rm]
  obj.rotation = rotate<<3
  obj.operands = [obj.d,obj.m,obj.rotation]
  obj.type = type_data_processing

@ispec("32[ 11101 00 0 1 1 0 1 Rn(4) 1111 0000 000 0 Rm(4) ]", mnemonic="TBB", is_tbh=False)
@ispec("32[ 11101 00 0 1 1 0 1 Rn(4) 1111 0000 000 1 Rm(4) ]", mnemonic="TBH", is_tbh=True)
def T1_TBB(obj,Rn,Rm):
  obj.n = env.regs[Rn]
  obj.m = env.regs[Rm]
  obj.operands = [obj.n,obj.m]
  obj.type = type_control_flow
