# -*- coding: utf-8 -*-

from amoco.arch.z80.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().iteritems()))

#import specifications:
from amoco.arch.core import instruction, disassembler

instruction.set_uarch(uarch)

from amoco.arch.z80.formats import Mostek_full
instruction.set_formatter(Mostek_full)

#define disassembler:
from amoco.arch.z80 import spec_mostek

disassemble = disassembler([spec_mostek])

def PC():
    return pc
