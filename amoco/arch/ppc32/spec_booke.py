# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2022 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from . import env

from amoco.arch.core import *

# -------------------------------------------------------
# instruction PPC Book E decoders
# ref:
#   ST RM0004 Reference manual
#   Programmer's reference manual for Book E processors
#   May 2015, DocID13694 Rev 2, 1025p.
# -------------------------------------------------------

ISPECS = []

@ispec("32<[ 011111 rD(5) rA(5) rB(5) .OE 100001010 .Rc ]", mnemonic="add")
@ispec("32<[ 011111 rD(5) rA(5) rB(5) .OE 000001010 .Rc ]", mnemonic="addc")
@ispec("32<[ 011111 rD(5) rA(5) rB(5) .OE 010001010 .Rc ]", mnemonic="adde")
@ispec("32<[ 011111 rD(5) rA(5) rB(5) .OE 110001010 .Rc ]", mnemonic="adde64")
@ispec("32<[ 011111 rD(5) rA(5) rB(5) .OE 111101011 .Rc ]", mnemonic="divw")
@ispec("32<[ 011111 rD(5) rA(5) rB(5) .OE 111001011 .Rc ]", mnemonic="divwu")
@ispec("32<[ 011111 rD(5) rA(5) rB(5) .OE 011101011 .Rc ]", mnemonic="mullw")
@ispec("32<[ 011111 rD(5) rA(5) rB(5) .OE 000101000 .Rc ]", mnemonic="subf")
@ispec("32<[ 011111 rD(5) rA(5) rB(5) .OE 000001000 .Rc ]", mnemonic="subfc")
@ispec("32<[ 011111 rD(5) rA(5) rB(5) .OE 010001000 .Rc ]", mnemonic="subfe")
@ispec("32<[ 011111 rD(5) rA(5) rB(5) .OE 110001000 .Rc ]", mnemonic="subfe64")
def ppc_OE_Rc(obj,rD,rA,rB):
    if obj.mnemonic.endswith("64") and obj.Rc==1:
        raise InstructionError(obj)
    obj.operands = [env.GPR[rD],env.GPR[rA],env.GPR[rB]]
    obj.type = type_data_processing

@ispec("32<[ 011111 rT(5) rA(5) rB(5) .OE 111101001 - ]", mnemonic="divd")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) .OE 111001001 - ]", mnemonic="divdu")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) .OE 011101001 - ]", mnemonic="mulld")
def ppc_OE(obj,rT,rA,rB):
    obj.operands = [env.GPR[rT],env.GPR[rA],env.GPR[rB]]
    obj.type = type_data_processing

@ispec("32<[ 011111 rT(5) rA(5) rB(5) - 001001001 - ]", mnemonic="mulhd")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) - 000001001 - ]", mnemonic="mulhdu")
def ppc_mulhd(obj,rT,rA,rB):
    obj.operands = [env.GPR[rT],env.GPR[rA],env.GPR[rB]]
    obj.type = type_data_processing

@ispec("32<[ 011111 rT(5) rA(5) rB(5) - 001001011 .Rc ]", mnemonic="mulhw")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) - 000001011 .Rc ]", mnemonic="mulhwu")
def ppc_Rc(obj,rT,rA,rB):
    obj.operands = [env.GPR[rT],env.GPR[rA],env.GPR[rB]]
    obj.type = type_data_processing

@ispec("32<[ 100010=U rT(5) rA(5) D(16) ]", mnemonic="lbz")
@ispec("32<[ 100011=U rT(5) rA(5) D(16) ]", mnemonic="lbzu")
@ispec("32<[ 100010=U rT(5) rA(5) D(16) ]", mnemonic="lha")
@ispec("32<[ 100011=U rT(5) rA(5) D(16) ]", mnemonic="lhau")
@ispec("32<[ 101000=U rT(5) rA(5) D(16) ]", mnemonic="lhz")
@ispec("32<[ 101001=U rT(5) rA(5) D(16) ]", mnemonic="lhzu")
@ispec("32<[ 101110=U rT(5) rA(5) D(16) ]", mnemonic="lmw")
@ispec("32<[ 100000=U rT(5) rA(5) D(16) ]", mnemonic="lwz")
@ispec("32<[ 100001=U rT(5) rA(5) D(16) ]", mnemonic="lwzu")
@ispec("32<[ 100110=U rT(5) rA(5) D(16) ]", mnemonic="stb")
@ispec("32<[ 100111=U rT(5) rA(5) D(16) ]", mnemonic="stbu")
@ispec("32<[ 101100=U rT(5) rA(5) D(16) ]", mnemonic="sth")
@ispec("32<[ 101101=U rT(5) rA(5) D(16) ]", mnemonic="sthu")
@ispec("32<[ 100100=U rT(5) rA(5) D(16) ]", mnemonic="stw")
@ispec("32<[ 100101=U rT(5) rA(5) D(16) ]", mnemonic="stwu")
def ppc_load_store(obj,U,rT,rA,D):
    if rA==0:
        addr = env.cst(0,32)
    else:
        addr = env.GPR[rA]
    if U==1:
        obj.rA = rA
    addr += env.cst(D,16).signextend(32)
    obj.operands = [env.GPR[rT],env.ptr(addr)]
    obj.type = type_data_processing

