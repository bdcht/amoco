# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.pe import *
from amoco.system.core import CoreExec
from amoco.code import tag, xfunc
import amoco.arch.x64.cpu_x64 as cpu

# ------------------------------------------------------------------------------


class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of win64.x64, the OS class will stub most NT API
    functions including a simulated heap memory allocator API.
    """

    stubs = {}
    default_stub = lambda env, **kargs: None

    def __init__(self, conf=None):
        if conf is None:
            from amoco.config import System

            conf = System()
        self.PAGESIZE = conf.pagesize
        self.ASLR = conf.aslr
        self.NX = conf.nx
        self.tasks = []

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
        p.state[cpu.rip] = cpu.cst(pe.Opt.AddressOfEntryPoint, 64)
        p.state[cpu.rbp] = cpu.cst(0, 64)
        p.state[cpu.rax] = cpu.cst(0, 64)
        p.state[cpu.rbx] = cpu.cst(0, 64)
        p.state[cpu.rcx] = cpu.cst(0, 64)
        p.state[cpu.rdx] = cpu.cst(0, 64)
        p.state[cpu.rsi] = cpu.cst(0, 64)
        p.state[cpu.rdi] = cpu.cst(0, 64)
        # create the stack space:
        if self.ASLR:
            p.state.mmap.newzone(p.cpu.rsp)
        else:
            ssz = pe.Opt.SizeOfStackReserve
            stack_base = 0x00007FFFFFFFFFFF & ~(self.PAGESIZE - 1)
            p.state.mmap.write(stack_base - ssz, b"\0" * ssz)
            p.state[cpu.esp] = cpu.cst(stack_base, 64)
        # create the dynamic segments:
        if len(pe.functions) > 0:
            self.load_pe_iat(p)
        # start task:
        self.tasks.append(p)
        return p

    def load_pe_iat(self, p):
        for k, f in iter(p.bin.functions.items()):
            xf = cpu.ext(f, size=64)
            xf.stub = p.OS.stub(f)
            p.state.mmap.write(k, xf)

    def stub(self, refname):
        return self.stubs.get(refname, self.default_stub)


# ------------------------------------------------------------------------------


class Task(CoreExec):

    # seqhelper provides arch-dependent information to amoco.main classes
    def seqhelper(self, seq):
        for i in seq:
            # some basic hints:
            if i.mnemonic.startswith("RET"):
                i.misc[tag.FUNC_END] = 1
                continue
            elif i.mnemonic in ("PUSH", "ENTER"):
                i.misc[tag.FUNC_STACK] = 1
                if i.operands and i.operands[0] is cpu.rbp:
                    i.misc[tag.FUNC_START] = 1
                    continue
            elif i.mnemonic in ("POP", "LEAVE"):
                i.misc[tag.FUNC_UNSTACK] = 1
                if i.operands and i.operands[0] is cpu.rbp:
                    i.misc[tag.FUNC_END] = 1
                    continue
            # provide hints of absolute location from relative offset:
            elif i.mnemonic in ("CALL", "JMP", "Jcc"):
                if i.mnemonic == "CALL":
                    i.misc[tag.FUNC_CALL] = 1
                    i.misc["retto"] = i.address + i.length
                else:
                    i.misc[tag.FUNC_GOTO] = 1
                    if i.mnemonic == "Jcc":
                        i.misc["cond"] = i.cond
                if (i.address is not None) and i.operands[0]._is_cst:
                    v = i.address + i.operands[0].signextend(64) + i.length
                    x = self.check_sym(v)
                    if x is not None:
                        v = x
                    i.misc["to"] = v
                    if i.misc[tag.FUNC_CALL] and i.misc["retto"] == v:
                        # this looks like a fake call
                        i.misc[tag.FUNC_CALL] = -1
                    continue
            # check operands (globals & .got calls):
            for op in i.operands:
                if op._is_mem:
                    if op.a.base is cpu.rbp:
                        if op.a.disp < 0:
                            i.misc[tag.FUNC_VAR] = True
                        elif op.a.disp >= 8:
                            i.misc[tag.FUNC_ARG] = True
                    elif op.a.base._is_cst:
                        x = self.check_sym(op.a.base + op.a.disp)
                        if x is not None:
                            op.a.base = x
                            op.a.disp = 0
                            if i.mnemonic == "JMP":  # PLT jumps:
                                i.misc[tag.FUNC_START] = 1
                                i.misc[tag.FUNC_END] = 1
                elif op._is_cst:
                    x = self.check_sym(op)
                    i.misc["imm_ref"] = x
        return seq

    def blockhelper(self, block):
        block._helper = block_helper_
        return CoreExec.blockhelper(self, block)

    def funchelper(self, f):
        # check single root node:
        roots = f.cfg.roots()
        if len(roots) == 0:
            roots = filter(lambda n: n.data.misc[tag.FUNC_START], f.cfg.sV)
            if len(roots) == 0:
                logger.warning("no entry to function %s found" % f)
        if len(roots) > 1:
            logger.verbose("multiple entries into function %s ?!" % f)
        # check _start symbol:
        elif roots[0].data.address == self.bin.entrypoints[0]:
            f.name = "_start"
        # get section symbol if any:
        f.misc["section"] = section = self.bin.getinfo(f.address.value)[0]
        # check leaves:
        rets = f.cfg.leaves()
        if len(rets) == 0:
            logger.warning("no exit to function %s found" % f)
        if len(rets) > 1:
            logger.verbose("multiple exits in function %s" % f)
        for r in rets:
            # export PLT external symbol name:
            if section and section.name == ".plt":
                if isinstance(r.data, xfunc):
                    f.name = section.name + r.name
            if r.data.misc[tag.FUNC_CALL]:
                f.misc[tag.FUNC_CALL] += 1
        if f.map:
            # check vars & args:
            f.misc[tag.FUNC_VAR] = []
            f.misc[tag.FUNC_ARG] = []
            for x in set(f.map.inputs()):
                f.misc[tag.FUNC_IN] += 1
                if x._is_mem and x.a.base == cpu.rsp:
                    if x.a.disp >= 8:
                        f.misc[tag.FUNC_ARG].append(x)
            for x in set(f.map.outputs()):
                if x in (cpu.rsp, cpu.rbp):
                    continue
                f.misc[tag.FUNC_OUT] += 1
                if x._is_mem and x.a.base == cpu.rsp:
                    if x.a.disp < 0:
                        f.misc[tag.FUNC_VAR].append(x)


# ----------------------------------------------------------------------------
# the block helper that will be called
# only when the map is computed.
def block_helper_(block, m):
    # update block.misc based on semantics:
    sta, sto = block.support
    if m[cpu.mem(cpu.rbp - 8, 64)] == cpu.rbp:
        block.misc[tag.FUNC_START] = 1
    if m[cpu.rip] == cpu.mem(cpu.rsp - 8, 64):
        block.misc[tag.FUNC_END] = 1
    if m[cpu.mem(cpu.rsp, 64)] == sto:
        block.misc[tag.FUNC_CALL] = 1


# STUBS DEFINED HERE :
# ----------------------------------------------------------------------------

from amoco.system.core import DefineStub


@DefineStub(OS, "*", default=True)
def pop_eip(m, **kargs):
    cpu.pop(m, cpu.rip)


@DefineStub(OS, "KERNEL32.dll::ExitProcess")
def ExitProcess(m, **kargs):
    m[cpu.rip] = cpu.top(64)


# ----------------------------------------------------------------------------
