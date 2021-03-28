# -*- coding: utf-8 -*-

from amoco.arch.mips.r3000.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_r3000 = type("instruction_r3000", (instruction,), {})
instruction_r3000.set_uarch(uarch)

from amoco.arch.mips.r3000.formats import MIPS_full
from amoco.arch.mips.r3000.formats import MIPS_synthetic

instruction_r3000.set_formatter(MIPS_full)

# define disassembler:
from amoco.arch.mips.r3000 import spec

endian = lambda: -1

disassemble = disassembler([spec], iclass=instruction_r3000,endian=endian)


def PC():
    return pc

def get_data_endian():
    return -1  # BE