@ispec("32<[ 110010=U rT(5) rA(5) D(16) ]", mnemonic="lfd")
@ispec("32<[ 110011=U rT(5) rA(5) D(16) ]", mnemonic="lfdu")
@ispec("32<[ 110000=U rT(5) rA(5) D(16) ]", mnemonic="lfs")
@ispec("32<[ 110001=U rT(5) rA(5) D(16) ]", mnemonic="lfsu")
@ispec("32<[ 110110=U rT(5) rA(5) D(16) ]", mnemonic="stfd")
@ispec("32<[ 110111=U rT(5) rA(5) D(16) ]", mnemonic="stfdu")
@ispec("32<[ 110100=U rT(5) rA(5) D(16) ]", mnemonic="stfs")
@ispec("32<[ 110101=U rT(5) rA(5) D(16) ]", mnemonic="stfsu")
@ispec("32<[ 101111=U rT(5) rA(5) D(16) ]", mnemonic="stmw")
def ppc_load_store(obj,U,rT,rA,D):
    if rA==0:
        addr = env.cst(0,32)
    else:
        addr = env.GPR[rA]
    if U==1:
        obj.rA = rA
    addr += env.cst(D,16).signextend(32)<<2
    obj.operands = [env.FPR[rT],env.ptr(addr)]
    obj.type = type_data_processing

@ispec("32<[ 111010 rT(5) rA(5) DE(12) 000 0=U ]", mnemonic="lbze")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 000 1=U ]", mnemonic="lbzue")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 010 0=U ]", mnemonic="lhae")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 010 1=U ]", mnemonic="lhaue")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 001 0=U ]", mnemonic="lhze")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 001 1=U ]", mnemonic="lhzue")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 011 0=U ]", mnemonic="lwze")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 011 1=U ]", mnemonic="lwzue")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 100 0=U ]", mnemonic="stbe")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 100 1=U ]", mnemonic="stbue")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 101 0=U ]", mnemonic="sthe")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 101 1=U ]", mnemonic="sthue")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 111 0=U ]", mnemonic="stwe")
@ispec("32<[ 111010 rT(5) rA(5) DE(12) 111 1=U ]", mnemonic="stwue")
def ppc_load_store(obj,rT,rA,DE,U):
    if rA==0:
        addr = env.cst(0,32)
    else:
        addr = env.GPR[rA]
    if U==1:
        obj.rA = rA
    addr += env.cst(DE,12).signextend(32)
    obj.operands = [env.GPR[rT],env.ptr(addr)]
    obj.type = type_data_processing

@ispec("32<[ 111110 rT(5) rA(5) DE(12) 000 0=U ]", mnemonic="lde")
@ispec("32<[ 111110 rT(5) rA(5) DE(12) 000 1=U ]", mnemonic="ldue")
@ispec("32<[ 111110 rT(5) rA(5) DE(12) 100 0=U ]", mnemonic="stde")
@ispec("32<[ 111110 rT(5) rA(5) DE(12) 100 1=U ]", mnemonic="stdue")
def ppc_load_store(obj,rT,rA,DE,U):
    if rA==0:
        addr = env.cst(0,32)
    else:
        addr = env.GPR[rA]
    if U==1:
        obj.rA = rA
    addr += env.cst(DE,12).signextend(32)<<2
    obj.operands = [env.GPR[rT],env.ptr(addr)]
    obj.type = type_data_processing

@ispec("32<[ 111110 rT(5) rA(5) DE(12) 011 0=U ]", mnemonic="lfde")
@ispec("32<[ 111110 rT(5) rA(5) DE(12) 011 1=U ]", mnemonic="lfdue")
@ispec("32<[ 111110 rT(5) rA(5) DE(12) 010 0=U ]", mnemonic="lfse")
@ispec("32<[ 111110 rT(5) rA(5) DE(12) 010 1=U ]", mnemonic="lfsue")
@ispec("32<[ 111110 rT(5) rA(5) DE(12) 111 0=U ]", mnemonic="stfde")
@ispec("32<[ 111110 rT(5) rA(5) DE(12) 111 1=U ]", mnemonic="stfdue")
@ispec("32<[ 111110 rT(5) rA(5) DE(12) 110 0=U ]", mnemonic="stfse")
@ispec("32<[ 111110 rT(5) rA(5) DE(12) 110 1=U ]", mnemonic="stfsue")
def ppc_load_store(obj,rT,rA,DE,U):
    if rA==0:
        addr = env.cst(0,32)
    else:
        addr = env.GPR[rA]
    if U==1:
        obj.rA = rA
    addr += env.cst(DE,12).signextend(32)<<2
    obj.operands = [env.FPR[rT],env.ptr(addr)]
    obj.type = type_data_processing

