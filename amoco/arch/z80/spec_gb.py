# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2012 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.logger import *
logger = Log(__name__)

from amoco.arch.core import *
from amoco.arch.z80 import env

# modifications of spec_mostek.ISPECS according to GB specs...
# (all DD/FD prefixed spec are removed IX/IY

# remove unused registers:
del env.ix,env.iy
del env.ir
del env.i, env.r
del env.ixh,env.ixl
del env.iyh,env.iyl

# remove unused flags & conditions:
del env.pf
del env.xf
del env.yf
del env.sf

del env.CONDITION[0b100]
del env.CONDITION[0b101]
del env.CONDITION[0b110]
del env.CONDITION[0b111]

# update flags:
env.cf.pos = 4
env.hf.pos = 5
env.nf.pos = 6
env.zf.pos = 7

# Prefixes are removed (obj.misc['pfx'] is always None)
# simplified getreg8/getreg16

def getreg8(obj,x):
    r = env.reg8[x]
    return r

def getreg16(obj,x):
    if x==0b11 and obj.mnemonic not in ('PUSH','POP'):
        r = env.sp
    else:
        r = env.reg16[x]
    return r

ISPECS = []

# ----------------
# 8-bit load group
# ----------------

# LD r,r'
@ispec("8<[ 01 rd(3) rs(3) ]", mnemonic='LD')
def mostek_ld(obj,rd,rs):
    dst,src = getreg8(obj,rd),getreg8(obj,rs)
    if dst._is_mem or src._is_mem:
        if rd==rs or (obj.misc['pfx'] is not None):
            raise InstructionError(obj)
    obj.operands = [dst,src]
    obj.type = type_data_processing

# LD r,n
@ispec("16<[ n(8) 00 r(3) 110 ]", mnemonic='LD')
def mostek_ld(obj,r,n):
    dst = getreg8(obj,r)
    if r==0b110 and obj.misc['pfx'] is not None:
        raise InstructionError(obj)
    obj.operands = [dst,env.cst(n,8)]
    obj.type = type_data_processing

# LD (BC/DE), A
@ispec("8<[ 000 b rev 010 ]", mnemonic='LD')
def mostek_ld(obj,b,rev):
    base = env.reg16[b]
    obj.operands = [env.mem(base,8), env.a]
    if rev: obj.operands.reverse()
    obj.type = type_data_processing

# LDD/LDI a,(hl) 
@ispec("8<[ {3a} ]", mnemonic='LDD')
@ispec("8<[ {2a} ]", mnemonic='LDI')
def mostek_ld(obj):
    obj.operands = [env.a, env.reg8[0b110]]
    obj.type = type_data_processing

@ispec("8<[ {32} ]", mnemonic='LDD')
@ispec("8<[ {22} ]", mnemonic='LDI')
def mostek_ld(obj):
    obj.operands = [env.reg8[0b110], env.a]
    obj.type = type_data_processing

@ispec("8<[ {f2} ]", mnemonic='LD')
def mostek_ld(obj):
    base = env.composer([env.c, env.cst(0xff,8)])
    obj.operands = [env.a, env.mem(base,8)]
    obj.type = type_data_processing

@ispec("8<[ {e2} ]", mnemonic='LD')
def mostek_ld(obj):
    base = env.composer([env.c, env.cst(0xff,8)])
    obj.operands = [env.mem(base,8), env.a]
    obj.type = type_data_processing

@ispec("16<[ n(8) {f0} ]", mnemonic='LD')
def mostek_ld(obj,n):
    base = env.cst(0xff00,16)+n
    obj.operands = [env.a, env.mem(base,8)]
    obj.type = type_data_processing

@ispec("16<[ n(8) {e0} ]", mnemonic='LD')
def mostek_ld(obj,n):
    base = env.cst(0xff00,16)+n
    obj.operands = [env.mem(base,8), env.a]
    obj.type = type_data_processing

