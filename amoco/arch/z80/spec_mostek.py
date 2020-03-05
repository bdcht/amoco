# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2012 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.logger import Log
logger = Log(__name__)

from amoco.arch.core import *
from amoco.arch.z80 import env

ISPECS = []

# ----------------
# DD/FD prefixes
# ----------------

@ispec("8[ {dd} ]+")
def mostek_prefix(obj):
    obj.misc['pfx'] = env.ix

@ispec("8[ {fd} ]+")
def mostek_prefix(obj):
    obj.misc['pfx'] = env.iy

def getreg8(obj,x):
    r = env.reg8[x]
    p = obj.misc['pfx']
    if p is not None:
        if x == 0b110:
            return env.mem(p,8)
        elif r == env.l:
            if p == env.ix:
                return env.ixl
            else:
                return env.iyl
        elif r == env.h:
            if p == env.ix:
                return env.ixh
            else:
                return env.iyh
    return r

def getreg16(obj,x):
    if x==0b11 and obj.mnemonic not in ('PUSH','POP'):
        r = env.sp
    else:
        r = env.reg16[x]
    p = obj.misc['pfx']
    if p is not None:
        if x == 0b10:
            return p
    return r

# note: ED is not considered as a consumable prefix,
# but as explicit first byte of ispecs.
# As a consequence, "unsafe mirrored instruction"
# are not supported.

# ----------------
# 8-bit load group
# ----------------

# LD r,r' except (ix/y+d) versions
@ispec("8<[ 01 rd(3) rs(3) ]", mnemonic='LD')
def mostek_ld(obj,rd,rs):
    dst,src = getreg8(obj,rd),getreg8(obj,rs)
    if dst._is_mem or src._is_mem:
        if rd==rs or (obj.misc['pfx'] is not None):
            raise InstructionError(obj)
    obj.operands = [dst,src]
    obj.type = type_data_processing

# DD/FD prefixed LD r,(ix/y+d)
@ispec("16<[ d(8) 01 rd(3) 110 ]", mnemonic='LD')
def mostek_ld(obj,d,rd):
    x = obj.misc['pfx']
    if rd==0b110 or x is None:
        raise InstructionError(obj)
    dst = env.reg8[rd]
    disp = env.cst(d,8).signextend(16)
    src = env.mem(x,8,disp=disp.value)
    obj.operands = [dst,src]
    obj.type = type_data_processing

# DD/FD prefixed LD (ix/y+d),r
@ispec("16<[ d(8) 01 110 rs(3) ]", mnemonic='LD')
def mostek_ld(obj,d,rs):
    x = obj.misc['pfx']
    if rs==0b110 or x is None:
        raise InstructionError(obj)
    src = env.reg8[rs]
    disp = env.cst(d,8).signextend(16)
    dst = env.mem(x,8,disp=disp.value)
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

# LD (I?+d), n
@ispec("24<[ n(8) d(8) {36} ]", mnemonic='LD')
def mostek_ld(obj,d,n):
    base = obj.misc['pfx']
    if base is None: raise InstructionError(obj)
    disp = env.cst(d,8).signextend(16)
    obj.operands = [env.mem(base,8,disp=disp.value),env.cst(n,8)]
    obj.type = type_data_processing

# LD (BC/DE), A
@ispec("8<[ 000 b rev 010 ]", mnemonic='LD')
def mostek_ld(obj,b,rev):
    base = env.reg16[b]
    obj.operands = [env.mem(base,8), env.a]
    if rev: obj.operands.reverse()
    obj.type = type_data_processing

# LD a,(nn)
@ispec("24<[ nn(16) 0011 rev 010 ]", mnemonic='LD')
def mostek_ld(obj,rev,nn):
    obj.operands = [env.mem(env.cst(nn,16),8), env.a]
    if rev: obj.operands.reverse()
    obj.type = type_data_processing

# LD i/r,a
@ispec("16<[ 010 rev r 111 {ed} ]", mnemonic='LD')
def mostek_ld(obj,rev,r):
    dst = env.i if r==0 else env.r
    obj.operands = [dst, env.a]
    if rev: obj.operands.reverse()
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

