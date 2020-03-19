# -*- coding: utf-8 -*-

from amoco.arch.superh.sh2.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_sh2 = type("instruction_sh2", (instruction,), {})
instruction_sh2.set_uarch(uarch)

from amoco.arch.superh.sh2.formats import SH2_full

instruction_sh2.set_formatter(SH2_full)

# define disassembler:
from amoco.arch.superh.sh2 import spec_sh2

disassemble = disassembler([spec_sh2], endian=lambda: -1, iclass=instruction_sh2)


def PC():
    return pc


def get_data_endian():
    return -1
