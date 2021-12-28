# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2021 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.arch.w65c02 import env

from amoco.arch.core import *

# -------------------------------------------------------
# W65C02(S) instruction decoders
# -------------------------------------------------------

ISPECS = []

# absolute addressing: a
# --------------------
@ispec("24<[a(16) {0c}]", mnemonic="TSB")
@ispec("24<[a(16) {0d}]", mnemonic="ORA")
@ispec("24<[a(16) {0e}]", mnemonic="ASL")
@ispec("24<[a(16) {1c}]", mnemonic="TRB")
@ispec("24<[a(16) {20}]", mnemonic="JSR")
@ispec("24<[a(16) {2c}]", mnemonic="BIT")
@ispec("24<[a(16) {2d}]", mnemonic="AND")
@ispec("24<[a(16) {2e}]", mnemonic="ROL")
@ispec("24<[a(16) {4c}]", mnemonic="JMP")
@ispec("24<[a(16) {4d}]", mnemonic="EOL")
@ispec("24<[a(16) {4e}]", mnemonic="LSR")
@ispec("24<[a(16) {6d}]", mnemonic="ADC")
@ispec("24<[a(16) {6e}]", mnemonic="ROR")
@ispec("24<[a(16) {8c}]", mnemonic="STY")
@ispec("24<[a(16) {8d}]", mnemonic="STA")
@ispec("24<[a(16) {8e}]", mnemonic="STX")
@ispec("24<[a(16) {9c}]", mnemonic="STZ")
@ispec("24<[a(16) {ad}]", mnemonic="LDA")
@ispec("24<[a(16) {ae}]", mnemonic="LDX")
@ispec("24<[a(16) {cc}]", mnemonic="CPY")
@ispec("24<[a(16) {cd}]", mnemonic="CMP")
@ispec("24<[a(16) {ce}]", mnemonic="DEC")
@ispec("24<[a(16) {ec}]", mnemonic="CPX")
@ispec("24<[a(16) {ed}]", mnemonic="SBC")
@ispec("24<[a(16) {ee}]", mnemonic="INC")
def w65c02_absolute(obj, a):
    adr = env.cst(a,16)
    if obj.mnemonic in ("JMP","JSR"):
        obj.operands = [adr]
        obj.type = type_control_flow
        obj.misc['ref'] = adr
    else:
        obj.operands = [env.mem(adr,8)]
        obj.type = type_data_processing

# absolute indexed indirect : (a,x)
# ---------------------------------
@ispec("24<[a(16) {7c}]", mnemonic="JMP")
def w65c02_aiix(obj, a):
    adr = env.cst(a,16) + env.X_
    obj.operands = [env.mem(adr,16)]
    obj.type = type_control_flow

# absolute indexed with X : a,x
# -----------------------------
@ispec("24<[a(16) {1d}]", mnemonic="ORA")
@ispec("24<[a(16) {1e}]", mnemonic="ASL")
@ispec("24<[a(16) {3c}]", mnemonic="BIT")
@ispec("24<[a(16) {3d}]", mnemonic="AND")
@ispec("24<[a(16) {3e}]", mnemonic="ROL")
@ispec("24<[a(16) {5d}]", mnemonic="EOR")
@ispec("24<[a(16) {5e}]", mnemonic="LSR")
@ispec("24<[a(16) {7d}]", mnemonic="ADC")
@ispec("24<[a(16) {7e}]", mnemonic="ROR")
@ispec("24<[a(16) {9d}]", mnemonic="STA")
@ispec("24<[a(16) {9e}]", mnemonic="STZ")
@ispec("24<[a(16) {bc}]", mnemonic="LDY")
@ispec("24<[a(16) {bd}]", mnemonic="LDA")
@ispec("24<[a(16) {dd}]", mnemonic="CMP")
@ispec("24<[a(16) {de}]", mnemonic="DEC")
@ispec("24<[a(16) {fd}]", mnemonic="SBC")
@ispec("24<[a(16) {fe}]", mnemonic="INC")
def w65c02_aix(obj, a):
    adr = env.cst(a,16) + env.X_
    obj.operands = [env.mem(adr,8)]
    obj.type = type_data_processing

