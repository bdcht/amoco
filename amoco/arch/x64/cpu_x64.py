# -*- coding: utf-8 -*-

from amoco.arch.x64.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().iteritems()))

from amoco.arch.core import instruction, disassembler

instruction.set_uarch(uarch)
from amoco.arch.x64.formats import IA32e_Intel
instruction.set_formatter(IA32e_Intel)

from amoco.arch.x64 import spec_ia32e

disassemble = disassembler([spec_ia32e])
disassemble.maxlen = 15

def PC():
    return rip
