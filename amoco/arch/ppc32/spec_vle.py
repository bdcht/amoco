# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2022 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from . import env

from amoco.arch.core import *

ISPECS = []

@ispec("16<[ 000001 00 rY(4) rX(4) ]", mnemonic="se_add")
def ppc_addx(obj,rX,rY):
    obj.operands = [env.GPR[rX],env.GPR[rY]]
    obj.type = type_data_processing
