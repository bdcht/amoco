# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2016-2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
.. _emu:

emu.py
======
The emu module of amoco implements the emulator class :class:`emul`.

"""

from collections import deque

from amoco.config import conf
from amoco.arch.core import DecodeError
from amoco.sa import lsweep
from amoco.ui.views import emulView
from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading emu")

class EmulError(Exception):
    pass


class emul(object):
    def __init__(self, task):
        self.task = task
        self.cpu = task.cpu
        self.pc = task.cpu.PC()
        self.psz = self.pc.size
        self.hooks = []
        self.watch = {}
        self.handlers = {}
        if task.OS is not None:
            self.abi = task.OS.abi
        else:
            self.abi = None
        self.sa = lsweep(task)
        self.hist = deque(maxlen=conf.Emu.hist)
        self.view = emulView(self)
        self.handlers[EmulError] = self.stop
        self.handlers[DecodeError] = self.stop

    def stepi(self,trace=False):
        addr = self.task.state(self.pc)
        if addr._is_top:
            logger.warning("%s has reached top value")
            raise EmulError()
        i = self.task.read_instruction(addr)
        if i is not None:
            if trace:
                ops_v = [(self.task.state(o),o) for o in i.operands]
                i.misc['trace'] = ops_v
            self.task.state.safe_update(i)
            self.hist.append(i)
            if i.misc.get('delayed',False):
                islot = self.task.read_instruction(addr+i.length)
                if trace:
                    ops_v = [(self.task.state(o),o) for o in islot.operands]
                    islot.misc['trace'] = ops_v
                self.task.state.safe_update(islot)
                self.hist.append(islot)
        else:
            raise DecodeError(addr)
        return i

    def iterate(self,trace=False):
        lasti = None
        while True:
            status,reason = self.checkstate(lasti)
            if status:
                logger.info("stop iteration due to %s"%reason.__doc__)
                break
            try:
                addr = self.task.state(self.pc)
                if addr._is_top:
                    raise EmulError()
                print("%s: %s"%(type(addr),addr))
                lasti = i = self.task.read_instruction(addr)
                if trace:
                    ops_v = [(self.task.state(o),o) for o in i.operands]
                    i.misc['trace'] = ops_v
                self.task.state.update(i)
                self.hist.append(i)
                if trace:
                    yield lasti,ops_v
                else:
                    yield lasti
            except Exception as e:
                lasti = None
                # we break only if the handler returns False:
                if not self.exception_handler(e):
                    break

    def exception_handler(self, e):
        te = type(e)
        logger.verbose("exception %s received" % te)
        if te in self.handlers:
            return self.handlers[te](self, e)
        raise (e)

    def checkstate(self, prev=None):
        """returns True iff the current state matches a condition that stops
           iterations of instructions. Breakpoints typically return True.
        """
        res = False
        who = None
        if prev is not None:
            for f in self.hooks:
                res |= f(self, prev)
                if res == True:
                    who = f
                    break
        return res,who

    def breakpoint(self,x=''):
        """add breakpoint hook associated with the provided expression.

           Argument:
           x (int/cst/exp): If x is an int or cst, the break condition
               is assumed to be bool(state(pc==x)).
               Otherwise, the condition is simply bool(state(x)).

           Note: all expressions are evaluated in the state. Thus it
                 excludes expressions related to instruction bytes,
                 mnemonic or operands. See ibreakpoint method.
        """
        if x == '':
            for index,f in enumerate(self.hooks):
                if f.__doc__.startswith('break'):
                    x += "[% 2d] %s\n"%(index,f.__doc__)
            return x
        if isinstance(x,int):
            x = self.task.cpu.cst(x,self.pc.size)
        if x._is_cst:
            x = self.pc==x
        f = lambda e,prev,expr=x: bool(e.task.state(expr))
        f.__doc__ = 'breakpoint: %s'%x
        self.hooks.append(f)
        return x

    def watchpoint(self,x=''):
        """add watchpoint hook associated with provided expression.

           Argument:
           x (int/cst/exp): If x is an int or cst, break occurs
               when state(mem(x,8)) changes (symbolic) value.
               Otherwise, break occurs when state(x) changes value.
               Initial value is taken from the watchpoint creation state.
        """
        if x == '':
            for index,f in enumerate(self.hooks):
                if f.__doc__.startswith('watch'):
                    x += "[% 2d] %s\n"%(index,f.__doc__)
            return x
        if isinstance(x,int):
            x = self.task.cpu.cst(x,self.pc.size)
        if x._is_cst:
            x = self.task.cpu.mem(x,8)
        self.watch[x] = self.task.state(x)
        f = lambda e,prev,expr=x: bool(e.task.state(expr)!=e.watch[expr])
        f.__doc__ = 'watchpoint: %s'%x
        self.hooks.append(f)
        return x

    def ibreakpoint(self,mnemonic='',dst=None,src=None):
        """add breakpoint hook related to specific instruction form.
           Currently supports breaking on mnemonic and/or destination
           operand or any source operand.

           Arguments:
           mnemonic (str): breaks after next instruction matching mnemonic.
           dst (int/cst/exp): break on matching destination operand.
           src (int/cst/exp): break on matching any source operand.

           Note: 
           like for breakpoint/watchpoint, if dst/src is an int or
           a cst expression, the input value is assumed to represent the
           address of dst/src (ie. ptr(dst) or ptr(src).)
        """
        def cast(x):
            if x is not None:
                if isinstance(x,int):
                    x = self.task.cpu.cst(x,self.pc.size)
                if x._is_cst:
                    x = self.task.cpu.ptr(x)
            return x
        dst = cast(dst)
        src = cast(src)
        def check(e,prev,mnemo=mnemonic,xdest=dst,xsrc=src):
            if mnemo:
                cond = (prev.mnemonic.lower()==mnemo)
                if not cond:
                    return False
            if xdest is not None or xsrc is not None:
                m = e.task.state.__class__()
                m = prev(m)
                if xdest is not None:
                    cond = any((bool(e.task.state(x==xdest)) for x,_ in m))
                    if not cond:
                        return False
                if xsrc is not None:
                    cond = any((bool(e.task.state(x==xsrc)) for _,x in m))
                    if not cond:
                        return False
            return False
        doc = 'breakpoint: '
        if mnemonic: doc += "%s "%mnemonic
        if dst: doc += "dst: %s "%str(dst)
        if src: doc += "src: %s"%str(dst)
        check.__doc__ = doc
        self.hooks.append(check)

    def stop(self,*args,**kargs):
        return False