@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0001 0=U 1 0 111 - ]", mnemonic="lbzx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0001 1=U 1 0 111 - ]", mnemonic="lbzux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0001 0=U 1 1 111 - ]", mnemonic="lbzxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0001 1=U 1 1 111 - ]", mnemonic="lbzuxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1100 0=U 1 0 111 - ]", mnemonic="ldx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1100 1=U 1 0 111 - ]", mnemonic="ldux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1100 0=U 1 1 111 - ]", mnemonic="ldxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1100 1=U 1 1 111 - ]", mnemonic="lduxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0101 0=U 1 0 111 - ]", mnemonic="lhax")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0101 1=U 1 0 111 - ]", mnemonic="lhaux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0101 0=U 1 1 111 - ]", mnemonic="lhaxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0101 1=U 1 1 111 - ]", mnemonic="lhauxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0100 0=U 1 0 111 - ]", mnemonic="lhzx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0100 1=U 1 0 111 - ]", mnemonic="lhzux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0100 0=U 1 1 111 - ]", mnemonic="lhzxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0100 1=U 1 1 111 - ]", mnemonic="lhzuxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0000 0=U 1 0 111 - ]", mnemonic="lwzx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0000 1=U 1 0 111 - ]", mnemonic="lwzux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0000 0=U 1 1 111 - ]", mnemonic="lwzxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0000 1=U 1 1 111 - ]", mnemonic="lwzuxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0011 0=U 1 0 111 - ]", mnemonic="stbx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0011 1=U 1 0 111 - ]", mnemonic="stbux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0011 0=U 1 1 111 - ]", mnemonic="stbxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0011 1=U 1 1 111 - ]", mnemonic="stbuxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1110 0=U 1 1 111 - ]", mnemonic="stdxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1110 1=U 1 1 111 - ]", mnemonic="stduxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0110 0=U 1 0 111 - ]", mnemonic="sthx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0110 1=U 1 0 111 - ]", mnemonic="sthux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0110 0=U 1 1 111 - ]", mnemonic="sthxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0110 1=U 1 1 111 - ]", mnemonic="sthuxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0010 0=U 1 0 111 - ]", mnemonic="stwx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0010 1=U 1 0 111 - ]", mnemonic="stwux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0010 0=U 1 1 111 - ]", mnemonic="stwxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 0010 1=U 1 1 111 - ]", mnemonic="stwuxe")
def ppc_load_store(obj,rT,rA,rB,U):
    if rA==0:
        addr = env.cst(0,32)
    else:
        addr = env.GPR[rA]
    if U==1:
        obj.rA = rA
    addr += env.GPR[rB]
    obj.operands = [env.GPR[rT],env.ptr(addr)]
    obj.type = type_data_processing

@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1001 0=U 1 0 111 - ]", mnemonic="lfdx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1001 1=U 1 0 111 - ]", mnemonic="lfdux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1001 0=U 1 1 111 - ]", mnemonic="lfdxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1001 1=U 1 1 111 - ]", mnemonic="lfduxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1000 0=U 1 0 111 - ]", mnemonic="lfsx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1000 1=U 1 0 111 - ]", mnemonic="lfsux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1000 0=U 1 1 111 - ]", mnemonic="lfsxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1000 1=U 1 1 111 - ]", mnemonic="lfsuxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1011 0=U 1 0 111 - ]", mnemonic="stfdx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1011 1=U 1 0 111 - ]", mnemonic="stfdux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1011 0=U 1 1 111 - ]", mnemonic="stfdxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1011 1=U 1 1 111 - ]", mnemonic="stfduxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1111 0=U 1 0 111 - ]", mnemonic="stfiwx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1111 0=U 1 1 111 - ]", mnemonic="stfiwxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1010 0=U 1 0 111 - ]", mnemonic="stfsx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1010 1=U 1 0 111 - ]", mnemonic="stfsux")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1010 0=U 1 1 111 - ]", mnemonic="stfsxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 1010 1=U 1 1 111 - ]", mnemonic="stfsuxe")
def ppc_load(obj,rT,rA,rB,U):
    if rA==0:
        addr = env.cst(0,32)
    else:
        addr = env.GPR[rA]
    if U==1:
        obj.rA = rA
    addr += env.GPR[rB]
    obj.operands = [env.FPR[rT],env.ptr(addr)]
    obj.type = type_data_processing

@ispec("32<[ 011111 rT(5) rA(5) rB(5) 011101 1=E 111 - ]", mnemonic="ldarxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 000001 0=E 100 - ]", mnemonic="lwarx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 000111 1=E 110 - ]", mnemonic="lwarxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 100001 0=E 110 - ]", mnemonic="lwbrx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 100001 1=E 110 - ]", mnemonic="lwbrxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 110001 0=E 110 - ]", mnemonic="lhbrx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 110001 1=E 110 - ]", mnemonic="lhbrxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 011111 1=E 111 1 ]", mnemonic="stdcxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 111001 0=E 110 - ]", mnemonic="sthbrx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 111001 1=E 110 - ]", mnemonic="sthbrxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 101001 0=E 110 - ]", mnemonic="stwbrx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 101001 1=E 110 - ]", mnemonic="stwbrxe")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 001001 0=E 110 - ]", mnemonic="stwcx")
@ispec("32<[ 011111 rT(5) rA(5) rB(5) 001001 1=E 110 - ]", mnemonic="stwcxe")
def ppc_load(obj,rT,rA,rB,E):
    if rA==0:
        addr = env.GPR[rB]
    else:
        addr = env.GPR[rA]+env.GPR[rB]
    obj.operands = [env.GPR[rT],env.ptr(addr)]
    obj.type = type_data_processing

@ispec("32<[ 011111 rT(5) rA(5) NB(5) 1001010101 - ]", mnemonic="lswi")
@ispec("32<[ 011111 rT(5) rA(5) NB(5) 1000010101 - ]", mnemonic="lswx")
@ispec("32<[ 011111 rT(5) rA(5) NB(5) 1011010101 - ]", mnemonic="stswi")
@ispec("32<[ 011111 rT(5) rA(5) NB(5) 1010010101 - ]", mnemonic="stswx")
def ppc_load(obj,rT,rA,NB):
    if rA==0:
        addr = env.GPR[rB]
    else:
        addr = env.GPR[rA]+env.GPR[rB]
    if obj.mnemonic=="lswi" and NB==0:
        n = 32
    else:
        n = NB
    obj.operands = [env.GPR[rT],env.ptr(addr),NB]
    obj.type = type_data_processing

