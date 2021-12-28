# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2021 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.structs import StructDefine,StructFormatter
from amoco.system.core import BinFormat, CoreExec, DefineStub
from amoco.system.memory import MemoryMap
from amoco.arch.w65c02 import cpu
from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")

RESETV = 0xFFFC

ROM = b'@\xad\xf9\xff\xf0\xfb0p\xc9a\x90\x078\xe9a\x18i\n`\xc9A\x90\x078\xe9A\x18i\n`8\xe90` \x01\x90\n\n\n\n\x85\x00 \x01\x90\x05\x00`\xad\xf9\xff\xf0\xfb0@\xc9\n\xf0\x04\xc9\r\xd0\xf1\xad\xf9\xff\xf0\xfb01\xc9S\xd0\xed\xad\xf9\xff\xf0\xfb0&\xc91\xd0\xdb "\x908\xe9\x03\x90\xd3\xf0\xd1\xaa\xa0\x00 "\x90\x85\x03 "\x90\x85\x02 "\x90\x91\x02\xc8\xca\xd0\xf7\x80\xb9L\x00\x10'+(b'\0'*28543)+b'\x00\x90@\x90\x00\x90'

# ----------------------------------------------------------------------------

class OS(object):
    stubs = {}
    default_stub = DefineStub.warning

    def __init__(self, conf=None):
        if conf is None:
            from amoco.config import System

            conf = System()
        self.tasks = []
        self.abi = None
        self.symbols = {}

    @classmethod
    def loader(cls, bprm, conf=None):
        return cls(conf).load_bin(bprm)

    def load_bin(self,bprm):
        p = Task(bprm, cpu)
        # map a W65C02 generic BIOS ROM in range [0x9000,0xffff]:
        p.state.mmap.write(0x9000,ROM)
        p.OS = self
        # define registers:
        p.state[cpu.sp_] = cpu.cst(0x01ff,16)
        p.state[cpu.A] = cpu.cst(0x0,8)
        p.state[cpu.X] = cpu.cst(0x0,8)
        p.state[cpu.Y] = cpu.cst(0x0,8)
        p.state[cpu.P] = cpu.cst(0x36,8)
        entry = p.getx(RESETV,size=16)
        print(entry)
        p.state[cpu.pc] = entry
        # map the stack area:
        p.state.mmap.write(0x100,b'\0'*0x100)
        self.tasks.append(p)
        return p

    def stub(self, refname):
        return self.stubs.get(refname, self.default_stub)


# ----------------------------------------------------------------------------

class Task(CoreExec):
    pass

# ----------------------------------------------------------------------------
@DefineStub(OS, "ret_0", default=True)
def nullstub(m, **kargs):
    m[cpu.pc] = m(cpu.mem(cpu.sp_,16))
    m[cpu.sp] = m(cpu.sp+2)