# absolute indexed with Y : a,y
# -------------------------
@ispec("24<[a(16) {19}]", mnemonic="ORA")
@ispec("24<[a(16) {39}]", mnemonic="AND")
@ispec("24<[a(16) {59}]", mnemonic="EOR")
@ispec("24<[a(16) {79}]", mnemonic="ADC")
@ispec("24<[a(16) {99}]", mnemonic="STA")
@ispec("24<[a(16) {b9}]", mnemonic="LDA")
@ispec("24<[a(16) {be}]", mnemonic="LDX")
@ispec("24<[a(16) {d9}]", mnemonic="CMP")
@ispec("24<[a(16) {f9}]", mnemonic="SBC")
def w65c02_aiy(obj, a):
    adr = env.cst(a,16) + env.Y_
    obj.operands = [env.mem(adr,8)]
    obj.type = type_data_processing

# absolute indirect: (a)
# ------------------
@ispec("24<[a(16) {6c}]", mnemonic="JMP")
def w65c02_ai(obj, a):
    adr = env.cst(a,16)
    obj.operands = [env.mem(adr,16)]
    obj.type = type_control_flow

# accumulator addressing : A
# ------------------------
@ispec("8<[{0a}]", mnemonic="ASL")
@ispec("8<[{1a}]", mnemonic="INC")
@ispec("8<[{2a}]", mnemonic="ROL")
@ispec("8<[{3a}]", mnemonic="DEC")
@ispec("8<[{4a}]", mnemonic="LSR")
@ispec("8<[{6a}]", mnemonic="ROR")
@ispec("8<[{ac}]", mnemonic="LDY")
def w65c02_A(obj):
    obj.operands = [env.A]
    obj.type = type_data_processing

# immediate addressing: #
# ---------------------
@ispec("16<[c(8) {09}]", mnemonic="ORA")
@ispec("16<[c(8) {29}]", mnemonic="AND")
@ispec("16<[c(8) {49}]", mnemonic="EOR")
@ispec("16<[c(8) {69}]", mnemonic="ADC")
@ispec("16<[c(8) {89}]", mnemonic="BIT")
@ispec("16<[c(8) {a0}]", mnemonic="LDY")
@ispec("16<[c(8) {a2}]", mnemonic="LDX")
@ispec("16<[c(8) {a9}]", mnemonic="LDA")
@ispec("16<[c(8) {c0}]", mnemonic="CPY")
@ispec("16<[c(8) {c9}]", mnemonic="CMP")
@ispec("16<[c(8) {e0}]", mnemonic="CPX")
@ispec("16<[c(8) {e9}]", mnemonic="SBC")
def w65c02_immediate(obj, c):
    obj.operands = [env.cst(c,8)]
    obj.type = type_data_processing

# implied addressing : i
# --------------------
@ispec("8<[{18}]", mnemonic="CLC", type=type_data_processing)
@ispec("8<[{38}]", mnemonic="SEC", type=type_data_processing)
@ispec("8<[{58}]", mnemonic="CLI", type=type_data_processing)
@ispec("8<[{78}]", mnemonic="SEI", type=type_data_processing)
@ispec("8<[{88}]", mnemonic="DEY", type=type_data_processing)
@ispec("8<[{8a}]", mnemonic="TXA", type=type_data_processing)
@ispec("8<[{98}]", mnemonic="TYA", type=type_data_processing)
@ispec("8<[{9a}]", mnemonic="TXS", type=type_data_processing)
@ispec("8<[{a8}]", mnemonic="TAY", type=type_data_processing)
@ispec("8<[{aa}]", mnemonic="TAX", type=type_data_processing)
@ispec("8<[{b8}]", mnemonic="CLV", type=type_data_processing)
@ispec("8<[{ba}]", mnemonic="TSX", type=type_data_processing)
@ispec("8<[{c8}]", mnemonic="INY", type=type_data_processing)
@ispec("8<[{ca}]", mnemonic="DEX", type=type_data_processing)
@ispec("8<[{cb}]", mnemonic="WAI", type=type_system)
@ispec("8<[{d8}]", mnemonic="CLD", type=type_data_processing)
@ispec("8<[{db}]", mnemonic="STP", type=type_system)
@ispec("8<[{e8}]", mnemonic="INX", type=type_data_processing)
@ispec("8<[{ea}]", mnemonic="NOP", type=type_data_processing)
@ispec("8<[{f8}]", mnemonic="SED", type=type_data_processing)
def w65c02_implied(obj):
    obj.operands = []

