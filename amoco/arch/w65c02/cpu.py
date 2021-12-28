# -*- coding: utf-8 -*-

from amoco.arch.w65c02.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_w65c02 = type("instruction_w65c02", (instruction,), {})
instruction_w65c02.set_uarch(uarch)

from amoco.arch.w65c02.formats import w65c02_full

instruction_w65c02.set_formatter(w65c02_full)

# define disassembler:
from amoco.arch.w65c02 import spec

disassemble = disassembler([spec], iclass=instruction_w65c02)


def PC():
    return pc


def get_data_endian():
    return 1  # LE
