# -*- coding: utf-8 -*-

from amoco.arch.pic.F46K22.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().items()))

#import specifications:
from amoco.arch.core import instruction, disassembler

instruction_f46k22 = type('instruction_f46k22',(instruction,),{})
instruction_f46k22.set_uarch(uarch)

from amoco.arch.pic.F46K22.formats import PIC_full
instruction_f46k22.set_formatter(PIC_full)

#define disassembler:
from amoco.arch.pic.F46K22 import spec_pic18

disassemble = disassembler([spec_pic18],iclass=instruction_f46k22)

def PC():
    return pc