@ispec("32<[ 00111 s rT(5) rA(5) SI(16) ]", mnemonic="addi")
@ispec("32<[ 00011 1=s rT(5) rA(5) SI(16) ]", mnemonic="mulli")
@ispec("32<[ 00100 0=s rT(5) rA(5) SI(16) ]", mnemonic="subfic")
def ppc_S(obj,s,rT,rA,SI):
    obj.s = s
    if s==0:
        imm = env.cst(SI,16).signextend(32)
    else:
        imm = env.cst(SI,32)<<16
    obj.operands = [env.GPR[rT],env.GPR[rA],imm]
    obj.type = type_data_processing

@ispec("32<[ 00110 .Rc rT(5) rA(5) SI(16) ]", mnemonic="addic")
def ppc_Rc(obj,rT,rA,SI):
    imm = env.cst(SI,16).signextend(32)
    obj.operands = [env.GPR[rT],env.GPR[rA],imm]
    obj.type = type_data_processing

@ispec("32<[ 011111 rT(5) rA(5) ----- .OE 0=E 11101010 .Rc ]", mnemonic="addme")
@ispec("32<[ 011111 rT(5) rA(5) ----- .OE 1=E 11101010 .Rc ]", mnemonic="addme64")
@ispec("32<[ 011111 rT(5) rA(5) ----- .OE 0=E 11001010 .Rc ]", mnemonic="addze")
@ispec("32<[ 011111 rT(5) rA(5) ----- .OE 1=E 11001010 .Rc ]", mnemonic="addze64")
@ispec("32<[ 011111 rT(5) rA(5) ----- .OE 0=E 01101000 .Rc ]", mnemonic="neg")
@ispec("32<[ 011111 rT(5) rA(5) ----- .OE 0=E 11101000 .Rc ]", mnemonic="subfme")
@ispec("32<[ 011111 rT(5) rA(5) ----- .OE 1=E 11101000 .Rc ]", mnemonic="subfme64")
@ispec("32<[ 011111 rT(5) rA(5) ----- .OE 0=E 11001000 .Rc ]", mnemonic="subfze")
@ispec("32<[ 011111 rT(5) rA(5) ----- .OE 1=E 11001000 .Rc ]", mnemonic="subfze64")
def ppc_OE_Rc(obj,rT,rA,E):
    if obj.mnemonic.endswith("64") and obj.Rc==1:
        raise InstructionError(obj)
    obj.E = E
    obj.operands = [env.GPR[rT],env.GPR[rA]]
    obj.type = type_data_processing

@ispec("32<[ 011111 rS(5) rA(5) rB(5) 0000011100 .Rc ]", mnemonic="and")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 0000111100 .Rc ]", mnemonic="andc")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 0100011100 .Rc ]", mnemonic="eqv")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 0111011100 .Rc ]", mnemonic="nand")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 0001111100 .Rc ]", mnemonic="nor")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 0110111100 .Rc ]", mnemonic="or")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 0110011100 .Rc ]", mnemonic="orc")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 0000011000 .Rc ]", mnemonic="slw")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 1100011000 .Rc ]", mnemonic="sraw")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 1000011000 .Rc ]", mnemonic="srw")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 0100111100 .Rc ]", mnemonic="xor")
def ppc_Rc(obj,rS,rA,rB):
    obj.operands = [env.GPR[rA],env.GPR[rS],env.GPR[rB]]
    obj.type = type_data_processing

@ispec("32<[ 011111 rS(5) rA(5) SH(5) 1100011000 .Rc ]", mnemonic="srawi")
def ppc_Rc(obj,rS,rA,SH):
    obj.operands = [env.GPR[rA],env.GPR[rS],env.cst(SH,5)]
    obj.type = type_data_processing

@ispec("32<[ 011111 rS(5) rA(5) rB(5) 0000011011 - ]", mnemonic="sld")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 1100011010 - ]", mnemonic="srad")
@ispec("32<[ 011111 rS(5) rA(5) rB(5) 1000011011 - ]", mnemonic="srd")
def ppc_sld(obj,rS,rA,rB):
    obj.operands = [env.GPR[rA],env.GPR[rS],env.GPR[rB]]
    obj.type = type_data_processing

@ispec("32<[ 011110 rS(5) rA(5) rB(5) mb(5) mb0 1000 - ]", mnemonic="rldcl")
@ispec("32<[ 011110 rS(5) rA(5) rB(5) mb(5) mb0 1001 - ]", mnemonic="rldcr")
def ppc_rldc(obj,rS,rA,rB,mb,mb0):
    mask = env.cst(mb+(mb0<<5),32)
    obj.operands = [env.GPR[rA],env.GPR[rS],env.GPR[rB],mask]
    obj.type = type_data_processing

@ispec("32<[ 010100 rS(5) rA(5) sh(5) mb(5) me(5) .Rc ]", mnemonic="rlwimi")
@ispec("32<[ 010111 rS(5) rA(5) sh(5) mb(5) me(5) .Rc ]", mnemonic="rlwnm")
@ispec("32<[ 010101 rS(5) rA(5) sh(5) mb(5) me(5) .Rc ]", mnemonic="rlwinm")
def ppc_Rc(obj,rS,rA,sh,mb,me):
    sh = env.cst(sh,5)
    mb = env.cst(mb,5)
    me = env.cst(me,5)
    obj.operands = [env.GPR[rA],env.GPR[rS],sh,mb,me]
    obj.type = type_data_processing

