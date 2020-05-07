# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# reference documentation:
# https://www.kernel.org/doc/Documentation/networking/filter.txt

# (old) bpf registers:
# --------------------
A = reg("A", 32)
X = reg("X", 32)
M = [reg("M[%02d]" % i, 32) for i in range(16)]
# bpf extensions:
def skb(field=""):
    if not field:
        return reg("#skb", 32)
    return reg("#skb->%s" % field, 32)


# (new) eBPF registers:
# ---------------------

r0 = reg("r0", 64)  # return value from in-kernel function, exit value
r1 = reg("r1", 64)  # arguments for eBPF prog to in-kernel functions
r2 = reg("r2", 64)
r3 = reg("r3", 64)
r4 = reg("r4", 64)
r5 = reg("r5", 64)
r6 = reg("r6", 64)  # callee saved regs preserved by in-kernel functions
r7 = reg("r7", 64)
r8 = reg("r8", 64)
r9 = reg("r9", 64)

r10 = reg("r10", 64)  # read-only frame pointer to access stack
is_reg_stack(r10)

R = [r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10]
E = [slc(R[i], 0, 32, "e%d" % i) for i in range(10)]

pc = reg("pc", 64)
is_reg_pc(pc)
