# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2021 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# reference documentations:
# TriCore TC1.6.2 core architecture manual, volume 1, Core architecure V1.1 2017-08-24.
# TriCore TC1.6.2 core architecture manual, volume 2, Instruction Set  V1.2.1 2019-07-29.

# registers :
# -----------

# data registers:
D = [reg("d%d" % r, 32) for r in range(16)]
# address registers:
A = [reg("a%d" % r, 32) for r in range(16)]

# extended data registers:
# indices are n=0,2,4,6,...,14
E = []
for i in range(0,16,2):
    E.append(composer([D[i],D[i+1]]))
    E.append(None)

# extended address registers:
# indices are n=0,2,4,6,...,14
P = []
for i in range(0,16,2):
    P.append(composer([A[i],A[i+1]]))
    P.append(None)

A[10].ref = "sp"
A[11].ref = "ra"

sp = A[10]
ra = A[11]

pc = reg("pc", 32)


# system registers:
# -----------------

ISP = reg("ISP",32)             # interrupt stack pointer
SYSCON = reg("SYSCON",32)       # system control register

ICR = reg("ICR",32)             # interrupt control register
PIPN = slc(ICR,16,8,"ICR.PIPN") # pending interrupt priority number
IE = slc(ICR,15,1,"IE")         # global interrupt Enable Bit
CCPN = slc(ICR,0,8,"CCPN")      # Current CPU Priority Number

BIV = reg("BIV",32)             # base of interrupt vector table register
BTV = reg("BTV",32)             # base of trap vector table register

PSW = reg("PSW",32)
C   = slc(PSW,31,1,"C")         # carry
V   = slc(PSW,30,1,"V")         # overflow
SV  = slc(PSW,29,1,"SV")        # sticky overflow
AV  = slc(PSW,28,1,"AV")        # advanced overflow
SAV = slc(PSW,27,1,"SAV")       # sticky advanced overflow

RES = slc(PSW,16,11,"reserved")
PRS2 = slc(PSW,15,1,"PRS2")     # protection register set bits[2:3]
S = slc(PSW,14,1,"S")           # safety task identifier
PRS1 = slc(PSW,12,2,"PRS")      # protection register set bits[0:2]
IO = slc(PSW,10,2,"IO")         # access privilege level control
IS = slc(PSW,9,1,"IS")          # interrupt stack control
GW = slc(PSW,8,1,"GW")          # global address register write permission
CDE = slc(PSW,7,1,"CDE")        # call depth count enable
CDC = slc(PSW,0,7,"CDC")        # call depth counter

PCXI = reg("PCXI",32)
PCPN = slc(PCXI,22,8,"PCPN")    # previous CPU priority number
PIE = slc(PCXI,21,1,"PIE")      # previous interrupt enable
UL = slc(PCXI,20,1,"UL")        # upper or lower context tag
PCXS = slc(PCXI,16,4,"PCXS")    # PCX segment address
PCXO = slc(PCXI,0,16,"PCXO")    # PCX offset into segment

FCX = reg("FCX",32)
FCXS = slc(FCX,16,4,"FCXS")    # FCX segment address
FCXO = slc(FCX,0,16,"FCXO")    # FCX offset into segment

LCX = reg("LCX",32)
LCXS = slc(FCX,16,4,"LCXS")    # LCX segment address
LCXO = slc(FCX,0,16,"LCXO")    # LCX offset into segment

def get_current_CSA():
    return composer([cst(0,6),PCXO,cst(0,6),PCXS])

Lower_Context = (PCXI, ra, A[2], A[3], D[0], D[1], D[2], D[3],
                 A[4], A[5], A[6], A[7], D[4], D[5], D[6], D[7])

Upper_Context = (PCXI,PSW,A[10],A[11],D[8],D[9],D[10],D[11],A[12],A[13],A[14],
                 A[15],D[12],D[13],D[14],D[15])

is_reg_pc(pc)
is_reg_flags(PSW)
is_reg_stack(sp)

registers = D+A+[PSW,pc]

CSFR = {
        0xfe00: PCXI,
        0xfe04: PSW,
        0xfe14: SYSCON,
        0xfe20: BIV,
        0xfe24: BTV,
        0xfe28: ISP,
        0xfe2c: ICR,
}

addr = 0xff00
for d in D:
    CSFR[addr] = d
    addr+=4

addr = 0xff80
for a in A:
    CSFR[addr] = d
    addr+=4

Traps = [ ("VAF", "VAP"),                                     # Class 0: MMU
        ("PRIV", "MPR", "MPW", "MPX", "MPP", "MPN", "GRWP"),  # Class 1: Internal Protection Traps
        ("IOPC", "UOPC", "OPD", "ALN", "MEM"),                # Class 2: Instruction Errors
        ("FCD", "CDO", "CDU", "FCU", "CSU", "CTYP", "NEST"),  # Class 3: Context Management
        ("PSE", "DSE", "DAE", "PIE", "DIE", "TAE"),           # Class 4: System Bus & Periph.
        ("OVF", "SOVF"),                                      # Class 5: Assertion Traps
        ("SYS",),                                             # Class 6: System Call,
        ("NMI",)]                                             # Class 7: Non-Maskable Interrupt

internals = {"trap": None}
