# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2013 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

#reference documentation:
#"ARM Architecture Reference Manual ARMv8, for ARMv8-A architecture profile, Errata markup (DDI0487A.a_errata_2013_Q3)

#registers (application level, see B1.3.2) :
#-------------------------------------------

r0  = reg('X0',64)
r1  = reg('X1',64)
r2  = reg('X2',64)
r3  = reg('X3',64)
r4  = reg('X4',64)
r5  = reg('X5',64)
r6  = reg('X6',64)
r7  = reg('X7',64)
r8  = reg('X8',64)
r9  = reg('X9',64)
r10 = reg('X10',64)
r11 = reg('X11',64)
r12 = reg('X12',64)
r13 = reg('X13',64)
r14 = reg('X14',64)
r15 = reg('X15',64)
r16 = reg('X16',64)
r17 = reg('X17',64)
r18 = reg('X18',64)
r19 = reg('X19',64)
r20 = reg('X20',64)
r21 = reg('X21',64)
r22 = reg('X22',64)
r23 = reg('X23',64)
r24 = reg('X24',64)
r25 = reg('X25',64)
r26 = reg('X26',64)
r27 = reg('X27',64)
r28 = reg('X28',64)
r29 = reg('X29',64)
r30 = reg('X30',64)

w0     = slc(r0 ,0,32,ref='W0')
w1     = slc(r1 ,0,32,ref='W1')
w2     = slc(r2 ,0,32,ref='W2')
w3     = slc(r3 ,0,32,ref='W3')
w4     = slc(r4 ,0,32,ref='W4')
w5     = slc(r5 ,0,32,ref='W5')
w6     = slc(r6 ,0,32,ref='W6')
w7     = slc(r7 ,0,32,ref='W7')
w8     = slc(r8 ,0,32,ref='W8')
w9     = slc(r9 ,0,32,ref='W9')
w10    = slc(r10,0,32,ref='W10')
w11    = slc(r11,0,32,ref='W11')
w12    = slc(r12,0,32,ref='W12')
w13    = slc(r13,0,32,ref='W13')
w14    = slc(r14,0,32,ref='W14')
w15    = slc(r15,0,32,ref='W15')
w16    = slc(r16,0,32,ref='W16')
w17    = slc(r17,0,32,ref='W17')
w18    = slc(r18,0,32,ref='W18')
w19    = slc(r19,0,32,ref='W19')
w20    = slc(r20,0,32,ref='W20')
w21    = slc(r21,0,32,ref='W21')
w22    = slc(r22,0,32,ref='W22')
w23    = slc(r23,0,32,ref='W23')
w24    = slc(r24,0,32,ref='W24')
w25    = slc(r25,0,32,ref='W25')
w26    = slc(r26,0,32,ref='W26')
w27    = slc(r27,0,32,ref='W27')
w28    = slc(r28,0,32,ref='W28')
w29    = slc(r29,0,32,ref='W29')
w30    = slc(r30,0,32,ref='W30')

xzr = cst(0,64); wzr = cst(0,32)

sp = reg('SP',64); wsp = slc(sp,0,32,ref='WSP')

#lr = r30 ; lr.ref='LR'    # link register (return address)

pc = reg('PC',64)

pstate = reg('pstate',64)  # in current program status register

N = slc(pstate,0,1,ref='N')   # negative result from ALU
Z = slc(pstate,1,1,ref='Z')   # zero flag
C = slc(pstate,2,1,ref='C')   # carry flag
V = slc(pstate,3,1,ref='V')   # overflow flag


Xregs = [r0,r1,r2,r3,r4,
        r5,r6,r7,r8,r9,
        r10,r11,r12,r13,r14,r15,r16,
        r17,r18,r19,r20,r21,r22,r23,
        r24,r25,r26,r27,r28,r29,r30,
        sp]
Wregs = [w0,w1,w2,w3,w4,
        w5,w6,w7,w8,w9,
        w10,w11,w12,w13,w14,w15,w16,
        w17,w18,w19,w20,w21,w22,w23,
        w24,w25,w26,w27,w28,w29,w30,
        wsp]

SPSel    = slc(pstate,12,1,ref='SPSel')
DAIFSet  = slc(pstate,4,4,ref='DAIFSet')
DAIFClr  = slc(pstate,4,4,ref='DAIFClr')

CONDITION_EQ        = 0x0  # ==
CONDITION_NE        = 0x1  # !=
CONDITION_CS        = 0x2  # >= (unsigned)
CONDITION_CC        = 0x3  # <  (unsigned)
CONDITION_MI        = 0x4  # <0
CONDITION_PL        = 0x5  # >=0
CONDITION_VS        = 0x6  # overflow
CONDITION_VC        = 0x7  # no overflow
CONDITION_HI        = 0x8  # >  (unsigned)
CONDITION_LS        = 0x9  # <= (unsigned)
CONDITION_GE        = 0xa  # >= (signed)
CONDITION_LT        = 0xb  # <  (signed)
CONDITION_GT        = 0xc  # >  (signed)
CONDITION_LE        = 0xd  # <= (signed)
CONDITION_AL        = 0xe  # always
CONDITION_UNDEFINED = 0xf

CONDITION = {
CONDITION_EQ        : ('eq',Z==1),  # ==
CONDITION_NE        : ('ne',Z==0),  # !=
CONDITION_CS        : ('cs',C==1),  # >= (unsigned)
CONDITION_CC        : ('cc',C==0),  # <  (unsigned)
CONDITION_MI        : ('mi',N==1),  # <0
CONDITION_PL        : ('pl',N==0),  # >=0
CONDITION_VS        : ('vs',V==1),  # overflow
CONDITION_VC        : ('vc',V==0),  # no overflow
CONDITION_HI        : ('hi',(C==1)&(Z==0)),  # >  (unsigned)
CONDITION_LS        : ('ls',(C==0)|(Z==1)),  # <= (unsigned)
CONDITION_GE        : ('ge',(N==V)),  # >= (signed)
CONDITION_LT        : ('lt',(N!=V)),  # <  (signed)
CONDITION_GT        : ('gt',(Z==0)&(N==V)),  # >  (signed)
CONDITION_LE        : ('le',(Z==1)|(N!=V)),  # <= (signed)
CONDITION_AL        : ('  ',bit1),  # always
CONDITION_UNDEFINED : ('??',top(1)),
}


# internal states not exposed to symbolic interpreter:
#-----------------------------------------------------
internals = {         # states MUST be in a mutable object !
    'endianstate': 0, # 0: little-endian, 1: big-endian
}

# SIMD and VFP (floating point) extensions:
# NOT IMPLEMENTED

# Coprocessor (CPxx) support:
# NOT IMPLEMENTED

