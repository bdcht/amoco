# -*- coding: utf-8 -*-

from amoco.arch.v850.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().items()))

#import specifications:
from amoco.arch.core import instruction, disassembler
instruction_v850 = type('instruction_v850',(instruction,),{})
instruction_v850.set_uarch(uarch)

from amoco.arch.v850.formats import v850_full
instruction_v850.set_formatter(v850_full)

#define disassembler:
import amoco.arch.v850.spec_v850e2s as spec

disassemble = disassembler([spec],iclass=instruction_v850)

def PC():
    return pc

def get_data_endian():
    return 1
