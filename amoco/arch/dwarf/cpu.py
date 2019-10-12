# -*- coding: utf-8 -*-

from amoco.arch.dwarf.asm import *
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().items()))

#import specifications:
from amoco.arch.core import instruction, disassembler
instruction_dwarf = type('instruction_dwarf',(instruction,),{})
instruction_dwarf.set_uarch(uarch)

from amoco.arch.dwarf.formats import DW_full
instruction_dwarf.set_formatter(DW_full)

#define disassembler:
from amoco.arch.dwarf import spec

disassemble = disassembler([spec],iclass=instruction_dwarf)
disassemble.maxlen = 21
def PC():
    return op_ptr

def get_data_endian():
    return 1
