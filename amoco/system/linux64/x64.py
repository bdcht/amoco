# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.elf import *
from amoco.system.core import CoreExec, DefineStub
from amoco.code import tag
import amoco.arch.x64.cpu_x64 as cpu

# AMD 64 specific definitions. #x86_64 relocs.
with Consts("r_type"):
    R_X86_64_PLTOFF64 = 0x1F
    R_X86_64_GOTPCREL64 = 0x1C
    R_X86_64_GOTOFF64 = 0x19
    R_X86_64_TPOFF64 = 0x12
    R_X86_64_GOT32 = 0x3
    R_X86_64_32 = 0xA
    R_X86_64_DTPOFF64 = 0x11
    R_X86_64_PC32 = 0x2
    R_X86_64_16 = 0xC
    R_X86_64_32S = 0xB
    R_X86_64_TPOFF32 = 0x17
    R_X86_64_64 = 0x1
    R_X86_64_GOTPCREL = 0x9
    R_X86_64_TLSDESC = 0x24
    R_X86_64_TLSGD = 0x13
    R_X86_64_GOTPC32 = 0x1A
    R_X86_64_PC8 = 0xF
    R_X86_64_DTPOFF32 = 0x15
    R_X86_64_PLT32 = 0x4
    R_X86_64_8 = 0xE
    R_X86_64_GOTPC32_TLSDESC = 0x22
    R_X86_64_IRELATIVE = 0x25
    R_X86_64_PC16 = 0xD
    R_X86_64_COPY = 0x5
    R_X86_64_GLOB_DAT = 0x6
    R_X86_64_GOT64 = 0x1B
    R_X86_64_SIZE32 = 0x20
    R_X86_64_TLSLD = 0x14
    R_X86_64_JUMP_SLOT = 0x7
    R_X86_64_TLSDESC_CALL = 0x23
    R_X86_64_GOTTPOFF = 0x16
    R_X86_64_NUM = 0x27
    R_X86_64_SIZE64 = 0x21
    R_X86_64_GOTPC64 = 0x1D
    R_X86_64_PC64 = 0x18
    R_X86_64_RELATIVE64 = 0x26
    R_X86_64_RELATIVE = 0x8
    R_X86_64_NONE = 0x0
    R_X86_64_DTPMOD64 = 0x10
    R_X86_64_GOTPLT64 = 0x1E

# ------------------------------------------------------------------------------


class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of linux64.x64, the OS class will stub all libc
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
            stack_base = 0x00007FFFFFFFFFFF & ~(self.PAGESIZE - 1)
            stack_size = 2 * self.PAGESIZE
            p.state.mmap.write(stack_base - stack_size, b"\0" * stack_size)
            p.state[cpu.rsp] = cpu.cst(stack_base, 64)
        # create the dynamic segments:
        if bprm.dynamic and interp:
            self.load_elf_interp(p, interp)
        # return task:
        self.tasks.append(p)
        return p

    def load_elf_interp(self, p, interp):
        for k, f in p.bin._Elf__dynamic(None).items():
            xf = cpu.ext(f, size=64)
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
                    if target.base is p.cpu.rip:
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


class Task(CoreExec):
    pass


# ----------------------------------------------------------------------------


@DefineStub(OS, "*", default=True)
def pop_rip(m, **kargs):
    cpu.pop(m, cpu.rip)


@DefineStub(OS, "__libc_start_main")
def libc_start_main(m, **kargs):
    "tags: func_call"
    m[cpu.rip] = m(cpu.rdi)
    cpu.push(m, cpu.ext("exit", size=64))


@DefineStub(OS, "exit")
def libc_exit(m, **kargs):
    m[cpu.rip] = top(64)


@DefineStub(OS, "abort")
def libc_abort(m, **kargs):
    m[cpu.rip] = top(64)


@DefineStub(OS, "__assert")
def libc_assert(m, **kargs):
    m[cpu.rip] = top(64)


@DefineStub(OS, "__assert_fail")
def libc_assert_fail(m, **kargs):
    m[cpu.rip] = top(64)


@DefineStub(OS, "_assert_perror_fail")
def _assert_perror_fail(m, **kargs):
    m[cpu.rip] = top(64)


# ----------------------------------------------------------------------------
