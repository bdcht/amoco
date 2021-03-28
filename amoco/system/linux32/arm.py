# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.elf import *
from amoco.system.core import CoreExec, DefineStub
import amoco.arch.arm.cpu_armv7 as cpu

with Consts("e_flags"):
    EF_ARM_EABI_UNKNOWN = 0x0
    EF_ARM_SOFT_FLOAT = 0x200
    EF_ARM_ALIGN8 = 0x40
    EF_ARM_NEW_ABI = 0x80
    EF_ARM_APCS_FLOAT = 0x10
    EF_ARM_SYMSARESORTED = 0x4
    EF_ARM_OLD_ABI = 0x100
    EF_ARM_INTERWORK = 0x4
    EF_ARM_ABI_FLOAT_SOFT = 0x200
    EF_ARM_EABI_VER5 = 0x5000000
    EF_ARM_EABI_VER2 = 0x2000000
    EF_ARM_ABI_FLOAT_HARD = 0x400
    EF_ARM_VFP_FLOAT = 0x400
    EF_ARM_HASENTRY = 0x2
    EF_ARM_LE8 = 0x400000
    EF_ARM_DYNSYMSUSESEGIDX = 0x8
    EF_ARM_EABI_VER1 = 0x1000000
    EF_ARM_EABI_VER4 = 0x4000000
    EF_ARM_EABI_VER3 = 0x3000000
    EF_ARM_BE8 = 0x800000
    EF_ARM_PIC = 0x20
    EF_ARM_MAPSYMSFIRST = 0x10
    EF_ARM_MAVERICK_FLOAT = 0x800
    EF_ARM_APCS_26 = 0x8
    EF_ARM_EABIMASK = 0xFF000000
    EF_ARM_RELEXEC = 0x1

