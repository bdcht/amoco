# -*- coding: utf-8 -*-

from amoco.arch.x64.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().items()))

from amoco.arch.core import instruction, disassembler
instruction_x64 = type('instruction_x64',(instruction,),{})
instruction_x64.set_uarch(uarch)
from amoco.arch.x64.formats import IA32e_Intel,IA32e_ATT
instruction_x64.set_formatter(IA32e_Intel)

from amoco.arch.x64 import spec_ia32e

disassemble = disassembler([spec_ia32e],iclass=instruction_x64)
disassemble.maxlen = 15

def PC():
    return rip

def configure(**kargs):
    from amoco.config import conf
    # asm format:
    f = kargs.get('format',conf.Arch.format_x64)
    if f in ('AT&T','at&t','ATT','att'):
        instruction_x64.set_formatter(IA32e_ATT)
    elif f in ('Intel','INTEL','intel'):
        instruction_x64.set_formatter(IA32e_Intel)

configure()
