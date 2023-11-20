# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2022 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *

from amoco.cas.utils import *

# ------------------------------------------------------------------------------
# helpers and decorators :
def _push_(fmap, _x):
    fmap[sp] = fmap[sp] - _x.length
    fmap[mem(sp, _x.size)] = _x


def _pop_(fmap, _l):
    fmap[_l] = fmap(mem(sp, _l.size))
    fmap[sp] = fmap[sp] + _l.length


def __npc(i_xxx):
    def npc(ins, fmap):
        fmap[pc] = fmap(pc) + ins.length
        i_xxx(ins, fmap)

    return npc


def trap(ins, fmap, trapname):
    fmap.internals["trap"] = trapname


