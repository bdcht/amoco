# -*- coding: utf-8 -*-

from amoco.arch.z80.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().items()))

#import specifications:
from amoco.arch.core import instruction, disassembler
instruction_z80 = type('instruction_z80',(instruction,),{})
instruction_z80.set_uarch(uarch)

from amoco.arch.z80.formats import Mostek_full
instruction_z80.set_formatter(Mostek_full)

#define disassembler:
from amoco.arch.z80 import spec_mostek

disassemble = disassembler([spec_mostek],iclass=instruction_z80)

def PC():
    return pc
