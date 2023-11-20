# -*- coding: utf-8 -*-

from amoco.arch.ppc32.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_ppc32 = type("instruction_ppc32", (instruction,), {})
instruction_ppc32.set_uarch(uarch)

from amoco.arch.ppc32.formats import PPC_full

instruction_ppc32.set_formatter(PPC_full)

# define disassembler:
from amoco.arch.ppc32 import spec_booke as spec

endian = lambda: -1

disassemble = disassembler([spec], iclass=instruction_ppc32,endian=endian)


def PC():
    return pc

def get_data_endian():
    return -1  # BE
