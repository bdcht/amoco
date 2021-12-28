# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2021 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.structs import StructDefine,StructFormatter
from amoco.system.core import BinFormat, CoreExec, DefineStub
from amoco.system.memory import MemoryMap
from amoco.arch.tricore import cpu
from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")


class SSW(object):
    stubs = {}
    default_stub = DefineStub.warning

    def __init__(self, conf=None):
        if conf is None:
            from amoco.config import System

            conf = System()
        self.tasks = []
        self.abi = None
        self.symbols = {}

    def setup_mmio(self,p):
        # Tricore memory address space is divided in 16 segments [0-F] of 256MB each.
        # Segments 0 and 2 are marked as "reserved",
        # segments [1,3-7] can be used as "virtual memory" and thus translated by the MMU
        # if enabled, and segments [8-F] are mapped to physical memory.
        # Segment F is always dedicated to peripheral space.
        # In every segment, the first 4MB is available for storing CSAs (Context-Save-Area)
        # A CSA holds either the lower-context or upper-context of registers and its PCXI
        # corresponding to a task's state.
        for addr, mmio, sz, access in MEMMAP:
            xf = cpu.ext(mmio,size=sz*8,
                         mmio_r="r" in access,
                         mmio_w="w" in access)
            xf.stub = self.stub(xf.ref)
            p.state.mmap.write(addr,xf)

    def setup_UCB(self,p,ucb):
        # The User Configuration Block contains information used for configuration
        # and protection installation.
        pass

    @classmethod
    def loader(cls, bprm, conf=None, ucb=None):
        if bprm.is_ELF:
            obj = cls(conf).load_elf(bprm)
        else:
            obj = cls(conf).load_fw(bprm,ucb)
        return obj

    def load_fw(self,bprm,ucb=None):
        p = Task(bprm, cpu)
        p.OS = self
        # map the Program to the Program Flash 0 area:
        p.state.mmap.write(0x80000000,p.bin.dataio[0:])
        # map mmio regs in memory:
        self.setup_mmio(p)
        # map User Configuration Block (UCB) in memory:
        if ucb is not None:
            self.setup_UCB(p,ucb)
            _START = ucb["UCB_BMHD0_ORIG"]["STAD"]
        else:
            _START = 0x80000000
        # define registers:
        p.state[cpu.pc] = cpu.cst(_START,32)
        p.state[cpu.PSW] = cpu.cst(0x00000b80,32)
        p.state[cpu.PCXI] = cpu.cst(0,32)
        # map the stack area:
        _STK = 0x70000000-8192
        p.state.mmap.write(_STK,b'\0'*8192)
        p.state[cpu.sp] = cpu.cst(_STK+8192,32)
        # map the SSW functions as external symbols:
        self.load_ssw(p)
        self.tasks.append(p)
        return p

    def load_elf(self,bprm):
        p = Task(bprm, cpu)
        p.OS = self
        self.setup_mmio(p)
        # create text and data segments according to elf header:
        for s in p.bin.Phdr:
            ms = p.bin.loadsegment(s, 4096)
            if ms != None:
                vaddr, data = list(ms.items())[0]
                p.state.mmap.write(vaddr, data)
        # map the stack area:
        p.state.mmap.write(0x70000000-8192,b'\0'*8192)
        # map registers:
        p.state[cpu.PSW] = cpu.cst(0x00000b80,32)
        p.state[cpu.PCXI] = cpu.cst(0,32)
        p.state[cpu.sp] = cpu.cst(0x70000000,32)
        p.state[cpu.pc] = cpu.cst(p.bin.entrypoints[0],32)
        self.tasks.append(p)
        return p

    def load_ssw(self,mmap):
        pass

    def stub(self, refname):
        return self.stubs.get(refname, self.default_stub)


# ----------------------------------------------------------------------------

class Task(CoreExec):
    pass


# ----------------------------------------------------------------------------

@DefineStub(SSW, "FCE0")
def Flexibe_CRC_Engine(m, **kargs):
    pass

@DefineStub(SSW, "ASCLIN0")
@DefineStub(SSW, "ASCLIN1")
@DefineStub(SSW, "ASCLIN2")
@DefineStub(SSW, "ASCLIN3")
@DefineStub(SSW, "ASCLIN4")
@DefineStub(SSW, "ASCLIN5")
@DefineStub(SSW, "ASCLIN6")
@DefineStub(SSW, "ASCLIN7")
@DefineStub(SSW, "ASCLIN8")
@DefineStub(SSW, "ASCLIN9")
def Async_Serial_Controller_LIN(m, **kargs):
    pass


MEMMAP = [
    (0xF0000000, "FCE0"   , 512, "rw"),
    (0xF0000600, "ASCLIN0", 256, "rw"),
    (0xF0000700, "ASCLIN1", 256, "rw"),
    (0xF0000800, "ASCLIN2", 256, "rw"),
    (0xF0000900, "ASCLIN3", 256, "rw"),
    (0xF0000A00, "ASCLIN4", 256, "rw"),
    (0xF0000B00, "ASCLIN5", 256, "rw"),
    (0xF0000C00, "ASCLIN6", 256, "rw"),
    (0xF0000D00, "ASCLIN7", 256, "rw"),
    (0xF0000E00, "ASCLIN8", 256, "rw"),
    (0xF0000F00, "ASCLIN9", 256, "rw"),
]

