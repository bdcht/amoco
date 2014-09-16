# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

from .env import *

#utilities:
#----------

from amoco.cas.utils import *

from amoco.logger import Log
logger = Log(__name__)


#------------------------------------------------------------------------------
# low level functions :
def _switch_isetstate():
    _s = internals['isetstate']
    internals['isetstate'] = 0 if _s==1 else 1
    logger.info('switch to %s instructions'%({'ARM','Thumb'}[internals['isetstate']]))

def __check_state(i,fmap):
    address = fmap(pc)
    if address.bit(0)==1:
        internals['isetstate'] = 1
    elif address.bit(1)==0:
        internals['isetstate'] = 0
    else:
        if address._is_cst:
            raise InstructionError(i)
        else:
            logger.warning('impossible to check isetstate (ARM/Thumb) until pc is cst')

# i_xxx is the translation of UAL (ARM/Thumb) instruction xxx.
#------------------------------------------------------------------------------

# Branch instructions (A4.3, pA4-7)
def i_B(i,fmap):
    cond = CONDITION[i.cond][1]
    fmap[pc] = fmap(tst(cond,pc+i.imm32,pc+i.length))
    __check_state(i,fmap)

def i_CBNZ(i,fmap):
    op1,op2 = i.operands
    fmap[pc] = tst(fmap(i.n)!=0,pc+i.imm32,pc+i.length)
    __check_state(i,fmap)

def i_CBZ(i,fmap):
    op1,op2 = i.operands
    fmap[pc] = tst(fmap(i.n)==0,pc+i.imm32,pc+i.length)
    __check_state(i,fmap)

def i_BL(i,fmap):
    fmap[lr] = fmap(pc)
    fmap[pc] = fmap(pc+i.length)
    offset = i.operands[0]
    __check_state(i,fmap)

def i_BLX(i,fmap):
    fmap[lr] = fmap(pc)
    fmap[pc] = fmap(pc+i.length)
    offset = i.operands[0]
    __check_state(i,fmap)