@ispec("32<[ 011110 rS(5) rA(5) sh(5) mb(5) mb0 000 sh0 - ]", mnemonic="rldicl")
@ispec("32<[ 011110 rS(5) rA(5) sh(5) mb(5) mb0 001 sh0 - ]", mnemonic="rldicr")
@ispec("32<[ 011110 rS(5) rA(5) sh(5) mb(5) mb0 010 sh0 - ]", mnemonic="rldic")
@ispec("32<[ 011110 rS(5) rA(5) sh(5) mb(5) mb0 011 sh0 - ]", mnemonic="rldimi")
def ppc_rld(obj,rS,rA,sh,mb,mb0,sh0):
    mask = env.cst(mb+(mb0<<5),32)
    obj.operands = [env.GPR[rA],env.GPR[rS],env.cst(sh+(sh0<<5),6),mask]
    obj.type = type_data_processing

@ispec("32<[ 011110 rS(5) rA(5) sh(5) 110011 101 sh0 - ]", mnemonic="sradi")
def ppc_rld(obj,rS,rA,sh,sh0):
    mask = env.cst(mb+(mb0<<5),32)
    obj.operands = [env.GPR[rA],env.GPR[rS],env.cst(sh+(sh0<<5),6)]
    obj.type = type_data_processing

@ispec("32<[ 111111 FRT(5) ----- FRB(5) 0100001000 .Rc ]", mnemonic="fabs")
@ispec("32<[ 111111 FRT(5) ----- FRB(5) 0000001110 .Rc ]", mnemonic="fctiw")
@ispec("32<[ 111111 FRT(5) ----- FRB(5) 0000001111 .Rc ]", mnemonic="fctiwz")
@ispec("32<[ 111111 FRT(5) ----- FRB(5) 0001001000 .Rc ]", mnemonic="fmr")
@ispec("32<[ 111111 FRT(5) ----- FRB(5) 0010001000 .Rc ]", mnemonic="fnabs")
@ispec("32<[ 111111 FRT(5) ----- FRB(5) 0000101000 .Rc ]", mnemonic="fneg")
@ispec("32<[ 111111 FRT(5) ----- FRB(5) 0000001100 .Rc ]", mnemonic="frsp")
def ppc_Rc(obj,FRT,FRB):
    obj.operands = [env.FPR[FRT],env.FPR[FRB]]
    obj.type = type_data_processing

@ispec("32<[ 111111 FRT(5) ----- FRB(5) 1101001110 - ]", mnemonic="fcfid")
@ispec("32<[ 111111 FRT(5) ----- FRB(5) 1100101110 - ]", mnemonic="fctid")
@ispec("32<[ 111111 FRT(5) ----- FRB(5) 1100101111 - ]", mnemonic="fctidz")
def ppc_fcfid(obj,FRT,FRB):
    obj.operands = [env.FPR[FRT],env.FPR[FRB]]
    obj.type = type_data_processing

@ispec("32<[ 111111 FRT(5) FRA(5) FRB(5) -----10101 .Rc ]", mnemonic="fadd")
@ispec("32<[ 111011 FRT(5) FRA(5) FRB(5) -----10101 .Rc ]", mnemonic="fadds")
@ispec("32<[ 111111 FRT(5) FRA(5) FRB(5) -----10010 .Rc ]", mnemonic="fdiv")
@ispec("32<[ 111011 FRT(5) FRA(5) FRB(5) -----10010 .Rc ]", mnemonic="fdivs")
@ispec("32<[ 111111 FRT(5) FRA(5) FRB(5) -----10100 .Rc ]", mnemonic="fsub")
@ispec("32<[ 111011 FRT(5) FRA(5) FRB(5) -----10100 .Rc ]", mnemonic="fsubs")
def ppc_Rc(obj,FRT,FRA,FRB):
    obj.operands = [env.FPR[FRT],env.FPR[FRA],env.FPR[FRB]]
    obj.type = type_data_processing

@ispec("32<[ 111011 FRT(5) ----- FRB(5) ----- 11000 .Rc ]", mnemonic="fres")
@ispec("32<[ 111111 FRT(5) ----- FRB(5) ----- 11010 .Rc ]", mnemonic="frsqrte")
@ispec("32<[ 111111 FRT(5) ----- FRB(5) ----- 10110 .Rc ]", mnemonic="fsqrt")
@ispec("32<[ 111011 FRT(5) ----- FRB(5) ----- 10110 .Rc ]", mnemonic="fsqrts")
def ppc_Rc(obj,FRT,FRB):
    obj.operands = [env.FPR[FRT],env.FPR[FRB]]
    obj.type = type_data_processing

@ispec("32<[ 111111 FRT(5) FRA(5) FRB(5) FRC(5) 11101 .Rc ]", mnemonic="fmadd")
@ispec("32<[ 111011 FRT(5) FRA(5) FRB(5) FRC(5) 11101 .Rc ]", mnemonic="fmadds")
@ispec("32<[ 111111 FRT(5) FRA(5) FRB(5) FRC(5) 11100 .Rc ]", mnemonic="fmsub")
@ispec("32<[ 111011 FRT(5) FRA(5) FRB(5) FRC(5) 11100 .Rc ]", mnemonic="fmsubs")
@ispec("32<[ 111111 FRT(5) FRA(5) FRB(5) FRC(5) 11111 .Rc ]", mnemonic="fnmadd")
@ispec("32<[ 111011 FRT(5) FRA(5) FRB(5) FRC(5) 11111 .Rc ]", mnemonic="fnmadds")
@ispec("32<[ 111111 FRT(5) FRA(5) FRB(5) FRC(5) 11110 .Rc ]", mnemonic="fnmsub")
@ispec("32<[ 111011 FRT(5) FRA(5) FRB(5) FRC(5) 11110 .Rc ]", mnemonic="fnmsubs")
@ispec("32<[ 111111 FRT(5) FRA(5) FRB(5) FRC(5) 10111 .Rc ]", mnemonic="fsel")
def ppc_Rc(obj,FRT,FRA,FRB,FRC):
    obj.operands = [env.FPR[FRT],env.FPR[FRA],env.FPR[FRC],env.FPR[FRB]]
    obj.type = type_data_processing

