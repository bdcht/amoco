# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.elf import *
from amoco.system.core import CoreExec, DefineStub
from amoco.code import tag
import amoco.arch.mips.cpu_r3000 as cpu


class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of linux32.mips, the OS class will stub all libc
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
        from .abi import cdecl

        self.abi = cdecl
        self.tasks = []
        self.symbols = {}

    @classmethod
    def loader(cls, bprm, conf=None):
        return cls(conf).load_elf_binary(bprm)

    def load_elf_binary(self, bprm):
        "load the program into virtual memory (populate the mmap dict)"
        p = Task(bprm, cpu)
        p.OS = self
        # create text and data segments according to elf header:
        for s in bprm.Phdr:
            if s.p_type == PT_INTERP:
                interp = bprm.readsegment(s).strip(b"\0")
            elif s.p_type == PT_LOAD:
                ms = bprm.loadsegment(s, self.PAGESIZE)
                if ms != None:
                    vaddr, data = ms.popitem()
                    p.state.mmap.write(vaddr, data)
            elif s.p_type == PT_GNU_STACK:
                # executable_stack = s.p_flags & PF_X
                pass
        # init task state registers:
        p.state[cpu.pc] = cpu.cst(p.bin.entrypoints[0], 32)
        p.state[cpu.npc] = p.state(cpu.pc+4)
        for r in cpu.registers:
            p.state[r] = cpu.cst(0, 32)
        # create the stack space:
        if self.ASLR:
            p.state.mmap.newzone(p.cpu.sp)
        else:
            stack_base = 0x7FFFFFFF & ~(self.PAGESIZE - 1)
            stack_size = 2 * self.PAGESIZE
            p.state.mmap.write(stack_base - stack_size, b"\0" * stack_size)
            p.state[cpu.sp] = cpu.cst(stack_base, 32)
        # create the dynamic segments:
        if bprm.dynamic and interp:
            self.load_elf_interp(p)
        # start task:
        self.tasks.append(p)
        return p

    def load_elf_interp(self, p):
        for k, f in p.bin._Elf__dynamic(None).items():
            xf = cpu.ext(f, size=32)
            xf.stub = self.stub(xf.ref)
            p.state.mmap.write(k, xf)
        # we want to add .plt addresses as symbols as well
        # to improve asm block views:
        plt = got = None
        for s in p.bin.Shdr:
            if s.name=='.plt':
                plt = s
            elif s.name=='.got':
                got = s
        if plt and got:
            address = plt.sh_addr
            pltco = p.bin.readsection(plt)
            while(pltco):
                i = p.cpu.disassemble(pltco)
                if i.mnemonic=='JMP' and i.operands[0]._is_mem:
                    target = i.operands[0].a
                    if target.base is p.cpu.pc:
                        target = address+target.disp
                    elif target.base._is_reg:
                        target = got.sh_addr+target.disp
                    elif target.base._is_cst:
                        target = target.base.value+target.disp
                    if target in p.bin.functions:
                        p.bin.functions[address] = p.bin.functions[target]
                pltco = pltco[i.length:]
                address += i.length

    def stub(self, refname):
        return self.stubs.get(refname, self.default_stub)


# ------------------------------------------------------------------------------


class Task(CoreExec):
    pass


# ----------------------------------------------------------------------------


@DefineStub(OS, "*", default=True)
def pop_pc(m, **kargs):
    m[cpu.pc] = m(cpu.lr)


@DefineStub(OS, "__libc_start_main")
def libc_start_main(m, **kargs):
    "tags: func_call"
    m[cpu.pc] = m(cpu.mem(cpu.sp + 4, 32))
    cpu.push(m, cpu.ext("exit", size=32))


@DefineStub(OS, "exit")
def libc_exit(m, **kargs):
    m[cpu.pc] = top(32)


@DefineStub(OS, "abort")
def libc_abort(m, **kargs):
    m[cpu.pc] = top(32)


@DefineStub(OS, "__assert")
def libc_assert(m, **kargs):
    m[cpu.pc] = top(32)


@DefineStub(OS, "__assert_fail")
def libc_assert_fail(m, **kargs):
    m[cpu.pc] = top(32)


@DefineStub(OS, "_assert_perror_fail")
def _assert_perror_fail(m, **kargs):
    m[cpu.pc] = top(32)


# ----------------------------------------------------------------------------
