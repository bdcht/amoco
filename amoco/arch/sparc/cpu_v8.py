# -*- coding: utf-8 -*-

from amoco.arch.sparc.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_sparc = type("instruction_sparc", (instruction,), {})
instruction_sparc.set_uarch(uarch)

from amoco.arch.sparc.formats import SPARC_V8_full
from amoco.arch.sparc.formats import SPARC_V8_synthetic

instruction_sparc.set_formatter(SPARC_V8_full)

# define disassembler:
from amoco.arch.sparc import spec_v8

disassemble = disassembler([spec_v8], endian=lambda: -1, iclass=instruction_sparc)


def PC():
    return pc


def get_data_endian():
    return -1