@ispec("32<[ 111111 FRT(5) FRA(5) ----- FRC(5) 11101 .Rc ]", mnemonic="fmul")
@ispec("32<[ 111011 FRT(5) FRA(5) ----- FRC(5) 11101 .Rc ]", mnemonic="fmuls")
def ppc_Rc(obj,FRT,FRA,FRC):
    obj.operands = [env.FPR[FRT],env.FPR[FRA],env.FPR[FRC],env.FPR[FRB]]
    obj.type = type_data_processing

@ispec("32<[ 111111 FRT(5) ----- ----- 10010 00111 .Rc ]", mnemonic="mffs")
def ppc_Rc(obj,FRT):
    obj.operands = [env.FPR[FRT]]
    obj.type = type_data_processing

@ispec("32<[ 111111 - FLM(8) - FRB(5) 1011000111 .Rc ]", mnemonic="mtfsf")
def ppc_Rc(obj,FLM,FRB):
    obj.operands = [env.cst(FLM,8),env.FPR[FRB]]
    obj.type = type_data_processing

@ispec("32<[ 111111 BF(3) ------- U(4) - 0010000110 .Rc ]", mnemonic="mtfsfi")
def ppc_Rc(obj,BF,U):
    obj.operands = [env.cst(BF,3),env.cst(U,4)]
    obj.type = type_data_processing

@ispec("32<[ 111111 BF(3) -- FRA(5) FRB(5) 0000000000 - ]", mnemonic="fcmpu")
@ispec("32<[ 111111 BF(3) -- FRA(5) FRB(5) 0000100000 - ]", mnemonic="fcmpuo")
def ppc_fcmpu(obj,BF,FRA,FRB):
    obj.operands = [BF,env.FPR[FRA],env.FPR[FRB]]
    obj.type = type_data_processing

@ispec("32<[ 01111 0=s rS(5) rA(5) UI(16) ]", mnemonic="andi")
@ispec("32<[ 01111 1=s rS(5) rA(5) UI(16) ]", mnemonic="andis")
@ispec("32<[ 01100 0=s rS(5) rA(5) UI(16) ]", mnemonic="ori")
@ispec("32<[ 01100 1=s rS(5) rA(5) UI(16) ]", mnemonic="oris")
@ispec("32<[ 01101 0=s rS(5) rA(5) UI(16) ]", mnemonic="xori")
@ispec("32<[ 01101 1=s rS(5) rA(5) UI(16) ]", mnemonic="xoris")
def ppc_S(obj,s,rS,rA,UI):
    obj.Rc = 1
    obj.s = s
    if s==0:
        imm = env.cst(UI,16).zeroextend(32)
    else:
        imm = env.cst(UI,32)<<16
    obj.operands = [env.GPR[rA],env.GPR[rS],imm]
    obj.type = type_data_processing

@ispec("32<[ 010 E 10 LI(24) .AA .LK ]", mnemonic="b")
def ppc_E_AA_LK(obj,E,LI):
    obj.E = E
    soff = env.cst(LI,24).signextend(32)<<2
    obj.operands = [soff]
    obj.type = type_control_flow

@ispec("32<[ 010000 ~BO(5) ~BI(5) BD(14) .AA .LK ]", mnemonic="bc")
@ispec("32<[ 001001 ~BO(5) ~BI(5) BD(14) .AA .LK ]", mnemonic="bce")
def ppc_AA_LK(obj,BO,BI,BD):
    soff = env.cst(BD,14).signextend(32)<<2
    obj.operands = [BO,BI,soff]
    obj.type = type_control_flow

@ispec("32<[ 010011 ~BO(5) ~BI(5) ----- 100001000 .E .LK ]", mnemonic="bcctr")
@ispec("32<[ 010011 ~BO(5) ~BI(5) ----- 000001000 .E .LK ]", mnemonic="bclr")
def ppc_E_LK(obj,BO,BI):
    obj.operands = [BO,BI]
    obj.type = type_control_flow

@ispec("32<[ 011111 TO(5) RA(5) RB(5) 0001000100 - ]", mnemonic="td")
@ispec("32<[ 011111 TO(5) RA(5) RB(5) 0000000100 - ]", mnemonic="tw")
def ppc_trap(obj,TO,RA,RB):
    obj.operands = [env.cst(TO,5),env.GPR[RA],env.GPR[RB]]
    obj.type = type_system

@ispec("32<[ 011111 ----- RA(5) RB(5) 1100010010=E - ]", mnemonic="tlbivax")
@ispec("32<[ 011111 ----- RA(5) RB(5) 1100010011=E - ]", mnemonic="tlbivaxe")
def ppc_trap(obj,RA,RB,E):
    if RA==0:
        addr = env.cst(0,32)
    else:
        addr = env.GPR[RA]
    obj.E = E
    obj.operands = [addr,env.GPR[RB]]
    obj.type = type_system

@ispec("32<[ 000010 TO(5) RA(5) SI(16) ]", mnemonic="tdi")
@ispec("32<[ 000011 TO(5) RA(5) SI(16) ]", mnemonic="twi")
def ppc_trap(obj,TO,RA,SI):
    obj.operands = [env.cst(TO,5),env.GPR[RA],env.cst(SI,16).signextend(32)]
    obj.type = type_system

