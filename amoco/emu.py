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

try:
    IntType = (int,long)
except NameError:
    IntType = (int,)
else:
    conf.Cas.unicode=False

class emul(object):
    def __init__(self,task):
        self.task = task
        self.cpu = task.cpu
        self.pc = task.cpu.PC()
        self.psz = self.pc.size
        if task.OS is not None:
            self.abi = task.OS.abi
        else:
            self.abi = None

    def stepi(self):
        addr = self.task.state(self.pc)
        i = self.task.read_instruction(addr)
        if i is not None:
            self.task.state.update(i)
        else:
            raise DecodeError(addr)
        return i

    def iterate(self):
        while True:
            yield self.stepi()

