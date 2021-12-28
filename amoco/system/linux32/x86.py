# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.elf import *
from amoco.system.core import CoreExec, DefineStub
from amoco.code import tag
import amoco.arch.x86.cpu_x86 as cpu

# Intel 80386 specific definitions. #i386 relocs.
with Consts("r_type"):
    R_386_NONE = 0
    R_386_32 = 1
    R_386_PC32 = 2
    R_386_GOT32 = 3
    R_386_PLT32 = 4
    R_386_COPY = 5
    R_386_GLOB_DAT = 6
    R_386_JMP_SLOT = 7
    R_386_RELATIVE = 8
    R_386_GOTOFF = 9
    R_386_GOTPC = 10
    R_386_32PLT = 11
    R_386_TLS_TPOFF = 14
    R_386_TLS_IE = 15
    R_386_TLS_GOTIE = 16
    R_386_TLS_LE = 17
    R_386_TLS_GD = 18
    R_386_TLS_LDM = 19
    R_386_16 = 20
    R_386_PC16 = 21
    R_386_8 = 22
    R_386_PC8 = 23
    R_386_TLS_GD_32 = 24
    R_386_TLS_GD_PUSH = 25
    R_386_TLS_GD_CALL = 26
    R_386_TLS_GD_POP = 27
    R_386_TLS_LDM_32 = 28
    R_386_TLS_LDM_PUSH = 29
    R_386_TLS_LDM_CALL = 30
    R_386_TLS_LDM_POP = 31
    R_386_TLS_LDO_32 = 32
    R_386_TLS_IE_32 = 33
    R_386_TLS_LE_32 = 34
    R_386_TLS_DTPMOD32 = 35
    R_386_TLS_DTPOFF32 = 36
    R_386_TLS_TPOFF32 = 37
    R_386_NUM = 38

# ------------------------------------------------------------------------------


class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of linux32.x86, the OS class will stub all libc
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
            stack_base = 0x7FFFFFFF & ~(self.PAGESIZE - 1)
            stack_size = 2 * self.PAGESIZE
            p.state.mmap.write(stack_base - stack_size, b"\0" * stack_size)
            p.state[cpu.esp] = cpu.cst(stack_base, 32)
        # create the dynamic segments:
        if bprm.dynamic and interp:
            self.load_elf_interp(p)
        # start task:
        self.tasks.append(p)
        return p

    def load_elf_interp(self, p):
        for k, f in p.bin._Elf__dynamic(None).items():
            xf = cpu.ext(f, size=32, task=p)
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
                    if target.base is p.cpu.eip:
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
def pop_eip(m, **kargs):
    cpu.pop(m, cpu.eip)


@DefineStub(OS, "__libc_start_main")
def libc_start_main(m, **kargs):
    "tags: func_call"
    m[cpu.eip] = m(cpu.mem(cpu.esp + 4, 32))
    x = cpu.ext("exit",size=32)
    x.stub = libc_exit
    cpu.push(m, x)


@DefineStub(OS, "exit")
def libc_exit(m, **kargs):
    m[cpu.eip] = cpu.top(32)


@DefineStub(OS, "abort")
def libc_abort(m, **kargs):
    m[cpu.eip] = cpu.top(32)


@DefineStub(OS, "__assert")
def libc_assert(m, **kargs):
    m[cpu.eip] = cpu.top(32)


@DefineStub(OS, "__assert_fail")
def libc_assert_fail(m, **kargs):
    m[cpu.eip] = cpu.top(32)


@DefineStub(OS, "_assert_perror_fail")
def _assert_perror_fail(m, **kargs):
    m[cpu.eip] = cpu.top(32)


# ----------------------------------------------------------------------------