@ispec("24<[ n(16) {fa} ]", mnemonic='LD')
def mostek_ld(obj,n):
    base = env.cst(n,16)
    obj.operands = [env.a, env.mem(base,8)]
    obj.type = type_data_processing

@ispec("24<[ n(16) {ea} ]", mnemonic='LD')
def mostek_ld(obj,n):
    base = env.cst(n,16)
    obj.operands = [env.mem(base,8), env.a]
    obj.type = type_data_processing

# -----------------
# 16-bit load group
# -----------------

# LD dd,nn
@ispec("24<[ nn(16) 00 dd(2) 0001 ]", mnemonic='LD')
def mostek_ld(obj,dd,nn):
    dst = getreg16(obj,dd)
    obj.operands = [dst,env.cst(nn,16)]
    obj.type = type_data_processing

# LD hl,(nn) / LD (nn), hl
@ispec("24<[ nn(16) 00 10 rev 010 ]", mnemonic='LD')
def mostek_ld(obj,rev,nn):
    dst = getreg16(obj,0b10)
    obj.operands = [dst,env.mem(env.cst(nn,16),16)]
    if not rev: obj.operands.reverse()
    obj.type = type_data_processing

# LD SP,HL
@ispec("8<[ 1111 1001 ]", mnemonic='LD')
def mostek_ld(obj):
    dst = getreg16(obj,0b10)
    obj.operands = [env.sp,dst]
    obj.type = type_data_processing

# PUSH qq
@ispec("8<[ 11 qq(2) 0101 ]", mnemonic='PUSH')
@ispec("8<[ 11 qq(2) 0001 ]", mnemonic='POP')
def mostek_ld(obj,qq):
    src = getreg16(obj,qq)
    if src==env.sp: src=env.af
    obj.operands = [src]
    obj.type = type_data_processing

# LDHL SP,n
@ispec("16<[ n(8) {f8} ]", mnemonic='LDHL')
def mostek_ld(obj,n):
    disp = env.cst(n,8).signextend(16)
    obj.operands = [env.sp, disp]
    obj.type = type_data_processing

# LD (nn), SP
@ispec("24<[ nn(16) {08} ]", mnemonic='LD')
def mostek_ld(obj,nn):
    obj.operands = [env.mem(env.cst(nn,16),16), env.sp]
    obj.type = type_data_processing

# ----------------------
# 8-bit Arithmetic Group
# ----------------------

# ADD a,r
@ispec("8<[ 1000 0 r(3) ]", mnemonic='ADD')
@ispec("8<[ 1000 1 r(3) ]", mnemonic='ADC')
@ispec("8<[ 1001 0 r(3) ]", mnemonic='SUB')
@ispec("8<[ 1001 1 r(3) ]", mnemonic='SBC')
@ispec("8<[ 1010 0 r(3) ]", mnemonic='AND')
@ispec("8<[ 1011 0 r(3) ]", mnemonic='OR')
@ispec("8<[ 1010 1 r(3) ]", mnemonic='XOR')
@ispec("8<[ 1011 1 r(3) ]", mnemonic='CP')
@ispec("8<[ 00 r(3) 100 ]", mnemonic='INC')
@ispec("8<[ 00 r(3) 101 ]", mnemonic='DEC')
def mostek_arithmetic(obj,r):
    if r==0b110 and obj.misc['pfx'] is not None:
        raise InstructionError(obj)
    src = getreg8(obj,r)
    obj.operands = [env.a,src]
    if obj.mnemonic in ('INC','DEC'): obj.operands.pop(0)
    obj.type = type_data_processing

@ispec("16<[ n(8) 1100 0110 ]", mnemonic='ADD')
@ispec("16<[ n(8) 1100 1110 ]", mnemonic='ADC')
@ispec("16<[ n(8) 1101 0110 ]", mnemonic='SUB')
@ispec("16<[ n(8) 1101 1110 ]", mnemonic='SBC')
@ispec("16<[ n(8) 1110 0110 ]", mnemonic='AND')
@ispec("16<[ n(8) 1111 0110 ]", mnemonic='OR')
@ispec("16<[ n(8) 1110 1110 ]", mnemonic='XOR')
@ispec("16<[ n(8) 1111 1110 ]", mnemonic='CP')
def mostek_arithmetic(obj,n):
    obj.operands = [env.a,env.cst(n,8)]
    obj.type = type_data_processing

