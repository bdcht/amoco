# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *

def __npc(i_xxx):
    def npc(ins,fmap):
        fmap[pc] = fmap(pc)+ins.length
        i_xxx(ins,fmap)
    return npc

# i_xxx is the translation of eBPF instruction xxx.
#------------------------------------------------------------------------------

