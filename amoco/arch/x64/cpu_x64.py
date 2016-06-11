# -*- coding: utf-8 -*-

from amoco.arch.x64.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().iteritems()))

from amoco.arch.core import instruction, disassembler

instruction.set_uarch(uarch)
from amoco.arch.x64.formats import IA32e_Intel,IA32e_ATT
instruction.set_formatter(IA32e_Intel)

from amoco.arch.x64 import spec_ia32e

disassemble = disassembler([spec_ia32e])
disassemble.maxlen = 15

def PC():
    return rip

def configure(**kargs):
    from amoco.config import get_module_conf
    conf = get_module_conf('x64')
    conf.update(kargs)
    # asm format:
    if conf['format'] in ('AT&T','at&t','ATT','att'):
        instruction.set_formatter(IA32e_ATT)
    else:
        instruction.set_formatter(IA32e_Intel)

configure()
