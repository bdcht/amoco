# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.arch.arm.v7.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().iteritems()))

from amoco.arch.core import instruction, disassembler

instruction.set_uarch(uarch)

# define disassembler:
from amoco.arch.arm.v7 import spec_armv7
from amoco.arch.arm.v7 import spec_thumb

from amoco.arch.arm.v7.formats import ARM_V7_full
instruction.set_formatter(ARM_V7_full)


mode   = (lambda : internals['isetstate'])
endian = (lambda : 1 if internals['endianstate']==0 else -1)

disassemble = disassembler([spec_armv7,spec_thumb],mode,endian)

def PC():
    return pc
