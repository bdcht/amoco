# -*- coding: utf-8 -*-

from amoco.arch.z80.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().iteritems()))

#import specifications:
from amoco.arch.core import instruction, disassembler

instruction.set_uarch(uarch)

from amoco.arch.z80.formats import GB_full
instruction.set_formatter(GB_full)

#define disassembler:
from amoco.arch.z80 import spec_gb

disassemble = disassembler([spec_gb])
