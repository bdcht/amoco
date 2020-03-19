# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.arch.eBPF import env

from amoco.arch.core import *

# -------------------------------------------------------
# instruction eBPF decoders
# refs:
#  + www.kernel.org/doc/Documentation/networking/filter.txt
#  + linux/v4.11.3/source/kernel/bpf/*
# -------------------------------------------------------

ISPECS = []

# ALU_32 instructions:
@ispec("64>[ 001 s 0000 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="add")
@ispec("64>[ 001 s 1000 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="sub")
@ispec("64>[ 001 s 0100 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="mul")
@ispec("64>[ 001 s 1100 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="div")
@ispec("64>[ 001 s 0010 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="or")
@ispec("64>[ 001 s 1010 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="and")
@ispec("64>[ 001 s 0110 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="lsh")
@ispec("64>[ 001 s 1110 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="rsh")
@ispec("64>[ 001 s 0001 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="neg")
@ispec("64>[ 001 s 1001 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="mod")
@ispec("64>[ 001 s 0101 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="xor")
@ispec("64>[ 001 s 1101 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="mov")
@ispec("64>[ 001 s 0011 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="arsh")
@ispec("64>[ 001 s 1011 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="end")
def ebpf_alu_(obj, s, dreg, sreg, off, imm):
    dst = env.E[dreg]
    src = env.cst(imm.int(-1), 32) if s == 0 else env.E[sreg]
    src.sf = True
    if obj.mnemonic in ("or", "and", "xor", "neg", "end"):
        src.sf = False
    obj.operands = [dst, src]
    obj.type = type_data_processing


# ALU_64 instructions:
@ispec("64>[ 111 s 0000 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="add")
@ispec("64>[ 111 s 1000 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="sub")
@ispec("64>[ 111 s 0100 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="mul")
@ispec("64>[ 111 s 1100 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="div")
@ispec("64>[ 111 s 0010 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="or")
@ispec("64>[ 111 s 1010 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="and")
@ispec("64>[ 111 s 0110 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="lsh")
@ispec("64>[ 111 s 1110 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="rsh")
@ispec("64>[ 111 s 0001 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="neg")
@ispec("64>[ 111 s 1001 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="mod")
@ispec("64>[ 111 s 0101 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="xor")
@ispec("64>[ 111 s 1101 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="mov")
@ispec("64>[ 111 s 0011 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="arsh")
@ispec("64>[ 111 s 1011 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="end")
def ebpf_alu_(obj, s, dreg, sreg, off, imm):
    dst = env.R[dreg]
    src = env.cst(imm.int(-1), 32).zeroextend(64) if s == 0 else env.R[sreg]
    src.sf = True
    if obj.mnemonic in ("or", "and", "xor", "neg", "end"):
        src.sf = False
    obj.operands = [dst, src]
    obj.type = type_data_processing


@ispec("64>[ 101 s 0000 dreg(4) sreg(4) ~off(16) ~imm(32) ]", mnemonic="ja")
@ispec("64>[ 101 s 1000 dreg(4) sreg(4) ~off(16) ~imm(32) ]", mnemonic="jeq")
@ispec("64>[ 101 s 0100 dreg(4) sreg(4) ~off(16) ~imm(32) ]", mnemonic="jgt")
@ispec("64>[ 101 s 1100 dreg(4) sreg(4) ~off(16) ~imm(32) ]", mnemonic="jge")
@ispec("64>[ 101 s 0010 dreg(4) sreg(4) ~off(16) ~imm(32) ]", mnemonic="jset")
@ispec("64>[ 101 s 1010 dreg(4) sreg(4) ~off(16) ~imm(32) ]", mnemonic="jne")
@ispec("64>[ 101 s 0110 dreg(4) sreg(4) ~off(16) ~imm(32) ]", mnemonic="jsgt")
@ispec("64>[ 101 s 1110 dreg(4) sreg(4) ~off(16) ~imm(32) ]", mnemonic="jsge")
def ebpf_jmp_(obj, s, dreg, sreg, off, imm):
    dst = env.R[dreg]
    src = env.cst(imm.int(-1), 64) if s == 0 else env.R[sreg]
    offset = env.cst(off.int(-1), 64)
    obj.operands = [dst, src, offset]
    obj.type = type_control_flow


@ispec("64>[ 101 s 0001 dreg(4) sreg(4) ~off(16) imm(32) ]", mnemonic="call")
def ebpf_call_(obj, s, dreg, sreg, off, imm):
    obj.operands = [env.cst(imm, 32)]
    obj.type = type_other


@ispec("64>[ 101 s 1001 dreg(4) sreg(4) ~off(16) imm(32) ]", mnemonic="exit")
def ebpf_exit_(obj, s, dreg, sreg, off, imm):
    obj.operands = []
    obj.type = type_control_flow


# MEM LOAD from reg instructions:
@ispec("64>[ 100 sz(2) 110 dreg(4) sreg(4) ~off(16) imm(32) ]", mnemonic="ldx")
def ebpf_ldx_(obj, sz, dreg, sreg, off, imm):
    size = {0: 32, 1: 16, 2: 8, 3: 64}[sz]
    if imm != 0:
        raise InstructionError(obj)
    dst = env.R[dreg]
    src = env.R[sreg]
    src = env.mem(src + off.int(-1), size)
    obj.operands = [dst, src]
    obj.mnemonic += {8: "b", 16: "h", 32: "w", 64: "dw"}[size]
    obj.type = type_data_processing


# MEM STORE immediate or reg instructions:
@ispec("64>[ 010 sz(2) 110 dreg(4) sreg(4) ~off(16) ~imm(32) ]", mnemonic="st")
@ispec("64>[ 110 sz(2) 110 dreg(4) sreg(4) ~off(16) ~imm(32) ]", mnemonic="stx")
def ebpf_st_(obj, sz, dreg, sreg, off, imm):
    size = {0: 32, 1: 16, 2: 8, 3: 64}[sz]
    dst = env.mem(env.R[dreg] + off.int(-1), size)
    if obj.mnemonic == "stx":
        src = env.R[sreg]
        if imm != 0:
            raise InstructionError(obj)
    else:
        src = env.cst(imm.int(-1), 32).zeroextend(64)
    src = src[0:size]
    obj.operands = [dst, src]
    obj.mnemonic += {8: "b", 16: "h", 32: "w", 64: "dw"}[size]
    obj.type = type_data_processing


# XADD instructions:
@ispec("64>[ 110 sz(2) 011 dreg(4) sreg(4) ~off(16) imm(32) ]", mnemonic="xadd")
def ebpf_xadd_(obj, sz, dreg, sreg, off, imm):
    size = {0: 32, 1: 16, 2: 8, 3: 64}[sz]
    if (size < 32) or imm != 0:
        raise InstructionError(obj)
    dst = env.mem(env.R[dreg] + off.int(-1), size)
    src = env.R[sreg][0:size]
    obj.operands = [dst, src]
    obj.mnemonic += {8: "b", 16: "h", 32: "w", 64: "dw"}[size]
    obj.type = type_data_processing


# IMM LOAD instructions
@ispec(
    "128>[ 000 11 000 dreg(4) sreg(4) off(16) imm(32) unused(32) imm2(32) ]",
    mnemonic="lddw",
)
def ebpf_ld64_(obj, dreg, sreg, off, imm, unused, imm2):
    dst = env.R[dreg]
    src = env.cst(imm | (imm2 << 32), 64)
    obj.operands = [dst, src]
    obj.type = type_data_processing


# ABS/IND LOAD instructions:
@ispec(
    "64>[ 000 sz(2) 100 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="ld", _abs=True
)
@ispec(
    "64>[ 000 sz(2) 010 dreg(4) sreg(4) off(16) ~imm(32) ]", mnemonic="ld", _abs=False
)
def ebpf_ld_(obj, sz, dreg, sreg, off, imm, _abs):
    size = {0: 32, 1: 16, 2: 8, 3: 64}[sz]
    dst = env.R[0]
    adr = env.reg("#skb", 64)
    if not _abs:
        adr += env.R[sreg]
    src = env.mem(adr, size, disp=imm.int(-1))
    obj.operands = [dst, src]
    obj.mnemonic += {8: "b", 16: "h", 32: "w", 64: "dw"}[size]
    obj.type = type_data_processing
