# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.arch.eBPF import env

from amoco.arch.core import *

# -------------------------------------------------------
# instruction BPF decoders
# refs:
#  + www.kernel.org/doc/Documentation/networking/filter.txt
#  + linux/v4.11.3/source/kernel/bpf/*
# -------------------------------------------------------

ISPECS = []

# BPF_ALU (0x4) instructions:
@ispec("64>[ 001 s 0000 {00} jt(8) jf(8) ~k(32) ]", mnemonic="add")
@ispec("64>[ 001 s 1000 {00} jt(8) jf(8) ~k(32) ]", mnemonic="sub")
@ispec("64>[ 001 s 0100 {00} jt(8) jf(8) ~k(32) ]", mnemonic="mul")
@ispec("64>[ 001 s 1100 {00} jt(8) jf(8) ~k(32) ]", mnemonic="div")
@ispec("64>[ 001 s 0010 {00} jt(8) jf(8) ~k(32) ]", mnemonic="or")
@ispec("64>[ 001 s 1010 {00} jt(8) jf(8) ~k(32) ]", mnemonic="and")
@ispec("64>[ 001 s 0110 {00} jt(8) jf(8) ~k(32) ]", mnemonic="lsh")
@ispec("64>[ 001 s 1110 {00} jt(8) jf(8) ~k(32) ]", mnemonic="rsh")
@ispec("64>[ 001 s 0001 {00} jt(8) jf(8) ~k(32) ]", mnemonic="neg")
@ispec("64>[ 001 s 1001 {00} jt(8) jf(8) ~k(32) ]", mnemonic="mod")
@ispec("64>[ 001 s 0101 {00} jt(8) jf(8) ~k(32) ]", mnemonic="xor")
def bpf_alu_(obj, s, jt, jf, k):
    dst = env.A
    src = env.cst(k.int(-1), 32) if s == 0 else env.X
    src.sf = True
    if obj.mnemonic in ("or", "and", "xor", "neg"):
        src.sf = False
    obj.operands = [dst, src]
    obj.type = type_data_processing


# BPF_JMP (0x5) instructions:
@ispec("64>[ 101 s 0000 {00} ~jt(8) ~jf(8) ~k(32) ]", mnemonic="ja")
@ispec("64>[ 101 s 1000 {00} ~jt(8) ~jf(8) ~k(32) ]", mnemonic="jeq")
@ispec("64>[ 101 s 0100 {00} ~jt(8) ~jf(8) ~k(32) ]", mnemonic="jgt")
@ispec("64>[ 101 s 1100 {00} ~jt(8) ~jf(8) ~k(32) ]", mnemonic="jge")
@ispec("64>[ 101 s 0010 {00} ~jt(8) ~jf(8) ~k(32) ]", mnemonic="jset")
def bpf_jmp_(obj, s, jt, jf, k):
    tst = env.cst(k.int(-1), 32)
    tst.sf = True
    offjt = env.cst(jt.int(-1), 64)
    offjf = env.cst(jf.int(-1), 64)
    obj.operands = [tst, offjt, offjf]
    obj.type = type_control_flow


# BPF_RET (0x6) instructions:
@ispec("64>[ 011 s(2) 000 {00} jt(8) jf(8) ~k(32) ]", mnemonic="ret")
def bpf_ret_(obj, s, jt, jf, k):
    src = (env.cst(k.int(-1), 32), env.X, env.A)[s]
    obj.operands = [src]
    obj.type = type_control_flow


# BPF_MISC (0x7) instructions:
@ispec("64>[ 111 s 0000 {00} jt(8) jf(8) ~k(32) ]", mnemonic="mov")
def bpf_mov_(obj, s, jt, jf, k):
    dst, src = (env.X, env.A) if s == 0 else (env.A, env.X)
    obj.operands = [dst, src]
    obj.type = type_data_processing


# BPF_LD (0x0) instructions:
@ispec("64>[ 000 00=sz(2) md(3) {00} jt(8) jf(8) ~k(32) ]", mnemonic="ldw")
@ispec("64>[ 000 01=sz(2) md(3) {00} jt(8) jf(8) ~k(32) ]", mnemonic="ldh")
@ispec("64>[ 000 10=sz(2) md(3) {00} jt(8) jf(8) ~k(32) ]", mnemonic="ldb")
def bpf_ld_(obj, sz, md, jt, jf, k):
    if sz == 3:
        raise InstructionError(obj)
    size = 32 >> sz
    dst = env.A
    adr = env.skb()
    if md == 0:  # IMM
        src = env.cst(k.int(-1), 32)
    elif md == 1:  # ABS
        src = env.mem(adr, size, disp=k.int(-1))
    elif md == 2:  # IND
        src = env.mem(adr + env.X + k.int(-1), size)
    elif md == 3 and k.int() < 16:  # MEM
        src = env.M[k.int()]
    elif md == 4:  # LEN
        src = env.skb("len")
    else:
        raise InstructionError(obj)
    obj.operands = [dst, src]
    obj.type = type_data_processing


# BPF_LDX (0x1) instructions:
@ispec("64>[ 100 sz(2) md(3) {00} jt(8) jf(8) ~k(32) ]", mnemonic="ld")
def bpf_ldx_(obj, sz, md, jt, jf, k):
    if sz == 3:
        raise InstructionError(obj)
    size = 32 >> sz
    dst = env.X
    adr = env.skb()
    if md == 0 and size == 32:  # IMM
        src = env.cst(k.int(-1), 32)
    elif md == 3 and size == 32 and k.int() < 16:  # MEM
        src = env.M[k.int()]
    elif md == 6 and size == 8:  # MSH
        src = env.mem(adr, size, disp=k.int(-1)) * 4
    else:
        raise InstructionError(obj)
    obj.operands = [dst, src]
    obj.type = type_data_processing


# BPF_ST(X) instructions:
@ispec("64>[ 010 sz(2) md(3) {00} jt(8) jf(8) ~k(32) ]", mnemonic="st")
@ispec("64>[ 110 sz(2) md(3) {00} jt(8) jf(8) ~k(32) ]", mnemonic="stx")
def bpf_ld_(obj, sz, md, jt, jf, k):
    dst = env.M[k.int()]
    if obj.mnemonic == "stx":
        src = env.X
        obj.mnemonic = "st"
    else:
        src = env.A
    obj.operands = [dst, src]
    obj.type = type_data_processing
