# -*- coding: utf-8 -*-

from amoco.arch.x86.asm import *
# expose "microarchitecture" (instructions semantics)
uarch = dict(filter(lambda kv:kv[0].startswith('i_'),locals().iteritems()))

from amoco.arch.core import instruction, disassembler

instruction.set_uarch(uarch)

from amoco.arch.x86.formats import *

from amoco.arch.x86 import spec_ia32
disassemble = disassembler([spec_ia32])
disassemble.maxlen = 15

def PC():
    return eip

def configure(**kargs):
    from amoco.config import get_module_conf
    conf = get_module_conf('x86')
    conf.update(kargs)
    # asm format:
    if conf['format'] in ('AT&T','at&t','ATT','att'):
        instruction.set_formatter(IA32_ATT)
    else:
        instruction.set_formatter(IA32_Intel)

configure()