@ispec("32<[ 011111 BF(3) - L rA(5) rB(5) 0000000000 - ]", mnemonic="cmp")
@ispec("32<[ 011111 BF(3) - L rA(5) rB(5) 0000100000 - ]", mnemonic="cmpl")
def ppc_cmp(obj,BF,L,rA,rB):
    obj.operands = [BF,L,env.GPR[rA],env.GPR[rB]]
    obj.type = type_data_processing

@ispec("32<[ 010011 BF(3) -- BFA(3) ------- 0000000000 - ]", mnemonic="mcfr")
@ispec("32<[ 111111 BF(3) -- BFA(3) ------- 0001000000 - ]", mnemonic="mcfrs")
def ppc_mcfr(obj,BF,BFA):
    obj.operands = [BF,BFA]
    obj.type = type_data_processing

@ispec("32<[ 011111 BF(3) ----- ------- 1000000000 - ]", mnemonic="mcrxr")
@ispec("32<[ 011111 BF(3) ----- ------- 1000100000 - ]", mnemonic="mcrxr64")
def ppc_mcrx(obj,BF):
    obj.operands = [BF]
    obj.type = type_data_processing

@ispec("32<[ 111111 BT(5) ---------- 0001000110 .Rc ]", mnemonic="mtfsb0")
@ispec("32<[ 111111 BT(5) ---------- 0000100110 .Rc ]", mnemonic="mtfsb1")
def ppc_mcrx(obj,BT):
    obj.operands = [BT]
    obj.type = type_data_processing

@ispec("32<[ 011111 RT(5) RA(5) ----- 0100010011 - ]", mnemonic="mfapidi")
def ppc_mfapidi(obj,RT,RA):
    obj.operands = [env.GPR[RT],env.GPR[RA]]
    obj.type = type_data_processing

@ispec("32<[ 011111 RT(5) ----- ----- 0000010011 - ]", mnemonic="mfcr")
@ispec("32<[ 011111 RT(5) ----- ----- 0001010011 - ]", mnemonic="mfmsr")
@ispec("32<[ 011111 RT(5) ----- ----- 0010010010 - ]", mnemonic="mtmsr")
def ppc_mfcr(obj,RT):
    obj.operands = [env.GPR[RT]]
    obj.type = type_data_processing

@ispec("32<[ 011111 RT(5) dcrn2(5) dcrn1(5) 0101000011 - ]", mnemonic="mfdcr")
def ppc_mfdcr(obj,RT,dcrn2,dcrn1):
    obj.operands = [env.GPR[RT],env.DCREG(dcrn2+(dcrn1<<5))]
    obj.type = type_data_processing

@ispec("32<[ 011111 RS(5) dcrn2(5) dcrn1(5) 0111000011 - ]", mnemonic="mtdcr")
def ppc_mtdcr(obj,RS,dcrn2,dcrn1):
    obj.operands = [env.DCREG(dcrn2+(dcrn1<<5)),env.GPR[RS]]
    obj.type = type_data_processing

@ispec("32<[ 011111 RT(5) sprn2(5) sprn1(5) 0101010011 - ]", mnemonic="mfspr")
def ppc_mfspr(obj,RT,sprn2,sprn1):
    obj.operands = [env.GPR[RT],env.SPREG(sprn2+(sprn1<<5))]
    obj.type = type_data_processing

@ispec("32<[ 011111 RS(5) sprn2(5) sprn1(5) 0111010011 - ]", mnemonic="mtspr")
def ppc_mtspr(obj,RS,sprn2,sprn1):
    obj.operands = [env.SPREG(sprn2+(sprn1<<5)),env.GPR[RS]]
    obj.type = type_data_processing

@ispec("32<[ 011111 RS(5) - FXM(8) - 0010010000 - ]", mnemonic="mfspr")
def ppc_mtcrf(obj,RS,FXM):
    obj.operands = [env.cst(FXM,8),env.GPR[RS]]
    obj.type = type_data_processing

@ispec("32<[ 001011 BF(3) - L rA(5) SI(16) ]", mnemonic="cmpi")
def ppc_cmpi(obj,BF,L,rA,SI):
    if obj.mnemonic == "cmpi":
        imm = env.cst(SI,16).signextend(32)
    else:
        imm = env.cst(SI,16).zeroextend(32)
    obj.operands = [BF,L,env.GPR[rA],imm]
    obj.type = type_data_processing

@ispec("32<[ 011111 rS(5) rA(5) ----- 0000 0 11010 .Rc ]", mnemonic="cntlzw")
@ispec("32<[ 011111 rS(5) rA(5) ----- 0000 1 11010 .Rc ]", mnemonic="cntlzd")
@ispec("32<[ 011111 rS(5) rA(5) ----- 1110 1 11010 .Rc ]", mnemonic="extsb")
@ispec("32<[ 011111 rS(5) rA(5) ----- 1110 0 11010 .Rc ]", mnemonic="extsh")
@ispec("32<[ 011111 rS(5) rA(5) ----- 1111 0 11010 .Rc ]", mnemonic="extsw")
def ppc_Rc(obj,rS,rA):
    if obj.mnemonic=="cntlzd" and obj.Rc==1:
        raise InstructionError(obj)
    obj.operands = [env.GPR[rA],env.GPR[rS]]
    obj.type = type_data_processing

