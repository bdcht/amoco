#!/usr/bin/env python

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.

from .utils import *

#------------------------------------------------------
# amoco x86 FPU (x87) instruction specs:
#------------------------------------------------------

ISPECS = []

@ispec_ia32("16>[ {0f}{77} ]", mnemonic = "EMMS", type=type_cpu_state)
def ia32_nooperand(obj):
    pass

