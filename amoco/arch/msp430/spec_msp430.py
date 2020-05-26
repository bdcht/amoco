# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# ref: MSP430x1xx User's Guide.
# 27 basic instructions, all encoded in 16/32 bits.

from amoco.arch.msp430 import env

from amoco.arch.core import *

# -------------------------------------------------------
# instruction MSP430 decoders
# -------------------------------------------------------

# get operand type/value based on addressing mode:
def getopd(obj, mode, reg, data, CGR=False):
    r = env.R[reg]
    if obj.BW:
        size = 8
    else:
        size = 16
    if CGR:
        if reg == 2:
            r = [r, env.cst(0, 16), env.cst(0x4, 16), env.cst(0x8, 16)][mode]
        elif reg == 3:
            r = env.cst([0, 1, 2, -1][mode], 16)
    if mode == 0:  # register mode
        return r[0:size], data
    if mode == 1:  # indexed/symbolic/absolute modes
        addr, data = data[0:16], data[16:]
        imm = env.cst(addr.int(-1), 16)
        obj.bytes += pack(addr)
        if r is env.sr:
            imm.sf = False
            return env.mem(imm, size), data
        if r is env.pc:
            return env.mem(env.pc + imm, size), data
        if r._is_cst:
            imm.sf = False
        return env.mem(r + imm, size), data
    if mode == 2:  # indirect register mode
        if r._is_cst:
            return r[0:size], data
        return env.mem(r, size), data
    if mode == 3:  # immediate & indirect autoincrement
        if r._is_cst:
            return r[0:size], data
        if r is env.pc:
            addr, data = data[0:16], data[16:]
            imm = env.cst(addr.int(), 16)
            obj.bytes += pack(addr)
            return imm[0:size], data
        else:
            obj.misc["autoinc"] = r
            return env.mem(r, size), data


ISPECS = []

# double-operand format
# ----------------------


@ispec("*<[ ~data(*) 0100 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="MOV")
@ispec("*<[ ~data(*) 0101 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="ADD")
@ispec("*<[ ~data(*) 0110 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="ADDC")
@ispec("*<[ ~data(*) 0111 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="SUBC")
@ispec("*<[ ~data(*) 1000 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="SUB")
@ispec("*<[ ~data(*) 1001 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="CMP")
@ispec("*<[ ~data(*) 1010 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="DADD")
@ispec("*<[ ~data(*) 1011 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="BIT")
@ispec("*<[ ~data(*) 1100 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="BIC")
@ispec("*<[ ~data(*) 1101 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="BIS")
@ispec("*<[ ~data(*) 1110 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="XOR")
@ispec("*<[ ~data(*) 1111 Sreg(4) Ad(1) .BW(1) As(2) Dreg(4) ]", mnemonic="AND")
def msp430_doubleop(obj, data, Sreg, Ad, As, Dreg):
    src, data = getopd(obj, As, Sreg, data, CGR=True)
    dst, data = getopd(obj, Ad, Dreg, data)
    obj.operands = [src, dst]
    if dst is env.pc:
        obj.type = type_control_flow
    else:
        obj.type = type_data_processing


# single-operand format
# ----------------------


@ispec("*<[ ~data(*) 0001 00 000 .BW(1) Ad(2) DSreg(4) ]", mnemonic="RRC")
@ispec("*<[ ~data(*) 0001 00 001 .BW(1) Ad(2) DSreg(4) ]", mnemonic="SWPB")
@ispec("*<[ ~data(*) 0001 00 010 .BW(1) Ad(2) DSreg(4) ]", mnemonic="RRA")
@ispec("*<[ ~data(*) 0001 00 011 .BW(1) Ad(2) DSreg(4) ]", mnemonic="SXT")
@ispec("*<[ ~data(*) 0001 00 100 .BW(1) Ad(2) DSreg(4) ]", mnemonic="PUSH")
def msp430_singleop(obj, data, Ad, DSreg):
    opd, data = getopd(obj, Ad, DSreg, data)
    obj.operands = [opd]
    obj.type = type_data_processing


@ispec("*<[ ~data(*) 0001 00 101 .BW(1) Ad(2) DSreg(4) ]", mnemonic="CALL")
@ispec("*<[ ~data(*) 0001 00 110 .BW(1) Ad(2) DSreg(4) ]", mnemonic="RETI")
def msp430_singleop(obj, data, Ad, DSreg):
    opd, data = getopd(obj, Ad, DSreg, data)
    obj.operands = [opd]
    obj.type = type_control_flow


# conditional-jump format
# ------------------------


@ispec("16<[ 001 .cond(3) offset(10) ]", mnemonic="Jcc", BW=0)
def msp430_jumps(obj, offset):
    if obj.cond == 0b111:
        obj.mnemonic = "JMP"
    off = env.cst(offset * 2, 11).signextend(16)
    obj.operands = [off]
    obj.type = type_control_flow

@ispec("16<[ 001 111 offset(10) ]", mnemonic="JMP", BW=0)
def msp430_jumps(obj, offset):
    obj.cond = 0b111
    off = env.cst(offset * 2, 11).signextend(16)
    obj.operands = [off]
    obj.type = type_control_flow