# program counter relative: r
# -------------------------
@ispec("16<[a(8) {10}]", mnemonic="BPL")
@ispec("16<[a(8) {30}]", mnemonic="BMI")
@ispec("16<[a(8) {50}]", mnemonic="BVC")
@ispec("16<[a(8) {70}]", mnemonic="BVS")
@ispec("16<[a(8) {80}]", mnemonic="BRA")
@ispec("16<[a(8) {90}]", mnemonic="BCC")
@ispec("16<[a(8) {b0}]", mnemonic="BCS")
@ispec("16<[a(8) {d0}]", mnemonic="BNE")
@ispec("16<[a(8) {f0}]", mnemonic="BEQ")
def w65c02_pcr(obj, a):
    offset = env.cst(a,8).signextend(16)
    obj.operands = [offset]
    obj.misc["pc_ref"] = offset
    obj.type = type_control_flow

@ispec("24<[a(8) b(8) {0f}]", mnemonic="BBR0")
@ispec("24<[a(8) b(8) {1f}]", mnemonic="BBR1")
@ispec("24<[a(8) b(8) {2f}]", mnemonic="BBR2")
@ispec("24<[a(8) b(8) {3f}]", mnemonic="BBR3")
@ispec("24<[a(8) b(8) {4f}]", mnemonic="BBR4")
@ispec("24<[a(8) b(8) {5f}]", mnemonic="BBR5")
@ispec("24<[a(8) b(8) {6f}]", mnemonic="BBR6")
@ispec("24<[a(8) b(8) {7f}]", mnemonic="BBR7")
@ispec("24<[a(8) b(8) {8f}]", mnemonic="BBS0")
@ispec("24<[a(8) b(8) {9f}]", mnemonic="BBS1")
@ispec("24<[a(8) b(8) {af}]", mnemonic="BBS2")
@ispec("24<[a(8) b(8) {bf}]", mnemonic="BBS3")
@ispec("24<[a(8) b(8) {cf}]", mnemonic="BBS4")
@ispec("24<[a(8) b(8) {df}]", mnemonic="BBS5")
@ispec("24<[a(8) b(8) {ef}]", mnemonic="BBS6")
@ispec("24<[a(8) b(8) {ff}]", mnemonic="BBS7")
def w65c02_bb(obj, a, b):
    offset = env.cst(a,8).signextend(16)
    cond = env.cst(b,8)
    obj.operands = [cond,offset]
    obj.misc["pc_ref"] = offset
    obj.type = type_control_flow

# stack addressing: s
# -----------------
@ispec("8<[{00}]", mnemonic="BRK", type=type_control_flow)
@ispec("8<[{08}]", mnemonic="PHP", type=type_data_processing)
@ispec("8<[{28}]", mnemonic="PLP", type=type_data_processing)
@ispec("8<[{40}]", mnemonic="RTI", type=type_control_flow)
@ispec("8<[{48}]", mnemonic="PHA", type=type_data_processing)
@ispec("8<[{5a}]", mnemonic="PHY", type=type_data_processing)
@ispec("8<[{60}]", mnemonic="RTS", type=type_control_flow)
@ispec("8<[{68}]", mnemonic="PLA", type=type_data_processing)
@ispec("8<[{7a}]", mnemonic="PLY", type=type_data_processing)
@ispec("8<[{da}]", mnemonic="PHX", type=type_data_processing)
@ispec("8<[{fa}]", mnemonic="PLX", type=type_data_processing)
def w65c02_stack(obj):
    obj.operands = []