with Consts("r_type"):
    R_ARM_GNU_VTENTRY = 0x64
    R_ARM_THM_ABS5 = 0x7
    R_ARM_XPC25 = 0xF
    R_ARM_TLS_IE12GP = 0x6F
    R_ARM_LDR_PC_G1 = 0x3E
    R_ARM_THM_PC22 = 0xA
    R_ARM_ALU_PC_G0_NC = 0x39
    R_ARM_GOT_ABS = 0x5F
    R_ARM_ABS16 = 0x5
    R_ARM_ABS12 = 0x6
    R_ARM_GOT_BREL12 = 0x61
    R_ARM_THM_TLS_DESCSEQ32 = 0x82
    R_ARM_PLT32 = 0x1B
    R_ARM_ALU_SBREL_27_20 = 0x25
    R_ARM_ABS32_NOI = 0x37
    R_ARM_THM_ALU_PREL_11_0 = 0x35
    R_ARM_RREL32 = 0xFC
    R_ARM_GOTOFF12 = 0x62
    R_ARM_ALU_PCREL_23_15 = 0x22
    R_ARM_AMP_VCALL9 = 0xC
    R_ARM_THM_MOVW_ABS_NC = 0x2F
    R_ARM_REL32_NOI = 0x38
    R_ARM_TLS_LE32 = 0x6C
    R_ARM_LDC_SB_G1 = 0x52
    R_ARM_SBREL31 = 0x27
    R_ARM_ALU_PCREL_15_8 = 0x21
    R_ARM_ALU_SB_G2 = 0x4A
    R_ARM_ALU_SB_G1_NC = 0x48
    R_ARM_MOVW_PREL_NC = 0x2D
    R_ARM_THM_PC8 = 0xB
    R_ARM_TLS_GOTDESC = 0x5A
    R_ARM_JUMP_SLOT = 0x16
    R_ARM_TLS_CALL = 0x5B
    R_ARM_NONE = 0x0
    R_ARM_RABS22 = 0xFD
    R_ARM_PREL31 = 0x2A
    R_ARM_GOTRELAX = 0x63
    R_ARM_ALU_PC_G0 = 0x3A
    R_ARM_BASE_ABS = 0x1F
    R_ARM_LDRS_SB_G0 = 0x4E
    R_ARM_LDRS_SB_G2 = 0x50
    R_ARM_TARGET2 = 0x29
    R_ARM_TLS_DESC = 0xD
    R_ARM_THM_TLS_DESCSEQ = 0x81
    R_ARM_RELATIVE = 0x17
    R_ARM_ABS8 = 0x8
    R_ARM_REL32 = 0x3
    R_ARM_RXPC25 = 0xF9
    R_ARM_LDC_PC_G2 = 0x45
    R_ARM_TLS_DTPOFF32 = 0x12
    R_ARM_ALU_SB_G0 = 0x47
    R_ARM_THM_GOT_BREL12 = 0x83
    R_ARM_THM_MOVT_PREL = 0x32
    R_ARM_MOVT_PREL = 0x2E
    R_ARM_COPY = 0x14
    R_ARM_ALU_PC_G2 = 0x3D
    R_ARM_LDR_PC_G2 = 0x3F
    R_ARM_TLS_LDO12 = 0x6D
    R_ARM_GLOB_DAT = 0x15
    R_ARM_THM_MOVW_PREL_NC = 0x31
    R_ARM_THM_XPC22 = 0x10
    R_ARM_LDC_SB_G0 = 0x51
    R_ARM_MOVT_ABS = 0x2C
    R_ARM_RPC24 = 0xFE
    R_ARM_THM_TLS_DESCSEQ16 = 0x81
    R_ARM_ALU_SBREL_19_12 = 0x24
    R_ARM_ALU_SB_G1 = 0x49
    R_ARM_ALU_PC_G1 = 0x3C
    R_ARM_V4BX = 0x28
    R_ARM_ALU_PC_G1_NC = 0x3B
    R_ARM_GOT_PREL = 0x60
    R_ARM_THM_JUMP6 = 0x34
    R_ARM_LDC_PC_G0 = 0x43
    R_ARM_LDR_SB_G2 = 0x4D
    R_ARM_IRELATIVE = 0xA0
    R_ARM_ABS32 = 0x2
    R_ARM_TLS_TPOFF32 = 0x13
    R_ARM_ME_TOO = 0x80
    R_ARM_GNU_VTINHERIT = 0x65
    R_ARM_PC24 = 0x1
    R_ARM_LDRS_PC_G1 = 0x41
    R_ARM_MOVW_BREL_NC = 0x54
    R_ARM_ALU_SB_G0_NC = 0x46
    R_ARM_THM_JUMP19 = 0x33
    R_ARM_THM_JUMP24 = 0x1E
    R_ARM_PLT32_ABS = 0x5E
    R_ARM_LDR_SB_G1 = 0x4C
    R_ARM_LDRS_PC_G0 = 0x40
    R_ARM_THM_MOVW_BREL = 0x59
    R_ARM_THM_RPC22 = 0xFB
    R_ARM_TLS_DTPMOD32 = 0x11
    R_ARM_RBASE = 0xFF
    R_ARM_RSBREL32 = 0xFA
    R_ARM_CALL = 0x1C
    R_ARM_THM_PC11 = 0x66
    R_ARM_MOVT_BREL = 0x55
    R_ARM_LDRS_PC_G2 = 0x42
    R_ARM_GOTOFF = 0x18
    R_ARM_ALU_PCREL_7_0 = 0x20
    R_ARM_PC13 = 0x4
    R_ARM_THM_PC12 = 0x36
    R_ARM_MOVW_BREL = 0x56
    R_ARM_THM_MOVW_BREL_NC = 0x57
    R_ARM_LDC_SB_G2 = 0x53
    R_ARM_TLS_LDO32 = 0x6A
    R_ARM_GOT32 = 0x1A
    R_ARM_LDR_SBREL_11_0 = 0x23
    R_ARM_LDRS_SB_G1 = 0x4F
    R_ARM_THM_SWI8 = 0xE
    R_ARM_THM_MOVT_ABS = 0x30
    R_ARM_MOVW_ABS_NC = 0x2B
    R_ARM_TARGET1 = 0x26
    R_ARM_THM_MOVT_BREL = 0x58
    R_ARM_JUMP24 = 0x1D
    R_ARM_THM_PC9 = 0x67
    R_ARM_NUM = 0x100
    R_ARM_LDR_SB_G0 = 0x4B
    R_ARM_TLS_LE12 = 0x6E
    R_ARM_LDC_PC_G1 = 0x44
    R_ARM_SBREL32 = 0x9
    R_ARM_TLS_IE32 = 0x6B
    R_ARM_SWI24 = 0xD
    R_ARM_TLS_GD32 = 0x68
    R_ARM_TLS_LDM32 = 0x69
    R_ARM_GOTPC = 0x19
    R_ARM_TLS_DESCSEQ = 0x5C
    R_ARM_THM_TLS_CALL = 0x5D

