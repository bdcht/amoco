# -*- coding: utf-8 -*-

from amoco.arch.ppc32.e200.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_e200 = type("instruction_e200", (instruction,), {})
instruction_e200.set_uarch(uarch)

from amoco.arch.ppc32.e200.formats import PPC_full

instruction_e200.set_formatter(PPC_full)

# define disassembler:
from amoco.arch.ppc32.e200 import spec_vle

endian = lambda: -1

disassemble = disassembler([spec_vle], iclass=instruction_e200,endian=endian)


def PC():
    return pc

def get_data_endian():
    return -1  # BE