def i_BX(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    offset = i.operands[0]
    _switch_isetstate()

def i_BXJ(i,fmap):
    fmap[lr] = fmap(pc)
    fmap[pc] = fmap(pc+i.length)
    offset = i.operands[0]
    internals['isetstate'] = 2
    logger.error('switch to Jazelle instructions (unsupported)')

#def i_TBB(i,fmap): pass
#def i_TBH(i,fmap): pass

# Data processing instructions (A4.4)

# standard (4.4.1):
def i_ADC(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result,cout,overflow = AddWithCarry(fmap(op1),fmap(op2),fmap(C))
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[V] = tst(cond,overflow,V)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_ADD(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result,cout,overflow = AddWithCarry(fmap(op1),fmap(op2))
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[V] = tst(cond,overflow,V)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_ADR(i,fmap):
    if i.add:
        result = fmap(pc%4)+i.imm32
    else:
        result = fmap(pc%4)-i.imm32
    cond = CONDITION[i.cond][1]
    fmap[i.d] = tst(cond,result,i.d)

def i_AND(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result = fmap(op1 & op2)
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_BIC(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result = fmap(op1 & (~op2))
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_CMN(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result,cout,overflow = AddWithCarry(fmap(op1),fmap(op2))
    fmap[C] = tst(cond,cout,C)
    fmap[V] = tst(cond,overflow,V)
    fmap[Z] = tst(cond,(result==0),Z)
    fmap[N] = tst(cond,(result<0),N)

def i_CMP(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result,cout,overflow = SubWithBorrow(fmap(op1),fmap(op2))
    fmap[C] = tst(cond,cout,C)
    fmap[V] = tst(cond,overflow,V)
    fmap[Z] = tst(cond,(result==0),Z)
    fmap[N] = tst(cond,(result<0),N)

def i_EOR(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result = fmap(op1 ^ op2)
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_MOV(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1 = i.operands
    result = fmap(op1)
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_MOVW(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1 = i.operands
    result = fmap(op1)
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_MVN(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1 = i.operands
    result = fmap(~op1)
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_ORN(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result = fmap(op1 | ~op2)
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_ORR(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result = fmap(op1 | op2)
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_RSB(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result,cout,overflow = AddWithCarry(fmap(~op1),fmap(op2),bit1)
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[V] = tst(cond,overflow,V)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_RSC(i,fmap):
   fmap[pc] = fmap(pc+i.length)
   cond = CONDITION[i.cond][1]
   dest,op1,op2 = i.operands
   result,cout,overflow = AddWithCarry(fmap(~op1),fmap(op2),fmap(C))
   fmap[dest] = tst(cond,result,dest)
   if dest is pc:
       __check_state(i,fmap)
   elif i.setflags:
       fmap[C] = tst(cond,cout,C)
       fmap[V] = tst(cond,overflow,V)
       fmap[Z] = tst(cond,(result==0),Z)
       fmap[N] = tst(cond,(result<0),N)

def i_SBC(i,fmap):
   fmap[pc] = fmap(pc+i.length)
   cond = CONDITION[i.cond][1]
   dest,op1,op2 = i.operands
   result,cout,overflow = AddWithCarry(fmap(op1),fmap(~op2),fmap(C))
   fmap[dest] = tst(cond,result,dest)
   if dest is pc:
       __check_state(i,fmap)
   elif i.setflags:
       fmap[C] = tst(cond,cout,C)
       fmap[V] = tst(cond,overflow,V)
       fmap[Z] = tst(cond,(result==0),Z)
       fmap[N] = tst(cond,(result<0),N)

def i_SUB(i,fmap):
   fmap[pc] = fmap(pc+i.length)
   cond = CONDITION[i.cond][1]
   dest,op1,op2 = i.operands
   result,cout,overflow = AddWithCarry(fmap(op1),fmap(~op2),bit1)
   fmap[dest] = tst(cond,result,dest)
   if dest is pc:
       __check_state(i,fmap)
   elif i.setflags:
       fmap[C] = tst(cond,cout,C)
       fmap[V] = tst(cond,overflow,V)
       fmap[Z] = tst(cond,(result==0),Z)
       fmap[N] = tst(cond,(result<0),N)

def i_TEQ(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result = fmap(op1 ^ op2)
    fmap[C] = tst(cond,cout,C)
    fmap[Z] = tst(cond,(result==0),Z)
    fmap[N] = tst(cond,(result<0),N)

def i_TST(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result = fmap(op1 & op2)
    fmap[C] = tst(cond,cout,C)
    fmap[Z] = tst(cond,(result==0),Z)
    fmap[N] = tst(cond,(result<0),N)

# shifts (4.4.2)
def i_ASR(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result,cout = ASR_C(fmap(op1),fmap(op2))
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_LSL(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result,cout = LSL_C(fmap(op1),fmap(op2))
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_LSR(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result,cout = LSR_C(fmap(op1),fmap(op2))
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_ROR(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2 = i.operands
    result,cout = ROR_C(fmap(op1),fmap(op2))
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

def i_RRX(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1 = i.operands
    result,cout = RRX_C(fmap(op1),fmap(C))
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[C] = tst(cond,cout,C)
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

# multiply (4.4.3)
# general:
def i_MLA(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2,addend = i.operands
    result = (op1*op2)+addend
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)
    elif i.setflags:
        fmap[Z] = tst(cond,(result==0),Z)
        fmap[N] = tst(cond,(result<0),N)

# MLS
def i_MLS(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,op1,op2,addend = i.operands
    result = addend-(op1*op2)
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        __check_state(i,fmap)

# MUL
# signed:
# SMLABB, SMLABT, SMLATB, SMLATT
# SMLAD
# SMLAL
# SMLALBB, SMLALBT, SMLALTB, SMLALTT
# SMLALD
# SMLAWB, SMLAWT
# SMLSD
# SMLSLD
# SMMLA
# SMMLS
# SMMUL
# SMUAD
# SMULB, SMULBT, SMULTB, SMULTT
# SMULL
# SMULWB, SMULWT
# SMUSD

# saturation (4.4.4)
# SSAT
# SSAT16
# USAT
# USAT16

# packing/unpacking (4.4.5)
# PKH
# SXTAB
# SXTAB16
# SXTAH
# SXTB
# SXTB16
# SXTH
# UXTAB
# UXTAB16
# UXTAH
# UXTB
# UXTB16
# UXTH

# miscellaneous (4.4.6)
def i_BFC(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,lsb,size = i.operands
    src  = fmap(dest)
    result = composer([src[0:lsb],cst(0,size),src[lsb+size:src.size]])
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        raise InstructionError(i)

def i_BFI(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,src,lsb,size = i.operands
    src = fmap(src)
    result = composer([dest[0:lsb],src[lsb,lsb+size],dest[lsb+size:dest.size]])
    fmap[dest] = tst(cond,result,dest)
    if dest is pc:
        raise InstructionError(i)

def i_CLZ(i,fmap):
    fmap[pc] = fmap(pc+i.length)
    cond = CONDITION[i.cond][1]
    dest,src = i.operands
    result = fmap(src)
    if result._is_cst:
        result = [(result.value>>i)&1 for i in range(result.size)]
        result = cst(result.find(1),dest.size)
    else:
        result = top(dest.size)
    fmap[dest] = tst(cond,result,dest)

# MOVT
# RBIT
# REV
# REV16
# REVSH
# SBFX
# SEL
# UBFX
# USAD8
# USADA8

# parallel addition/substraction (4.4.7)
# ADD16
# ASX
# SAX
# SUB16
# ADD8
# SUB8


# divide (4.4.8)
# SDIV
# UDIV

# apsr access (A4.5)
# CPS
# MRS
# MSR

# load/store (A4.6)
# LDR, LDRH, LDRSH, LDRB, LDRSB, LDRD
# STR, STRH, STRB, STRD
# LDRT, LDRHT, LDRSHT, LDRBT, LDRSBT
# STRT, STRHT, STRBT
# LDREX, LDREXH, LDREXB, LDREXD
# STREX, STREXH, STREXB, STREXD

# load/store mulitple (A4.7)
# LDM, LDMIA, LDMFD
# LDMDA, LDMFA
# LDMDB, LDMEA
# LDMIB, LDMED
# POP
# PUSH
# STM, STMIA, STMEA
# STMDA, STMED
# STMDB, STMFD
# STMIB, STMFA

# miscellaneous (A4.8)
# CLREX
# DBG
# DMB
# DSB
# ISB
# IT
# NOP
# PLD, PLDW
# PLI
# SETEND
# SEV
# SVC
# SWP, SWPB
# WFE
# WFI
# YIELD

# coprocessor (A4.9)
# MCR, MCR2
# MCRR, MCRR2
# MRC, MRC2
# MRRC, MRRC2
# LDC, LDC2
# STC, STC2

# SIMD and VFP (A4.10)
# NOT IMPLEMENTED