# zero page addressing: zp
# ---------------------
@ispec("16<[a(8) {04}]", mnemonic="TSB")
@ispec("16<[a(8) {05}]", mnemonic="ORA")
@ispec("16<[a(8) {06}]", mnemonic="ASL")
@ispec("16<[a(8) {14}]", mnemonic="TRB")
@ispec("16<[a(8) {24}]", mnemonic="BIT")
@ispec("16<[a(8) {25}]", mnemonic="AND")
@ispec("16<[a(8) {26}]", mnemonic="ROL")
@ispec("16<[a(8) {45}]", mnemonic="EOR")
@ispec("16<[a(8) {46}]", mnemonic="LSR")
@ispec("16<[a(8) {64}]", mnemonic="STZ")
@ispec("16<[a(8) {65}]", mnemonic="ADC")
@ispec("16<[a(8) {66}]", mnemonic="ROR")
@ispec("16<[a(8) {84}]", mnemonic="STY")
@ispec("16<[a(8) {85}]", mnemonic="STA")
@ispec("16<[a(8) {86}]", mnemonic="STX")
@ispec("16<[a(8) {a4}]", mnemonic="LDY")
@ispec("16<[a(8) {a5}]", mnemonic="LDA")
@ispec("16<[a(8) {a6}]", mnemonic="LDX")
@ispec("16<[a(8) {c4}]", mnemonic="CPY")
@ispec("16<[a(8) {c5}]", mnemonic="CMP")
@ispec("16<[a(8) {c6}]", mnemonic="DEC")
@ispec("16<[a(8) {e4}]", mnemonic="CPX")
@ispec("16<[a(8) {e5}]", mnemonic="SBC")
@ispec("16<[a(8) {e6}]", mnemonic="INC")
@ispec("16<[a(8) {07}]", mnemonic="RMB0")
@ispec("16<[a(8) {17}]", mnemonic="RMB1")
@ispec("16<[a(8) {27}]", mnemonic="RMB2")
@ispec("16<[a(8) {37}]", mnemonic="RMB3")
@ispec("16<[a(8) {47}]", mnemonic="RMB4")
@ispec("16<[a(8) {57}]", mnemonic="RMB5")
@ispec("16<[a(8) {67}]", mnemonic="RMB6")
@ispec("16<[a(8) {77}]", mnemonic="RMB7")
@ispec("16<[a(8) {87}]", mnemonic="SMB0")
@ispec("16<[a(8) {97}]", mnemonic="SMB1")
@ispec("16<[a(8) {a7}]", mnemonic="SMB2")
@ispec("16<[a(8) {b7}]", mnemonic="SMB3")
@ispec("16<[a(8) {c7}]", mnemonic="SMB4")
@ispec("16<[a(8) {d7}]", mnemonic="SMB5")
@ispec("16<[a(8) {e7}]", mnemonic="SMB6")
@ispec("16<[a(8) {f7}]", mnemonic="SMB7")
def w65c02_zp(obj, a):
    adr = env.cst(a,16)
    obj.operands = [env.mem(adr,8)]
    obj.type = type_data_processing

# zero page indexed indirect addressing: (zp,x)
# --------------------------------------
@ispec("16<[a(8) {01}]", mnemonic="ORA")
@ispec("16<[a(8) {21}]", mnemonic="AND")
@ispec("16<[a(8) {41}]", mnemonic="EOR")
@ispec("16<[a(8) {61}]", mnemonic="ADC")
@ispec("16<[a(8) {81}]", mnemonic="STA")
@ispec("16<[a(8) {a1}]", mnemonic="LDA")
@ispec("16<[a(8) {c1}]", mnemonic="CMP")
@ispec("16<[a(8) {e1}]", mnemonic="SBC")
def w65c02_zpii(obj, a):
    off = env.cst(a,16) + env.X_
    adr = env.mem(off,8).zeroextend(16)
    obj.operands = [env.mem(adr,8)]
    obj.type = type_data_processing

# zero page indexed with X : zp,x
# --------------------------
@ispec("16<[a(8) {15}]", mnemonic="ORA")
@ispec("16<[a(8) {16}]", mnemonic="ASL")
@ispec("16<[a(8) {34}]", mnemonic="BIT")
@ispec("16<[a(8) {35}]", mnemonic="AND")
@ispec("16<[a(8) {36}]", mnemonic="ROL")
@ispec("16<[a(8) {55}]", mnemonic="EOR")
@ispec("16<[a(8) {56}]", mnemonic="LSR")
@ispec("16<[a(8) {74}]", mnemonic="STZ")
@ispec("16<[a(8) {75}]", mnemonic="ADC")
@ispec("16<[a(8) {76}]", mnemonic="ROR")
@ispec("16<[a(8) {94}]", mnemonic="STY")
@ispec("16<[a(8) {95}]", mnemonic="STA")
@ispec("16<[a(8) {b4}]", mnemonic="LDY")
@ispec("16<[a(8) {b5}]", mnemonic="LDA")
@ispec("16<[a(8) {d5}]", mnemonic="CMP")
@ispec("16<[a(8) {d6}]", mnemonic="DEC")
@ispec("16<[a(8) {f5}]", mnemonic="SBC")
@ispec("16<[a(8) {f6}]", mnemonic="INC")
def w65c02_zpx(obj, a):
    adr = env.cst(a,16) + env.X_
    obj.operands = [env.mem(adr,8)]
    obj.type = type_data_processing

# zero page indexed with Y : zp,y
# --------------------------
@ispec("16<[a(8) {96}]", mnemonic="STX")
@ispec("16<[a(8) {b6}]", mnemonic="LDX")
def w65c02_zpy(obj, a):
    adr = env.cst(a,16) + env.Y_
    obj.operands = [env.mem(adr,8)]
    obj.type = type_data_processing