# LD hl,(nn)
@ispec("24<[ nn(16) 00 10 rev 010 ]", mnemonic='LD')
def mostek_ld(obj,rev,nn):
    dst = getreg16(obj,0b10)
    obj.operands = [dst,env.mem(env.cst(nn,16),16)]
    if not rev: obj.operands.reverse()
    obj.type = type_data_processing

# LD dd,(nn)
@ispec("32<[ nn(16) 01 dd(2) rev 011 {ed} ]", mnemonic='LD')
def mostek_ld(obj,dd,rev,nn):
    obj.operands = [getreg16(obj,dd),env.mem(env.cst(nn,16),16)]
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

# ------------------------------------------
# Exchange, Block Transfer, and Search Group
# ------------------------------------------

# EX de,hl
@ispec("8<[ {eb} ]", mnemonic='EX')
def mostek_ld(obj):
    # DD/FD prefix ignored
    obj.operands = [env.de, env.hl]
    obj.type = type_data_processing

# EX af,af'
@ispec("8<[ {08} ]", mnemonic='EX')
def mostek_ld(obj):
    # DD/FD prefix ignored
    obj.operands = [env.af, env.af_]
    obj.type = type_data_processing

@ispec("8<[ {d9} ]", mnemonic='EXX')
@ispec("16<[ {a0} {ed} ]", mnemonic='LDI')
@ispec("16<[ {b0} {ed} ]", mnemonic='LDIR')
@ispec("16<[ {a8} {ed} ]", mnemonic='LDD')
@ispec("16<[ {b8} {ed} ]", mnemonic='LDDR')
@ispec("16<[ {a1} {ed} ]", mnemonic='CPI')
@ispec("16<[ {b1} {ed} ]", mnemonic='CPIR')
@ispec("16<[ {a9} {ed} ]", mnemonic='CPD')
@ispec("16<[ {b9} {ed} ]", mnemonic='CPDR')
def mostek_ld(obj):
    # DD/FD prefix ignored
    obj.operands = []
    obj.type = type_data_processing

# EX (sp),hl/ix/iy
@ispec("8<[ {e3} ]", mnemonic='EX')
def mostek_ld(obj):
    src = getreg16(obj,0b10)
    obj.operands = [env.mem(env.sp,16),src]
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
    # DD/FD prefix are ignored
    obj.operands = [env.a,env.cst(n,8)]
    obj.type = type_data_processing

@ispec("16<[ d(8) 1000 0 110 ]", mnemonic='ADD')
@ispec("16<[ d(8) 1000 1 110 ]", mnemonic='ADC')
@ispec("16<[ d(8) 1001 0 110 ]", mnemonic='SUB')
@ispec("16<[ d(8) 1001 1 110 ]", mnemonic='SBC')
@ispec("16<[ d(8) 1010 0 110 ]", mnemonic='AND')
@ispec("16<[ d(8) 1011 0 110 ]", mnemonic='OR')
@ispec("16<[ d(8) 1010 1 110 ]", mnemonic='XOR')
@ispec("16<[ d(8) 1011 1 110 ]", mnemonic='CP')
@ispec("16<[ d(8) 00 110 100 ]", mnemonic='INC')
@ispec("16<[ d(8) 00 110 101 ]", mnemonic='DEC')
def mostek_arithmetic(obj,d):
    if obj.misc['pfx'] is None: raise InstructionError(obj)
    base = obj.misc['pfx']
    disp = env.cst(d,8).signextend(16)
    src = env.mem(base,8,disp=disp.value)
    obj.operands = [env.a,src]
    if obj.mnemonic in ('INC','DEC'): obj.operands.pop(0)
    obj.type = type_data_processing

# ------------------------------------------------
# General Purpose Arithmetic and CPU Control Group
# ------------------------------------------------

