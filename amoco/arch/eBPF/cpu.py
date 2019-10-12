# -*- coding: utf-8 -*-

from amoco.arch.eBPF.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().items()))

#import specifications:
from amoco.arch.core import instruction, disassembler
instruction_eBPF = type('instruction_eBPF',(instruction,),{})
instruction_eBPF.set_uarch(uarch)

from amoco.arch.eBPF.formats import eBPF_full
instruction_eBPF.set_formatter(eBPF_full)

#define disassembler:
from amoco.arch.eBPF import spec

disassemble = disassembler([spec],iclass=instruction_eBPF)

def PC():
    return pc

def get_data_endian():
    return 1
