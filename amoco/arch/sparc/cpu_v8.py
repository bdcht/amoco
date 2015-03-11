# -*- coding: utf-8 -*-

from amoco.arch.sparc.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().iteritems()))

#import specifications:
from amoco.arch.core import instruction, disassembler

instruction.set_uarch(uarch)

from amoco.arch.sparc.formats import SPARC_V8_full
from amoco.arch.sparc.formats import SPARC_V8_synthetic
instruction.set_formatter(SPARC_V8_synthetic)

#define disassembler:
from amoco.arch.sparc import spec_v8

disassemble = disassembler([spec_v8],endian=lambda:-1)

def PC():
    return pc