# ------------------------------------------------------------------------------


class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of linux32.arm, the OS class will stub all libc
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
        self.abi = None
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
        # init task state:
        for r in cpu.regs:
            p.state[r] = cpu.cst(0, 32)
        entry = cpu.cst(p.bin.entrypoints[0], 32)
        p.setx(cpu.pc_,entry)
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
            self.load_elf_interp(p, interp)
        # start task:
        self.tasks.append(p)
        return p

    def load_elf_interp(self, p, interp):
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
            address = p.cpu.cst(plt.sh_addr,32)
            thunk = address.value
            pltco = p.bin.readsection(plt)
            # we assume that plt code is not in Thumb...
            mode = p.cpu.internals['isetstate']
            p.cpu.internals['isetstate']=0
            m = None
            while(pltco):
                i = p.cpu.disassemble(pltco)
                if i is None:
                    pltco = pltco[4:]
                    address += 4
                    continue
                if i.mnemonic=='ADR':
                   thunk = address.value
                   m = p.state.__class__()
                   m[p.cpu.pc_] = address
                   m[p.cpu.pc] = address + 4
                if m is not None:
                    i(m)
                    target = p.state(m(p.cpu.pc))
                    if target._is_ext:
                        p.bin.functions[thunk] = target.ref
                pltco = pltco[i.length:]
                address += i.length
            #restore mode:
            p.cpu.internals['isetstate']=mode

    def stub(self, refname):
        return self.stubs.get(refname, self.default_stub)


class Task(CoreExec):

    def title_info(self):
        return [{0:"ARM32", 1:"THUMB"}[self.cpu.internals['isetstate']]]

    def setx(self, loc, val, size=0):
        pc = self.cpu.PC()
        if isinstance(loc, str):
            x = getattr(self.cpu, loc)
            size = x.size
        elif isinstance(loc, int):
            endian = self.cpu.get_data_endian()
            psz = pc.size
            x = self.cpu.mem(self.cpu.cst(loc, psz), size, endian=endian)
        else:
            x = loc
            size = x.size
        if isinstance(val, bytes):
            if x._is_mem:
                x.size = len(val) if size == 0 else size
                self.state._Mem_write(x.a, val)
                return
            else:
                endian = self.cpu.get_data_endian()
                v = self.cpu.cst(
                    Bits(val[0 : x.size : endian], bitorder=1).int(), x.size * 8
                )
        elif isinstance(val, int):
            v = self.cpu.cst(val, size)
        else:
            v = val
        if x == pc and v[0:1] == 1:
            self.cpu.internals["isetstate"] = 1
            v = (v >> 1) << 1
        self.state[x] = v


# ----------------------------------------------------------------------------

@DefineStub(OS, "*", default=True)
def nullstub(m, **kargs):
    m[cpu.pc_] = m(cpu.lr)


@DefineStub(OS, "__libc_start_main")
def libc_start_main(m, **kargs):
    "tags: func_call"
    m[cpu.pc_] = m(cpu.r0)


@DefineStub(OS, "exit")
def libc_exit(m, **kargs):
    m[cpu.pc_] = top(32)


@DefineStub(OS, "abort")
def libc_abort(m, **kargs):
    m[cpu.pc_] = top(32)


@DefineStub(OS, "__assert")
def libc_assert(m, **kargs):
    m[cpu.pc_] = top(32)


@DefineStub(OS, "__assert_fail")
def libc_assert_fail(m, **kargs):
    m[cpu.pc_] = top(32)


@DefineStub(OS, "_assert_perror_fail")
def _assert_perror_fail(m, **kargs):
    m[cpu.pc_] = top(32)


@DefineStub(OS, "printf")
@DefineStub(OS, "__printf_chk")
def libc_printf(m, **kargs):
    task = kargs.get('task',None)
    if task:
        res, args = task.OS.abi(m)
        fmt = task.get_cstr(args[0])
        print(fmt)
    m[cpu.pc_] = m(cpu.lr)


