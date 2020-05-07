# -*- coding: utf-8 -*-

from amoco.arch.eBPF.asm import *

# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))

# import specifications:
from amoco.arch.core import instruction, disassembler

instruction_BPF = type("instruction_BPF", (instruction,), {})
instruction_BPF.set_uarch(uarch)

# we use the same formatter has eBPF...
from amoco.arch.eBPF.formats import eBPF_full

instruction_BPF.set_formatter(eBPF_full)

# define disassembler with spec_bpf module:
from amoco.arch.eBPF import spec_bpf

disassemble = disassembler([spec_bpf], iclass=instruction_BPF)


def PC():
    return pc


def get_data_endian():
    return 1