# zero page indirect: (zp)
# -------------------
@ispec("16<[a(8) {12}]", mnemonic="ORA")
@ispec("16<[a(8) {32}]", mnemonic="AND")
@ispec("16<[a(8) {52}]", mnemonic="EOR")
@ispec("16<[a(8) {72}]", mnemonic="ADC")
@ispec("16<[a(8) {92}]", mnemonic="STA")
@ispec("16<[a(8) {b2}]", mnemonic="LDA")
@ispec("16<[a(8) {d2}]", mnemonic="CMP")
@ispec("16<[a(8) {f2}]", mnemonic="SBC")
def w65c02_zpi(obj, a):
    adr = env.mem(env.cst(a,16),16)
    obj.operands = [env.mem(adr,8)]
    obj.type = type_data_processing

# zero page indirect indexed with Y: (zp),y
# ----------------------------------
@ispec("16<[a(8) {11}]", mnemonic="ORA")
@ispec("16<[a(8) {31}]", mnemonic="AND")
@ispec("16<[a(8) {51}]", mnemonic="EOR")
@ispec("16<[a(8) {71}]", mnemonic="ADC")
@ispec("16<[a(8) {91}]", mnemonic="STA")
@ispec("16<[a(8) {b1}]", mnemonic="LDA")
@ispec("16<[a(8) {d1}]", mnemonic="CMP")
@ispec("16<[a(8) {f1}]", mnemonic="SBC")
def w65c02_zpiy(obj, a):
    adr = env.mem(env.cst(a,16),16) + env.Y_
    obj.operands = [env.mem(adr,8)]
    obj.type = type_data_processing

# no-op (ignored):
# ----------------
@ispec("8<[{02}]", mnemonic="NOP")
@ispec("8<[{03}]", mnemonic="NOP")
@ispec("8<[{0b}]", mnemonic="NOP")
@ispec("8<[{13}]", mnemonic="NOP")
@ispec("8<[{1b}]", mnemonic="NOP")
@ispec("8<[{22}]", mnemonic="NOP")
@ispec("8<[{23}]", mnemonic="NOP")
@ispec("8<[{2b}]", mnemonic="NOP")
@ispec("8<[{33}]", mnemonic="NOP")
@ispec("8<[{3b}]", mnemonic="NOP")
@ispec("8<[{42}]", mnemonic="NOP")
@ispec("8<[{43}]", mnemonic="NOP")
@ispec("8<[{44}]", mnemonic="NOP")
@ispec("8<[{4b}]", mnemonic="NOP")
@ispec("8<[{53}]", mnemonic="NOP")
@ispec("8<[{54}]", mnemonic="NOP")
@ispec("8<[{5b}]", mnemonic="NOP")
@ispec("8<[{5c}]", mnemonic="NOP")
@ispec("8<[{62}]", mnemonic="NOP")
@ispec("8<[{63}]", mnemonic="NOP")
@ispec("8<[{6b}]", mnemonic="NOP")
@ispec("8<[{73}]", mnemonic="NOP")
@ispec("8<[{7b}]", mnemonic="NOP")
@ispec("8<[{82}]", mnemonic="NOP")
@ispec("8<[{83}]", mnemonic="NOP")
@ispec("8<[{8b}]", mnemonic="NOP")
@ispec("8<[{93}]", mnemonic="NOP")
@ispec("8<[{9b}]", mnemonic="NOP")
@ispec("8<[{a3}]", mnemonic="NOP")
@ispec("8<[{ab}]", mnemonic="NOP")
@ispec("8<[{b3}]", mnemonic="NOP")
@ispec("8<[{bb}]", mnemonic="NOP")
@ispec("8<[{c2}]", mnemonic="NOP")
@ispec("8<[{c3}]", mnemonic="NOP")
@ispec("8<[{d3}]", mnemonic="NOP")
@ispec("8<[{d4}]", mnemonic="NOP")
@ispec("8<[{dc}]", mnemonic="NOP")
@ispec("8<[{e2}]", mnemonic="NOP")
@ispec("8<[{e3}]", mnemonic="NOP")
@ispec("8<[{eb}]", mnemonic="NOP")
@ispec("8<[{f3}]", mnemonic="NOP")
@ispec("8<[{f4}]", mnemonic="NOP")
@ispec("8<[{fb}]", mnemonic="NOP")
@ispec("8<[{fc}]", mnemonic="NOP")
def w65c02_nop(obj):
    obj.operands = []
    obj.type = type_data_processing

