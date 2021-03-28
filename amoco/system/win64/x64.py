# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.pe import *
from amoco.system.core import CoreExec, DefineStub
from amoco.code import tag
import amoco.arch.x64.cpu_x64 as cpu

# ------------------------------------------------------------------------------

with Consts("COFFRelocation.Type"):
    IMAGE_REL_AMD64_ABSOLUTE = 0x0000
    IMAGE_REL_AMD64_ADDR64 = 0x0001
    IMAGE_REL_AMD64_ADDR32 = 0x0002
    IMAGE_REL_AMD64_ADDR32NB = 0x0003
    IMAGE_REL_AMD64_REL32 = 0x0004
    IMAGE_REL_AMD64_REL32_1 = 0x0005
    IMAGE_REL_AMD64_REL32_2 = 0x0006
    IMAGE_REL_AMD64_REL32_3 = 0x0007
    IMAGE_REL_AMD64_REL32_4 = 0x0008
    IMAGE_REL_AMD64_REL32_5 = 0x0009
    IMAGE_REL_AMD64_SECTION = 0x000A
    IMAGE_REL_AMD64_SECREL = 0x000B
    IMAGE_REL_AMD64_SECREL7 = 0x000C
    IMAGE_REL_AMD64_TOKEN = 0x000D
    IMAGE_REL_AMD64_SREL32 = 0x000E
    IMAGE_REL_AMD64_PAIR = 0x000F
    IMAGE_REL_AMD64_SSPAN32 = 0x0010


class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of win64.x64, the OS class will stub most NT API
    functions including a simulated heap memory allocator API.
    """

    stubs = {}
    default_stub = DefineStub.warning

    def __init__(self, conf=None):
        if conf is None:
            from amoco.config import System

            conf = System()
        self.PAGESIZE = conf.pagesize
        self.ASLR = conf.aslr
        self.NX = conf.nx
        self.tasks = []
        self.abi = None
        self.symbols = {}

    @classmethod
    def loader(cls, pe, conf=None):
        return cls(conf).load_pe_binary(pe)

    def load_pe_binary(self, pe):
        "load the program into virtual memory (populate the mmap dict)"
        p = Task(pe, cpu)
        p.OS = self
        # create text and data segments according to elf header:
        for s in pe.sections:
            ms = pe.loadsegment(s, pe.Opt.SectionAlignment)
            if ms != None:
                vaddr, data = ms.popitem()
                p.state.mmap.write(vaddr, data)
        # init task state:
        p.state[cpu.rip] = cpu.cst(p.bin.entrypoints[0], 64)
        p.state[cpu.rbp] = cpu.cst(0, 64)
        p.state[cpu.rax] = cpu.cst(0, 64)
        p.state[cpu.rbx] = cpu.cst(0, 64)
        p.state[cpu.rcx] = cpu.cst(0, 64)
        p.state[cpu.rdx] = cpu.cst(0, 64)
        p.state[cpu.rsi] = cpu.cst(0, 64)
        p.state[cpu.rdi] = cpu.cst(0, 64)
        p.state[cpu.r8] = cpu.cst(0, 64)
        p.state[cpu.r9] = cpu.cst(0, 64)
        p.state[cpu.r10] = cpu.cst(0, 64)
        p.state[cpu.r11] = cpu.cst(0, 64)
        p.state[cpu.r12] = cpu.cst(0, 64)
        p.state[cpu.r13] = cpu.cst(0, 64)
        p.state[cpu.r14] = cpu.cst(0, 64)
        p.state[cpu.r15] = cpu.cst(0, 64)
        p.state[cpu.rflags] = cpu.cst(0, 64)
        # create the stack space:
        if self.ASLR:
            p.state.mmap.newzone(p.cpu.rsp)
        else:
            ssz = pe.Opt.SizeOfStackReserve
            stack_base = 0x00007FFFFFFFFFFF & ~(self.PAGESIZE - 1)
            p.state.mmap.write(stack_base - ssz, b"\0" * ssz)
            p.state[cpu.rsp] = cpu.cst(stack_base, 64)
        # create the dynamic segments:
        if len(pe.functions) > 0:
            self.load_pe_iat(p)
        # start task:
        self.tasks.append(p)
        return p

    def load_pe_iat(self, p):
        for k, f in iter(p.bin.functions.items()):
            xf = cpu.ext(f, size=64, task=p)
            xf.stub = self.stub(xf.ref)
            p.state.mmap.write(k, xf)

    def stub(self, refname):
        return self.stubs.get(refname, self.default_stub)


# ------------------------------------------------------------------------------


class Task(CoreExec):
    pass


# ----------------------------------------------------------------------------

@DefineStub(OS, "*", default=True)
def pop_eip(m, **kargs):
    cpu.pop(m, cpu.rip)


@DefineStub(OS, "KERNEL32.dll::ExitProcess")
def ExitProcess(m, **kargs):
    m[cpu.rip] = cpu.top(64)

# ----------------------------------------------------------------------------
