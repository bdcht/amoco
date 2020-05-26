# -*- coding: utf-8 -*-

from amoco.arch.riscv.rv32i.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_riscv = type("instruction_riscv", (instruction,), {})
instruction_riscv.set_uarch(uarch)

from amoco.arch.riscv.rv32i.formats import RISCV_full
from amoco.arch.riscv.rv32i.formats import RISCV_synthetic

instruction_riscv.set_formatter(RISCV_full)

# define disassembler:
from amoco.arch.riscv.rv32i import spec_rv32i

disassemble = disassembler([spec_rv32i], iclass=instruction_riscv)


def PC():
    return pc


def get_data_endian():
    return 1  # LE
