# -*- coding: utf-8 -*-

from amoco.arch.msp430.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_msp430 = type("instruction_msp430", (instruction,), {})
instruction_msp430.set_uarch(uarch)

from amoco.arch.msp430.formats import MSP430_full
from amoco.arch.msp430.formats import MSP430_synthetic

instruction_msp430.set_formatter(MSP430_synthetic)

# define disassembler:
from amoco.arch.msp430 import spec_msp430

disassemble = disassembler([spec_msp430], iclass=instruction_msp430)
disassemble.maxlen = 6


def PC():
    return pc


def get_data_endian():
    return 1
