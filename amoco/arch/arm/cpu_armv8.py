# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.arch.arm.v8.asm64 import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().iteritems()))

from amoco.arch.core import instruction, disassembler

instruction.set_uarch(uarch)

# define disassembler:
from amoco.arch.arm.v8 import spec_armv8
from amoco.arch.arm.v8.formats import ARM_V8_full

instruction.set_formatter(ARM_V8_full)

endian = (lambda : 1 if internals['endianstate']==0 else -1)

disassemble = disassembler([spec_armv8],endian=endian)

def PC():
    return pc