# ADD SP,n
@ispec("16<[ n(8) {e8} ]", mnemonic='ADD')
def mostek_ld(obj,n):
    disp = env.cst(n,8).signextend(16)
    obj.operands = [env.sp, disp]
    obj.type = type_data_processing

# ------------------------------------------------
# General Purpose Arithmetic and CPU Control Group
# ------------------------------------------------

@ispec("8<[ {76} ]", mnemonic='HALT')
@ispec("8<[ {f3} ]", mnemonic='DI')
@ispec("8<[ {fb} ]", mnemonic='EI')
@ispec("8<[ {10} ]", mnemonic='STOP')
def mostek_gpa_cpuc(obj):
    obj.operands = []
    obj.type = type_cpu_state

@ispec("8<[ {27} ]", mnemonic='DAA')
@ispec("8<[ {2f} ]", mnemonic='CPL')
@ispec("8<[ {3f} ]", mnemonic='CCF')
@ispec("8<[ {37} ]", mnemonic='SCF')
@ispec("8<[ {00} ]", mnemonic='NOP')
def mostek_arithmetic(obj):
    obj.operands = []
    obj.type = type_data_processing

@ispec("8<[ {d9} ]", mnemonic='RETI')
def mostek_arithmetic(obj):
    obj.operands = []
    obj.type = type_control_flow

# -----------------------
# 16-bit Arithmetic Group
# -----------------------

@ispec(" 8<[ 00 ss(2) 1001 ]", mnemonic='ADD')
@ispec(" 8<[ 00 ss(2) 0011 ]", mnemonic='INC')
@ispec(" 8<[ 00 ss(2) 1011 ]", mnemonic='DEC')
def mostek_arithmetic(obj,ss):
    dst = getreg16(obj,0b10) #hl (or ix/iy)
    src = getreg16(obj,ss)
    obj.operands = [dst,src]
    if obj.mnemonic in ('INC','DEC'): obj.operands.pop(0)
    obj.type = type_data_processing

@ispec("16<[ n(8) 1100 0110 ]", mnemonic='ADD')
@ispec("16<[ n(8) 1100 1110 ]", mnemonic='ADC')
@ispec("16<[ n(8) 1101 0110 ]", mnemonic='SUB')
@ispec("16<[ n(8) 1101 1110 ]", mnemonic='SBC')
@ispec("16<[ n(8) 1110 0110 ]", mnemonic='AND')
@ispec("16<[ n(8) 1111 0110 ]", mnemonic='OR')
@ispec("16<[ n(8) 1110 1110 ]", mnemonic='XOR')
@ispec("16<[ n(8) 1111 1110 ]", mnemonic='CP')
def mostek_arithmetic(obj,n):
    # DD/FD prefix are ignored
    obj.operands = [env.a,env.cst(n,8)]
    obj.type = type_data_processing

# ----------------------
# Rotate and Shift Group
# ----------------------

@ispec("8<[ {07} ]", mnemonic='RLCA')
@ispec("8<[ {17} ]", mnemonic='RLA')
@ispec("8<[ {0f} ]", mnemonic='RRCA')
@ispec("8<[ {1f} ]", mnemonic='RRA')
def mostek_rotshift(obj):
    obj.operands = []
    obj.type = type_data_processing

