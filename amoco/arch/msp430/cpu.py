# -*- coding: utf-8 -*-

from amoco.arch.msp430.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().iteritems()))

#import specifications:
from amoco.arch.core import instruction, disassembler

instruction.set_uarch(uarch)

from amoco.arch.msp430.formats import MSP430_synthetic
instruction.set_formatter(MSP430_synthetic)

#define disassembler:
from amoco.arch.msp430 import spec_msp430

disassemble = disassembler([spec_msp430])
disassemble.maxlen = 6

def PC():
    return pc
