# -*- coding: utf-8 -*-

from amoco.arch.riscv.rv64i.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_riscv64 = type("instruction_riscv64", (instruction,), {})
instruction_riscv64.set_uarch(uarch)

from amoco.arch.riscv.rv64i.formats import RISCV_full
from amoco.arch.riscv.rv64i.formats import RISCV_synthetic

instruction_riscv64.set_formatter(RISCV_full)

# define disassembler:
from amoco.arch.riscv.rv64i import spec_rv64i

disassemble = disassembler([spec_rv64i], iclass=instruction_riscv64)


def PC():
    return pc


def get_data_endian():
    return 1  # LE
