# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2007 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import *
from amoco.code import tag

import amoco.arch.x86.cpu_x86 as cpu

PAGESIZE = 4096

class PE(CoreExec):

    def __init__(self,p):
        CoreExec.__init__(self,p,cpu)

    def load_binary(self):
        p = self.bin
        if p!=None:
            # create text and data segments according to PE headers:
            base,headers = p.loadsegment(0).popitem()
            self.mmap.write(base,headers) # load Headers
            for s in p.sections:          # load other Sections
                ms = p.loadsegment(s,PAGESIZE)
                if ms!=None:
                    vaddr,data = ms.popitem()
                    self.mmap.write(vaddr,data)
            # create the dynamic segments:
            self.load_shlib()
        # create the stack zone:
        self.mmap.newzone(cpu.esp)

    # call dynamic linker to populate mmap with shared libs:
    # for now, the external libs are seen through the elf dynamic section:
    def load_shlib(self):
        for k,f in self.bin.functions.iteritems():
            self.mmap.write(k,cpu.ext(f,size=32))

    def initenv(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        for k,v in ((cpu.eip, cpu.cst(self.bin.entrypoints[0],32)),
                    (cpu.ebp, cpu.cst(0,32)),
                    (cpu.eax, cpu.cst(0,32)),
                    (cpu.ebx, cpu.cst(0,32)),
                    (cpu.ecx, cpu.cst(0,32)),
                    (cpu.edx, cpu.cst(0,32)),
                    (cpu.esi, cpu.cst(0,32)),
                    (cpu.edi, cpu.cst(0,32))):
            m[k] = v
        return m

    # lookup in bin if v is associated with a function or variable name:
    def check_sym(self,v):
        if v._is_cst:
            x = self.bin.functions.get(v.value,None) or self.bin.variables.get(v.value,None)
            if x is not None:
                if isinstance(x,str): x=cpu.ext(x,size=32)
                else: x=cpu.sym(x[0],v.value,v.size)
                return x
        return None

    def codehelper(self,**kargs):
        if 'seq' in kargs: return self.seqhelper(kargs['seq'])
        if 'block' in kargs: return self.blockhelper(kargs['block'])
        if 'func' in kargs: return self.funchelper(kargs['func'])

    # seqhelper provides arch-dependent information to amoco.main classes
    def seqhelper(self,seq):
        for i in seq:
            # some basic hints:
            if i.mnemonic.startswith('RET'):
                i.misc[tag.FUNC_END]=1
                continue
            elif i.mnemonic in ('PUSH','ENTER'):
                i.misc[tag.FUNC_STACK]=1
                if i.operands and i.operands[0] is cpu.ebp:
                    i.misc[tag.FUNC_START]=1
                    continue
            elif i.mnemonic in ('POP','LEAVE'):
                i.misc[tag.FUNC_UNSTACK]=1
                if i.operands and i.operands[0] is cpu.ebp:
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
                    v = i.address+i.operands[0].signextend(32)+i.length
                    x = self.check_sym(v)
                    if x is not None: v=x
                    i.misc['to'] = v
                    continue
            # check operands (globals & .got calls):
            for op in i.operands:
                if op._is_mem:
                    if op.a.base is cpu.ebp:
                        if   op.a.disp<0: i.misc[tag.FUNC_ARG]=1
                        elif op.a.disp>4: i.misc[tag.FUNC_VAR]=1
                    elif op.a.base._is_cst:
                        x = self.check_sym(op.a.base)
                        if x is not None: op.a.base=x
                elif op._is_cst:
                    x = self.check_sym(op)
                    i.misc['imm_ref'] = x
        return seq

    def blockhelper(self,block):
        for i in self.seqhelper(block):
            block.misc.update(i.misc)
        def _helper(block,m):
            # update block.misc based on semantics:
            sta,sto = block.support
            if m[cpu.mem(cpu.ebp-4,32)] == cpu.ebp:
                block.misc[tag.FUNC_START]=1
            if m[cpu.eip]==cpu.mem(cpu.esp-4,32):
                block.misc[tag.FUNC_END]=1
            if m[cpu.mem(cpu.esp,32)]==sto:
                block.misc[tag.FUNC_CALL]=1
        # register the block helper that will be called
        # only when the map is computed.
        block._helper = _helper
        return block

    def funchelper(self,f):
        roots = f.cfg.roots()
        if len(roots)==0:
            roots = filter(lambda n:n.data.misc[tag.FUNC_START],f.cfg.sV)
            if len(roots)==0:
                logger.warning("no entry to function %s found"%f)
        if len(roots)>1:
            logger.verbose('multiple entries into function %s ?!'%f)
        rets = f.cfg.leaves()
        if len(rets)==0:
            logger.warning("no exit to function %s found"%f)
        if len(rets)>1:
            logger.verbose('multiple exits in function %s'%f)
        for r in rets:
            if r.data.misc[tag.FUNC_CALL]: f.misc[tag.FUNC_CALL] += 1


# HOOKS DEFINED HERE :
#----------------------------------------------------------------------------

@stub_default
def pop_eip(m,**kargs):
    cpu.pop(m,cpu.eip)