@ispec("8<[ {76} ]", mnemonic='HALT')
@ispec("8<[ {f3} ]", mnemonic='DI')
@ispec("8<[ {fb} ]", mnemonic='EI')
@ispec("16<[ {46} {ed} ]", mnemonic='IM0')
@ispec("16<[ {56} {ed} ]", mnemonic='IM1')
@ispec("16<[ {5e} {ed} ]", mnemonic='IM2')
def mostek_gpa_cpuc(obj):
    # DD/FD prefix are ignored
    obj.operands = []
    obj.type = type_cpu_state

@ispec("8<[ {27} ]", mnemonic='DAA')
@ispec("8<[ {2f} ]", mnemonic='CPL')
@ispec("16<[ {44} {ed} ]", mnemonic='NEG')
@ispec("8<[ {3f} ]", mnemonic='CCF')
@ispec("8<[ {37} ]", mnemonic='SCF')
@ispec("8<[ {00} ]", mnemonic='NOP')
def mostek_arithmetic(obj):
    # DD/FD prefix are ignored
    obj.operands = []
    obj.type = type_data_processing

# -----------------------
# 16-bit Arithmetic Group
# -----------------------

@ispec(" 8<[ 00 ss(2) 1001 ]", mnemonic='ADD')
@ispec(" 8<[ 00 ss(2) 0011 ]", mnemonic='INC')
@ispec(" 8<[ 00 ss(2) 1011 ]", mnemonic='DEC')
@ispec("16<[ 01 ss(2) 1010 {ed} ]", mnemonic='ADC')
@ispec("16<[ 01 ss(2) 0010 {ed} ]", mnemonic='SBC')
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
@ispec("16<[ {6f} {ed} ]", mnemonic='RLD')
@ispec("16<[ {67} {ed} ]", mnemonic='RRD')
def mostek_rotshift(obj):
    # DD/FD prefix are ignored
    obj.operands = []
    obj.type = type_data_processing

@ispec("16<[ 00000 r(3) {cb} ]", mnemonic='RLC')
@ispec("16<[ 00010 r(3) {cb} ]", mnemonic='RL')
@ispec("16<[ 00001 r(3) {cb} ]", mnemonic='RRC')
@ispec("16<[ 00011 r(3) {cb} ]", mnemonic='RR')
@ispec("16<[ 00100 r(3) {cb} ]", mnemonic='SLA')
@ispec("16<[ 00110 r(3) {cb} ]", mnemonic='SLL') #undocumented
@ispec("16<[ 00101 r(3) {cb} ]", mnemonic='SRA')
@ispec("16<[ 00111 r(3) {cb} ]", mnemonic='SRL')
def mostek_rotshift(obj,r):
    if obj.misc['pfx'] is not None:
        raise InstructionError(obj)
    op1 = getreg8(obj,r)
    obj.operands = [op1]
    obj.type = type_data_processing

# FD / DD prefixed:
@ispec("24<[ 00000 r(3) d(8) {cb} ]", mnemonic='RLC')
@ispec("24<[ 00010 r(3) d(8) {cb} ]", mnemonic='RL')
@ispec("24<[ 00001 r(3) d(8) {cb} ]", mnemonic='RRC')
@ispec("24<[ 00011 r(3) d(8) {cb} ]", mnemonic='RR')
@ispec("24<[ 00100 r(3) d(8) {cb} ]", mnemonic='SLA')
@ispec("24<[ 00110 r(3) d(8) {cb} ]", mnemonic='SLL')
@ispec("24<[ 00101 r(3) d(8) {cb} ]", mnemonic='SRA')
@ispec("24<[ 00111 r(3) d(8) {cb} ]", mnemonic='SRL')
def mostek_rotshift(obj,r,d):
    base = obj.misc['pfx']
    if base is None: raise InstructionError(obj)
    disp = env.cst(d,8).signextend(16)
    op1 = env.mem(base,8,disp=disp.value)
    obj.operands = [op1]
    if r!=0b110: obj.operands.append(getreg8(obj,r))
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

