# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.structs import StructDefine,StructFormatter
from amoco.system.core import BinFormat, CoreExec, DefineStub
from amoco.system.memory import MemoryMap
from amoco.arch.avr import cpu
from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")

@DefineLoader("atmega328p")
def loader_atmega328p(p):
    from amoco.config import conf
    logger.info("atmega328p program loading...")
    return Boot.loader(p,conf)


class Task(CoreExec):
    def __init__(self, p, cpu=None):
        super().__init__(p,cpu)
        self.code = self.initstate()

    def read_instruction(self, vaddr, **kargs):
        kargs["address"] = vaddr
        kargs["mmap"] = self.code.mmap
        return super().read_instruction(vaddr<<1, **kargs)

# ----------------------------------------------------------------------------

class Boot(object):
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
        return cls(conf).load_binary(bprm)

    def load_binary(self,bprm):
        p = Task(bprm, cpu)
        p.OS = self
        # map the CODE area:
        p.code.mmap.write(bprm.entrypoints[0], self.dataio.read())
        # define registers:
        for r in cpu.registers:
            p.state[r] = cpu.cst(0,r.size())
        p.state[cpu.pc] = cpu.cst(bprm.entrypoints[0]/2,cpu.pc.size())
        RAMEND = 0x0900
        p.state[cpu.sp] = cpu.cst(RAMEND,16)
        # map the DATA area:
        p.state.mmap.write(0x100,b'\0'*(RAMEND-0x100))
        # map the BIOS functions as external symbols:
        self.load_bios(p.code.mmap)
        self.tasks.append(p)
        return p

    def load_bios(self,mmap):
        xf = cpu.ext("bios_a0",size=32)
        xf.stub = self.stub(xf.ref)
        mmap.write(0xa0,xf)
        xf = cpu.ext("bios_b0",size=32)
        xf.stub = self.stub(xf.ref)
        mmap.write(0xb0,xf)
        xf = cpu.ext("bios_c0",size=32)
        xf.stub = self.stub(xf.ref)
        mmap.write(0xc0,xf)

    def stub(self, refname):
        return self.stubs.get(refname, self.default_stub)


# ----------------------------------------------------------------------------

@DefineStub(Boot, "ret_0", default=True)
def nullstub(m, **kargs):
    m[cpu.pc] = m(cpu.ra)


