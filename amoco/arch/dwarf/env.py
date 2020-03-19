# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# symbols from libgcc/unwind-dw2.c :
# -----------------------------------

WORD = 64

with is_reg_pc:
    op_ptr = reg("op_ptr", 64)

with is_reg_stack:
    sp = reg("sp", 64)

stack_elt = reg("stack_elt", 6)
