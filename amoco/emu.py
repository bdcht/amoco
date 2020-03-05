# -*- coding: utf-8 -*-

"""
.. _emu:

emu.py
======
The emu module of amoco.

"""

# This code is part of Amoco
# Copyright (C) 2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.config import conf
from amoco.arch.core import DecodeError
from amoco.logger import Log
logger = Log(__name__)
logger.debug('loading emu')

class emul(object):
    def __init__(self,task):
        self.task = task
        self.cpu = task.cpu
        self.pc = task.cpu.PC()
        self.psz = self.pc.size
        self.hooks = []
        self.handlers = {}
        if task.OS is not None:
            self.abi = task.OS.abi
        else:
            self.abi = None

    def stepi(self):
        addr = self.task.getx(self.pc)
        i = self.task.read_instruction(addr)
        if i is not None:
            self.task.state.safe_update(i)
        else:
            raise DecodeError(addr)
        return i

    def iterate(self):
        lasti = None
        while True:
            if not self.checkstate(lasti):
                break
            try:
                lasti = self.stepi()
                yield lasti
            except MemoryError as e:
                lasti = None
                if not self.exception_handler(e):
                    break

    def exception_handler(self,e):
        te = type(e)
        logger.debug('exception %s received'%te)
        if te in self.handlers:
            return self.handlers[te](self,e)
        raise(e)

    def checkstate(self,prev=None):
        res = True
        for f in self.hooks:
            res &= f(self,prev)
            if not res: break
        return res