@ispec("32<[ 010011 BT(5) BA(5) BB(5) 0100000001 - ]", mnemonic="crand")
@ispec("32<[ 010011 BT(5) BA(5) BB(5) 0010000001 - ]", mnemonic="crandc")
@ispec("32<[ 010011 BT(5) BA(5) BB(5) 0100100001 - ]", mnemonic="creqv")
@ispec("32<[ 010011 BT(5) BA(5) BB(5) 0011100001 - ]", mnemonic="crnand")
@ispec("32<[ 010011 BT(5) BA(5) BB(5) 0000100001 - ]", mnemonic="crnor")
@ispec("32<[ 010011 BT(5) BA(5) BB(5) 0111000001 - ]", mnemonic="cror")
@ispec("32<[ 010011 BT(5) BA(5) BB(5) 0110100001 - ]", mnemonic="crorc")
@ispec("32<[ 010011 BT(5) BA(5) BB(5) 0011000001 - ]", mnemonic="crxor")
def ppc_cr(obj,BT,BA,BB):
    obj.operands = [env.CR[BT:BT+1], env.CR[BA:BA+1], env.CR[BB:BB+1]]
    obj.type = type_data_processing

@ispec("32<[ 011111 ----- rA(5) rB(5) 101111 0 110 - ]", mnemonic="dcba")
@ispec("32<[ 011111 ----- rA(5) rB(5) 101111 1 110 - ]", mnemonic="dcbae")
@ispec("32<[ 011111 ----- rA(5) rB(5) 000101 0 110 - ]", mnemonic="dcbf")
@ispec("32<[ 011111 ----- rA(5) rB(5) 000101 1 110 - ]", mnemonic="dcbfe")
@ispec("32<[ 011111 ----- rA(5) rB(5) 011101 0 110 - ]", mnemonic="dcbi")
@ispec("32<[ 011111 ----- rA(5) rB(5) 011101 1 110 - ]", mnemonic="dcbie")
@ispec("32<[ 011111 ----- rA(5) rB(5) 000011 0 110 - ]", mnemonic="dcbst")
@ispec("32<[ 011111 ----- rA(5) rB(5) 000011 1 110 - ]", mnemonic="dcbste")
@ispec("32<[ 011111 ----- rA(5) rB(5) 111111 0 110 - ]", mnemonic="dcbz")
@ispec("32<[ 011111 ----- rA(5) rB(5) 111111 1 110 - ]", mnemonic="dcbze")
@ispec("32<[ 011111 ----- rA(5) rB(5) 111101 0 110 - ]", mnemonic="icbi")
@ispec("32<[ 011111 ----- rA(5) rB(5) 111101 1 110 - ]", mnemonic="icbie")
def ppc_dc(obj,rA,rB):
    obj.operands = [env.GPR[rA],env.GPR[rB]]
    obj.type = type_data_processing

@ispec("32<[ 011111 CT(5) rA(5) rB(5) 010001 0 110- ]", mnemonic="dcbt")
@ispec("32<[ 011111 CT(5) rA(5) rB(5) 010001 1 110- ]", mnemonic="dcbte")
@ispec("32<[ 011111 CT(5) rA(5) rB(5) 001111 0 110- ]", mnemonic="dcbtst")
@ispec("32<[ 011111 CT(5) rA(5) rB(5) 001111 1 110- ]", mnemonic="dcbtste")
@ispec("32<[ 011111 CT(5) rA(5) rB(5) 000001 0 110- ]", mnemonic="icbt")
@ispec("32<[ 011111 CT(5) rA(5) rB(5) 000001 1 110- ]", mnemonic="icbte")
def ppc_dc2(obj,CT,rA,rB):
    obj.operands = [env.cst(CT,5),env.GPR[rA],env.GPR[rB]]
    obj.type = type_data_processing

@ispec("32<[ 010011 --------------- 0010010110 - ]", mnemonic="isync")
@ispec("32<[ 011111 --------------- 1001010110 - ]", mnemonic="msync")
@ispec("32<[ 010011 --------------- 0000110011 - ]", mnemonic="rfci")
@ispec("32<[ 010011 --------------- 0000110010 - ]", mnemonic="rfi")
@ispec("32<[ 010001 --------------- ---------1 - ]", mnemonic="sc")
@ispec("32<[ 011111 --------------- 1000110110 - ]", mnemonic="tlbsync")
def ppc_dc2(obj):
    obj.operands = []
    obj.type = type_other

@ispec("32<[ 011111 data(15) 1110110010 - ]", mnemonic="tlbre")
@ispec("32<[ 011111 data(15) 1111010010 - ]", mnemonic="tlbwe")
def ppc_dc2(obj,data):
    obj.tlb_data = env.cst(data,15)
    obj.operands = []
    obj.type = type_other

@ispec("32<[ 011111 ----- rA(5) rB(5) 1110010010 - ]", mnemonic="tlbsx")
@ispec("32<[ 011111 ----- rA(5) rB(5) 1110010011 - ]", mnemonic="tlbsxe")
def ppc_tlb(obj,rA,rB):
    if rA==0:
        addr = env.cst(0,32)
    else:
        addr = env.GPR[rA]
    obj.operands = [addr,env.GPR[rB]]
    obj.type = type_other

@ispec("32<[ 011111 MO(5) ---------- 1101010110 - ]", mnemonic="mbar")
def ppc_dc2(obj,MO):
    obj.operands = [env.cst(MO,5)]
    obj.type = type_other

@ispec("32<[ 011111 RS(5) ----- ----- 0010000011 - ]", mnemonic="wrtee")
def ppc_dc2(obj,RS):
    obj.operands = [env.GPR[RS][31:32]]
    obj.type = type_system

@ispec("32<[ 011111 ----- ----- E---- 0010100011 - ]", mnemonic="wrteei")
def ppc_dc2(obj,E):
    obj.operands = [env.cst(E,1)]
    obj.type = type_system

