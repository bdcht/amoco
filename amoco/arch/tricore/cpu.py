# -*- coding: utf-8 -*-

from amoco.arch.tricore.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_tricore = type("instruction_tricore", (instruction,), {})
instruction_tricore.set_uarch(uarch)

from amoco.arch.tricore.formats import TriCore_full

instruction_tricore.set_formatter(TriCore_full)

# define disassembler:
from amoco.arch.tricore import spec

disassemble = disassembler([spec], iclass=instruction_tricore)


def PC():
    return pc


def get_data_endian():
    return 1  # LE
