# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2021 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *


# registers :
# -----------

A = reg("A", 8)
X = reg("X", 8)
Y = reg("Y", 8)

sp_ = reg("sp",16)
sp = slc(sp_,0,8,"SP")
P = reg("P",8)

pc = reg("PC",16)

pcl = slc(pc,0,8,"PCL")
pch = slc(pc,8,8,"PCH")


C = slc(P,0,1,"C") # carry
Z = slc(P,1,1,"Z") # zero
I = slc(P,2,1,"I") # interrupt enable/disable(1)
D = slc(P,3,1,"D") # decimal mode
B = slc(P,4,1,"B") # brk command
V = slc(P,6,1,"V") # overflow
N = slc(P,7,1,"N") # negative

is_reg_pc(pc)
is_reg_stack(sp_)
is_reg_flags(P)

registers = [A,X,Y,sp_,P,pc]

A_ = A.zeroextend(16)
X_ = A.zeroextend(16)
Y_ = A.zeroextend(16)

