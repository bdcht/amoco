# -*- coding: utf-8 -*-

from amoco.arch.avr.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().items()))

#import specifications:
from amoco.arch.core import instruction, disassembler
instruction_avr = type('instruction_avr',(instruction,),{})
instruction_avr.set_uarch(uarch)

from amoco.arch.avr.formats import AVR_full
instruction_avr.set_formatter(AVR_full)

#define disassembler:
from amoco.arch.avr import spec

disassemble = disassembler([spec],iclass=instruction_avr)

def PC():
    return pc

def get_data_endian():
    return 1 # LE
