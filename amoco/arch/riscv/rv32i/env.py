# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# reference documentations:
# The RISC-V Instruction Set Manual, volume I, User level ISA, version 1.2.
# https://riscv.org/specifications/
# and the tiny risc-v instruction set architecture:
# http://www.csl.cornell.edu/courses/ece4750/handouts/ece4750-tinyrv-isa.txt

# registers :
# -----------

# general registers:
x = [reg("x%d" % r, 32) for r in range(32)]
# fpu registers:
f = [reg("f%d" % r, 32) for r in range(32)]

x[0] = cst(0, 32).to_sym("zero")
x[1].ref = "ra"
x[2].ref = "sp"
x[3].ref = "gp"
x[4].ref = "tp"
x[5].ref = "t0"
x[6].ref = "t1"
x[7].ref = "t2"
x[8].ref = "s0"
x[9].ref = "s1"

zero = x[0]
ra = x[1]
sp = x[2]
gp = x[3]
tp = x[4]
t0 = x[5]
t1 = x[6]
t2 = x[7]
s0 = x[8]
s1 = x[9]

for i in range(0, 8):
    x[10 + i].ref = "a%d" % i

a0 = x[10]
a1 = x[11]
a2 = x[12]
a3 = x[13]
a4 = x[14]
a5 = x[15]
a6 = x[16]
a7 = x[17]

for i in range(2, 12):
    x[16 + i].ref = "s%d" % i

x[28].ref = "t3"
x[29].ref = "t4"
x[30].ref = "t5"
x[31].ref = "t6"

t3 = x[28]
t4 = x[29]
t5 = x[30]
t6 = x[31]

csr = {
    0x7C0: reg("prog2mngr", 32),
    0xFC0: reg("mngr2prog", 32),
    0xF14: reg("coreid", 32),
    0xFC1: reg("numcores", 32),
    0x7C1: reg("stats_en", 32),
}

fcsr = reg("fcsr", 32)
pc = reg("pc", 32)

is_reg_pc(pc)
is_reg_stack(sp)

registers = x+[pc]
