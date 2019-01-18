# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2018 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

# ref: The SH-4 CPU Core Architecture, 12 september 2002.

from amoco.arch.superh.sh4 import env

from amoco.arch.core import *

#-------------------------------------------------------
# sh-4 decoders
#-------------------------------------------------------

ISPECS = []

# import sh-2 instructions
#-------------------------

from amoco.arch.superh.sh2.spec_sh2 import *

# add sh3/sh4 instructions
#-------------------------