@ispec("16<[ 00000 r(3) {cb} ]", mnemonic='RLC')
@ispec("16<[ 00010 r(3) {cb} ]", mnemonic='RL')
@ispec("16<[ 00001 r(3) {cb} ]", mnemonic='RRC')
@ispec("16<[ 00011 r(3) {cb} ]", mnemonic='RR')
@ispec("16<[ 00100 r(3) {cb} ]", mnemonic='SLA')
@ispec("16<[ 00110 r(3) {cb} ]", mnemonic='SWAP') #undocumented
@ispec("16<[ 00101 r(3) {cb} ]", mnemonic='SRA')
@ispec("16<[ 00111 r(3) {cb} ]", mnemonic='SRL')
def mostek_rotshift(obj,r):
    if obj.misc['pfx'] is not None:
        raise InstructionError(obj)
    op1 = getreg8(obj,r)
    obj.operands = [op1]
    obj.type = type_data_processing

# -----------------------------
# Bit Set, Reset and Test Group
# -----------------------------

# unprefixed BIT & SET:
@ispec("16<[ 01 b(3) r(3) {cb} ]", mnemonic='BIT')
@ispec("16<[ 11 b(3) r(3) {cb} ]", mnemonic='SET')
def mostek_bitset(obj,b,r):
    if obj.misc['pfx'] is not None:
        raise InstructionError(obj)
    op1 = env.cst(b,3)
    op2 = getreg8(obj,r)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# ----------
# Jump Group
# ----------

@ispec("24<[ nn(16) 11 000 011 ]", mnemonic='JP')
def mostek_jump(obj,nn):
    obj.operands = [env.cst(nn,16)]
    obj.type = type_control_flow

@ispec("24<[ nn(16) 11 cc(3) 010 ]", mnemonic='JPcc')
def mostek_jump(obj,cc,nn):
    if cc>=0b100: raise InstructionError(obj)
    obj.cond = env.CONDITION[cc]
    obj.operands = [obj.cond[0],env.cst(nn,16)]
    obj.type = type_control_flow

@ispec("16<[ e(8) {18} ]", mnemonic='JR')
@ispec("16<[ e(8) {10} ]", mnemonic='DJNZ')
@ispec("16<[ e(8) {38} ]", mnemonic='JRcc', cond=('c',env.cf==1))
@ispec("16<[ e(8) {30} ]", mnemonic='JRcc', cond=('nc',env.cf==0))
@ispec("16<[ e(8) {28} ]", mnemonic='JRcc', cond=('z',env.zf==1))
@ispec("16<[ e(8) {20} ]", mnemonic='JRcc', cond=('nz',env.zf==0))
def mostek_jump(obj,e):
    disp = env.cst(e,8).signextend(16)
    obj.operands = [disp]
    if hasattr(obj,'cond'):
        obj.operands.insert(0,obj.cond[0])
    obj.type = type_control_flow

@ispec("8<[ {e9} ]", mnemonic='JP')
def mostek_jump(obj):
    r = getreg16(obj,0b10)
    # is it mem(r,16) ??
    obj.operands = [r]
    obj.type = type_control_flow

# ---------------------
# Call and Return Group
# ---------------------

@ispec("24<[ nn(16) 1100 1101 ]", mnemonic='CALL')
def mostek_call(obj,nn):
    obj.operands = [env.cst(nn,16)]
    obj.type = type_control_flow

@ispec("24<[ nn(16) 11 cc(3) 100 ]", mnemonic='CALLcc')
def mostek_call(obj,cc,nn):
    if cc>=0b100: raise InstructionError(obj)
    obj.cond = env.CONDITION[cc]
    obj.operands = [obj.cond[0],env.cst(nn,16)]
    obj.type = type_control_flow

@ispec("8<[ {c9} ]", mnemonic='RET')
def mostek_ret(obj):
    obj.operands = []
    obj.type = type_control_flow

@ispec("8<[ 11 cc(3) 000 ]", mnemonic='RETcc')
def mostek_ret(obj,cc):
    if cc>=0b100: raise InstructionError(obj)
    obj.cond = env.CONDITION[cc]
    obj.operands = [obj.cond[0]]
    obj.type = type_control_flow

@ispec("8<[ 11 t(3) 111 ]", mnemonic='RST')
def mostek_rst(obj,t):
    p = (0x00, 0x08, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38)[t]
    obj.operands = [env.cst(p,8)]
    obj.type = type_control_flow

