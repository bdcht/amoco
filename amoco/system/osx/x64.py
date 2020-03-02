# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.macho import *
from amoco.system.core import CoreExec
from amoco.code import tag
import amoco.arch.x64.cpu_x64 as cpu

#------------------------------------------------------------------------------

class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of osx.x64, the OS class will stub all libc
    functions including a simulated heap memory allocator API.
    """
    stubs = {}
    default_stub = (lambda env,**kargs:None)

    def __init__(self,conf=None):
        if conf is None:
            from amoco.config import System
            conf = System()
        else:
            self.PAGESIZE = conf.pagesize
            self.ASLR     = conf.aslr
            self.NX       = conf.nx
        self.tasks = []
        self.abi = None

    @classmethod
    def loader(cls,bprm,conf=None):
        return cls(conf).load_macho_binary(bprm)

    def load_macho_binary(self,bprm):
        "load the program into virtual memory (populate the mmap dict)"
        p = Task(bprm,cpu)
        p.OS = self
        do_stack = False
        interp = None
        # do load commands:
        for s in bprm.cmds:
            if s.cmd == LC_LOAD_DYLINKER:
                interp = s.offset
            elif s.cmd == LC_SEGMENT_64:
                if s.segname.startswith(b'__PAGEZERO\0'):
                    continue
                data = bprm.readsegment(s).ljust(s.vmsize,b'\0')
                p.state.mmap.write(s.vmaddr,data)
            elif s.cmd in (LC_THREAD,LC_UNIXTHREAD):
                if s.flavor == x86_THREAD_STATE64:
                    for f in s.state.fields:
                        r = getattr(cpu,f.name)
                        p.state[r] = cpu.cst(s.state[f.name],r.size)
                    bprm.__entry = p.state[cpu.rip]
                if s.cmd==LC_UNIXTHREAD:
                    do_stack = True
                    stack_size = 2*self.PAGESIZE
            elif s.cmd == LC_MAIN:
                p.state[cpu.rip] = cpu.cst(s.entryoff,64)
                bprm.__entry = p.state[cpu.rip]
                if s.stacksize:
                    do_stack = True
                    stack_size = s.stacksize
        # create the stack space:
        if do_stack:
            if self.ASLR:
                p.state.mmap.newzone(p.cpu.rsp)
                p.state[cpu.rsp] = cpu.rsp
            else:
                stack_base = (0x00007fffffffffff & ~(self.PAGESIZE-1))
                p.state.mmap.write(stack_base-stack_size,b'\0'*stack_size)
                p.state[cpu.rsp] = cpu.cst(stack_base,64)

        # create the dynamic segments:
        if bprm.dynamic and interp:
            self.load_macho_interp(p,interp)
        # return task:
        self.tasks.append(p)
        return p

    def load_macho_interp(self,p,interp):
        for k,f in p.bin.la_symbol_ptr.items():
            xfunc = cpu.ext(f,size=64)
            xfunc.stub = p.OS.stub(f)
            p.state.mmap.write(k,xfunc)

    def stub(self,refname):
        return self.stubs.get(refname,self.default_stub)


class Task(CoreExec):

    # seqhelper provides arch-dependent information to amoco.main classes
    def seqhelper(self,seq):
        for i in seq:
            # some basic hints:
            if i.mnemonic.startswith('RET'):
                i.misc[tag.FUNC_END]=1
                continue
            elif i.mnemonic in ('PUSH','ENTER'):
                i.misc[tag.FUNC_STACK]=1
                if i.operands and i.operands[0] is cpu.rbp:
                    i.misc[tag.FUNC_START]=1
                    continue
            elif i.mnemonic in ('POP','LEAVE'):
                i.misc[tag.FUNC_UNSTACK]=1
                if i.operands and i.operands[0] is cpu.rbp:
                    i.misc[tag.FUNC_END]=1
                    continue
            # provide hints of absolute location from relative offset:
            elif i.mnemonic in ('CALL','JMP','Jcc'):
                if i.mnemonic == 'CALL':
                    i.misc[tag.FUNC_CALL]=1
                    i.misc['retto'] = i.address+i.length
                else:
                    i.misc[tag.FUNC_GOTO]=1
                    if i.mnemonic == 'Jcc':
                        i.misc['cond'] = i.cond
                if (i.address is not None) and i.operands[0]._is_cst:
                    v = i.address+i.operands[0].signextend(64)+i.length
                    x = self.check_sym(v)
                    if x is not None: v=x
                    i.misc['to'] = v
                    if i.misc[tag.FUNC_CALL] and i.misc['retto']==v:
                        # this looks like a fake call
                        i.misc[tag.FUNC_CALL]=-1
                    continue
            # check operands (globals & .got calls):
            for op in i.operands:
                if op._is_mem:
                    if op.a.base is cpu.rbp:
                        if   op.a.disp<0: i.misc[tag.FUNC_VAR]=True
                        elif op.a.disp>=16: i.misc[tag.FUNC_ARG]=True
                    elif op.a.base._is_cst or (op.a.base is cpu.rip):
                        b = op.a.base
                        if b is cpu.rip: b=i.address+i.length
                        x = self.check_sym(b+op.a.disp)
                        if x is not None:
                            op.a.base=x
                            op.a.disp=0
                            if i.mnemonic == 'JMP': # PLT jumps:
                                i.misc[tag.FUNC_START]=1
                                i.misc[tag.FUNC_END]=1
                elif op._is_cst:
                    x = self.check_sym(op)
                    i.misc['imm_ref'] = x
        return seq

    def blockhelper(self,block):
        block._helper = block_helper_
        return CoreExec.blockhelper(self,block)

    def funchelper(self,f):
        # check single root node:
        roots = f.cfg.roots()
        if len(roots)==0:
            roots = filter(lambda n:n.data.misc[tag.FUNC_START],f.cfg.sV)
            if len(roots)==0:
                logger.warning("no entry to function %s found"%f)
        if len(roots)>1:
            logger.verbose('multiple entries into function %s ?!'%f)
        # check start symbol:
        elif roots[0].data.address == self.bin.entrypoints[0]:
            f.name = '_start'
        # get section symbol if any:
        f.misc['section'] = section = self.bin.getinfo(f.address.value)[0]
        rets = f.cfg.leaves()
        if len(rets)==0:
            logger.warning("no exit to function %s found"%f)
        if len(rets)>1:
            logger.verbose('multiple exits in function %s'%f)
        for r in rets:
           # export PLT external symbol name:
            if section and section.name=='.plt':
                if isinstance(r.data,xfunc): f.name = section.name+r.name
            if r.data.misc[tag.FUNC_CALL]:
                f.misc[tag.FUNC_CALL] += 1
        if f.map:
        # check vars & args: should reflect x64 register calling convention
            f.misc[tag.FUNC_VAR] = []
            f.misc[tag.FUNC_ARG] = []
            for x in set(f.map.inputs()):
                f.misc[tag.FUNC_IN] += 1
                if x._is_mem and x.a.base==cpu.rsp:
                    if x.a.disp>=8:
                        f.misc[tag.FUNC_ARG].append(x)
            for x in set(f.map.outputs()):
                if x in (cpu.rsp, cpu.rbp): continue
                f.misc[tag.FUNC_OUT] += 1
                if x._is_mem and x.a.base==cpu.rsp:
                    if x.a.disp<0:
                        f.misc[tag.FUNC_VAR].append(x)


def block_helper_(block,m):
    # annotations based on block semantics:
    sta,sto = block.support
    if m[cpu.mem(cpu.rbp-8,64)] == cpu.rbp:
        block.misc[tag.FUNC_START]=1
    if m[cpu.rip]==cpu.mem(cpu.rsp-8,64):
        block.misc[tag.FUNC_END]=1
    if m[cpu.mem(cpu.rsp,64)]==sto:
        block.misc[tag.FUNC_CALL]=1

#----------------------------------------------------------------------------

# STUBS DEFINED HERE :
#----------------------------------------------------------------------------

from amoco.system.core import DefineStub

@DefineStub(OS,'*',default=True)
def pop_rip(m,**kargs):
    cpu.pop(m,cpu.rip)

@DefineStub(OS,'__libc_start_main')
def libc_start_main(m,**kargs):
    "tags: func_call"
    m[cpu.rip] = m(cpu.rdi)
    cpu.push(m,cpu.ext('exit',size=64))

@DefineStub(OS,'exit')
def libc_exit(m,**kargs):
    m[cpu.rip] = top(64)
@DefineStub(OS,'abort')
def libc_abort(m,**kargs):
    m[cpu.rip] = top(64)
@DefineStub(OS,'__assert')
def libc_assert(m,**kargs):
    m[cpu.rip] = top(64)
@DefineStub(OS,'__assert_fail')
def libc_assert_fail(m,**kargs):
    m[cpu.rip] = top(64)
@DefineStub(OS,'_assert_perror_fail')
def _assert_perror_fail(m,**kargs):
    m[cpu.rip] = top(64)

#----------------------------------------------------------------------------

