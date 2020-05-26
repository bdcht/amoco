# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.pe import *
from amoco.system.core import CoreExec, DefineStub
from amoco.code import tag
import amoco.arch.x86.cpu_x86 as cpu

# ------------------------------------------------------------------------------


class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of win32.x86, the OS class will stub most NT API
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
        p.state[cpu.eip] = cpu.cst(p.bin.entrypoints[0], 32)
        p.state[cpu.ebp] = cpu.cst(0, 32)
        p.state[cpu.eax] = cpu.cst(0, 32)
        p.state[cpu.ebx] = cpu.cst(0, 32)
        p.state[cpu.ecx] = cpu.cst(0, 32)
        p.state[cpu.edx] = cpu.cst(0, 32)
        p.state[cpu.esi] = cpu.cst(0, 32)
        p.state[cpu.edi] = cpu.cst(0, 32)
        # create the stack space:
        if self.ASLR:
            p.state.mmap.newzone(p.cpu.esp)
        else:
            ssz = pe.Opt.SizeOfStackReserve
            stack_base = 0x7FFFFFFF & ~(self.PAGESIZE - 1)
            p.state.mmap.write(stack_base - ssz, b"\0" * ssz)
            p.state[cpu.esp] = cpu.cst(stack_base, 32)
        # create the dynamic segments:
        if len(pe.functions) > 0:
            self.load_pe_iat(p)
        # start task:
        self.tasks.append(p)
        return p

    def load_pe_iat(self, p):
        for k, f in iter(p.bin.functions.items()):
            xf = cpu.ext(f, size=32)
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
    cpu.pop(m, cpu.eip)


@DefineStub(OS, "KERNEL32.dll::ExitProcess")
def ExitProcess(m, **kargs):
    m[cpu.eip] = cpu.top(32)

# ----------------------------------------------------------------------------