# FD/DD prefixed BIT & SET:
@ispec("24<[ 01 b(3) 110 d(8) {cb} ]", mnemonic='BIT')
@ispec("24<[ 11 b(3) 110 d(8) {cb} ]", mnemonic='SET')
def mostek_bitset(obj,d,b):
    op1 = env.cst(b,3)
    base = obj.misc['pfx']
    if base is None: raise InstructionError(obj)
    disp = env.cst(d,8).signextend(16)
    op2 = env.mem(base,8,disp=disp.value)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# ----------
# Jump Group
# ----------

@ispec("24<[ nn(16) 11 000 011 ]", mnemonic='JP')
def mostek_jump(obj,nn):
    # DD/FD prefix are ignored
    obj.operands = [env.cst(nn,16)]
    obj.type = type_control_flow

@ispec("24<[ nn(16) 11 cc(3) 010 ]", mnemonic='JPcc')
def mostek_jump(obj,cc,nn):
    # DD/FD prefix are ignored
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
    # DD/FD prefix are ignored
    disp = env.cst(e,8)
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
    # DD/FD prefix are ignored
    obj.operands = [env.cst(nn,16)]
    obj.type = type_control_flow

@ispec("24<[ nn(16) 11 cc(3) 100 ]", mnemonic='CALLcc')
def mostek_call(obj,cc,nn):
    # DD/FD prefix are ignored
    obj.cond = env.CONDITION[cc]
    obj.operands = [obj.cond[0],env.cst(nn,16)]
    obj.type = type_control_flow

@ispec("8<[ {c9} ]", mnemonic='RET')
@ispec("16<[ {4d} {ed} ]", mnemonic='RETI')
@ispec("16<[ {45} {ed} ]", mnemonic='RETN')
def mostek_ret(obj):
    # DD/FD prefix are ignored
    obj.operands = []
    obj.type = type_control_flow

@ispec("8<[ 11 cc(3) 000 ]", mnemonic='RETcc')
def mostek_ret(obj,cc):
    # DD/FD prefix are ignored
    obj.cond = env.CONDITION[cc]
    obj.operands = [obj.cond[0]]
    obj.type = type_control_flow

@ispec("8<[ 11 t(3) 111 ]", mnemonic='RST')
def mostek_rst(obj,t):
    # DD/FD prefix are ignored
    p = (0x00, 0x08, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38)[t]
    obj.operands = [env.cst(p,8)]
    obj.type = type_control_flow

# ----------------------
# Input and output Group
# ----------------------

@ispec("16<[ n(8) {db} ]", mnemonic='IN')
@ispec("16<[ n(8) {d3} ]", mnemonic='OUT')
def mostek_io(obj,n):
    # DD/FD prefix are ignored
    obj.operands = [env.a, env.cst(n,8)]
    if obj.mnemonic=='OUT': obj.operands.reverse()
    obj.type = type_other

@ispec("16<[ 01 r(3) 000 {ed} ]", mnemonic='IN')
@ispec("16<[ 01 r(3) 001 {ed} ]", mnemonic='OUT')
def mostek_io(obj,r):
    # DD/FD prefix are ignored
    dst = env.reg8[r] if r!=0b110 else env.f
    obj.operands = [dst, env.c]
    if obj.mnemonic=='OUT': obj.operands.reverse()
    obj.type = type_other

@ispec("16<[ {a2} {ed} ]", mnemonic='INI')
@ispec("16<[ {b2} {ed} ]", mnemonic='INIR')
@ispec("16<[ {aa} {ed} ]", mnemonic='IND')
@ispec("16<[ {ba} {ed} ]", mnemonic='INDR')
@ispec("16<[ {a3} {ed} ]", mnemonic='OUTI')
@ispec("16<[ {b3} {ed} ]", mnemonic='OTIR')
@ispec("16<[ {ab} {ed} ]", mnemonic='OUTD')
@ispec("16<[ {bb} {ed} ]", mnemonic='OTDR')
def mostek_io(obj):
    # DD/FD prefix are ignored
    obj.operands = []
    obj.type = type_other


