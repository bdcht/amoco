# -*- coding: utf-8 -*-

from amoco.arch.superh.sh4.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_sh4 = type("instruction_sh4", (instruction,), {})
instruction_sh4.set_uarch(uarch)

from amoco.arch.superh.sh4.formats import SH4_full
from amoco.arch.superh.sh4.formats import SH4_synthetic

instruction_sh4.set_formatter(SH4_synthetic)

# define disassembler:
from amoco.arch.superh.sh4 import spec_sh4

disassemble = disassembler([spec_sh4], endian=lambda: -1, iclass=instruction_sh4)


def PC():
    return pc
