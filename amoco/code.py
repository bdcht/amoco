# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
code.py
=======

This module defines classes that represent assembly instructions blocks,
functions, and calls to *external* functions. In amoco, such objects are
found as :attr:`node.data` in nodes of a :class:`cfg.graph`. As such,they
all provide a common API with:

    * ``address`` to identify and locate the object in memory
    * ``support`` to get the address range of the object
    * ``view`` to display the object

"""

from heapq import heappush

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

from amoco.ui.views import blockView, funcView

# -------------------------------------------------------------------------------
class acode(object):
    _is_block = False
    _is_func = False

    def cut(self, address):
        raise ValueError(address)


class block(acode):
    """A block instance holds a sequence of instructions.

    Args:
        instr (list[instruction]): the sequence of continuous (ordered) instructions

    Attributes:
        instr (list): the list of instructions of the block.
        view (:class:`blockView`): holds the :mod:`ui.views` object used to display the block.
        length (int): the byte length of the block instructions sequence.
        support (tuple): the memory footprint of the block
    """

    _is_block = True
    __slots__ = ["instr", "view"]

    def __init__(self, instrlist):
        self.instr = instrlist
        self.view = blockView(self)

    @property
    def address(self):
        """address (:class:`cst`): the address of the first instruction in the block.
        """
        try:
            return self.instr[0].address
        except IndexError:
            return None

    @property
    def length(self):
        return sum([i.length for i in self.instr], 0)

    def __len__(self):
        return self.length

    # @property
    # def cfi(self):
    #    ii = self.instr
    #    TODO

    @property
    def support(self):
        if len(self.instr) > 0:
            return (self.address, self.address + self.length)
        else:
            return (None, None)

    def __getitem__(self, i):
        """block objects support slicing from given start/stop addresses

           Args:
               i (slice): start and stop address *within* the block. The
                          values must match addresses of instructions otherwise
                          a :exc:`ValueError` exception is raised.

           Returns:
               block: a new block with selected instructions.
        """
        sta, sto, stp = i.indices(self.length)
        assert stp == 1
        pos = [0]
        for i in self.instr:
            pos.append(pos[-1] + i.length)
        try:
            ista = pos.index(sta)
            isto = pos.index(sto)
        except ValueError:
            logger.warning(
                "can't slice block: indices must match instruction boudaries"
            )
            return None
        I = self.instr[ista:isto]
        if len(I) > 0:
            return block(self.instr[ista:isto])

    def cut(self, address):
        """cutting the block at given address will remove instructions after this address,
        (which needs to be aligned with instructions boundaries.) The effect is thus to
        reduce the block size.

        Args:
            address (cst): the address where the cut occurs.

        Returns:
            int: the number of instructions removed from the block.
        """
        I = [i.address for i in self.instr]
        try:
            pos = I.index(address)
        except ValueError:
            logger.warning(
                "invalid attempt to cut block @%s at %s" % (self.address, address)
            )
            return 0
        else:
            self.instr = self.instr[:pos]
            nl = len(I) - pos
            return nl

    def __str__(self):
        T = self.view._vltable(formatter="Null")
        return "\n".join([r.show(raw=True, **T.rowparams) for r in T.rows])

    def __repr__(self):
        sta, sto = self.support
        nbi = len(self.instr)
        return "<{} object ({}-{}) with {} instructions>".format(
            self.__class__.__name__, sta, sto, nbi
        )

    def raw(self):
        """returns the *raw* bytestring of the block instructions.
       """
        return b"".join([i.bytes for i in self.instr])

    def __cmp__(self, b):
        return cmp(self.raw(), b.raw())

    def __eq__(self, b):
        return self.raw() == b.raw()

    def __hash__(self):
        return hash(self.address.value)

    def __getstate__(self):
        return self.instr

    def __setstate__(self, state):
        self.instr = state
        self.view = blockView(self)


# ------------------------------------------------------------------------------
class func(acode):
    """A graph of blocks that represents a function's Control-Flow-Graph (CFG).

    Args:
        g (graph_core): the connected graph component of nodes.

    Attributes:
        cfg (graph_core): the :class:`graph_core` CFG of the function
                          (see :mod:`cfg`.)
        blocks (list[block]): the list of blocks in the CFG
        support (tuple): the memory footprint of the function
    """

    _is_func = True
    __slots__ = ["cfg", "view"]

    # the init of a func takes a core_graph and creates a map of it:
    def __init__(self, g=None):
        self.cfg = g
        if self.cfg:
            roots = self.cfg.roots()
            if len(roots) > 1:
                raise ValueError("multiple roots node in CFG")
            self.view = funcView(self)

    @property
    def address(self):
        root = self.cfg.roots()[0]
        return root.data.address

    @property
    def blocks(self):
        """blocks (list): the list of blocks within the function.
        """
        return sorted(
            filter(lambda x: x._is_block, [n.data for n in self.cfg.sV]),
            key=lambda x: x.address,
        )

    @property
    def support(self):
        smin = self.address
        smax = max((b.address + b.length for b in self.blocks))
        return (smin, smax)

    def __str__(self):
        return "%s{%d}" % (self.address, len(self.blocks))

    def __getstate__(self):
        return self.cfg

    def __setstate__(self, state):
        self.cfg = state
        self.view = funcView(self)


# ------------------------------------------------------------------------------


class tag:
    """defines keys as class attributes, used in :attr:`misc` attributes to
    indicate various relevant properties of blocks within functions.
    """

    FUNC_START = "func_start"
    FUNC_END = "func_end"
    FUNC_STACK = "func_stack"
    FUNC_UNSTACK = "func_unstack"
    FUNC_CALL = "func_call"
    FUNC_GOTO = "func_goto"
    FUNC_ARG = "func_arg"
    FUNC_VAR = "func_var"
    FUNC_IN = "func_in"
    FUNC_OUT = "func_out"
    LOOP_START = "loop_start"
    LOOP_END = "loop_end"
    LOOP_COND = "loop_cond"

    @classmethod
    def list(cls):
        """get the list of all defined keys
        """
        return filter(lambda kv: kv[0].startswith("FUNC_"), cls.__dict__.items())

    @classmethod
    def sig(cls, name):
        """symbols for tag keys used to compute the block's signature
        """
        return {
            "cond": "?",
            "func": "F",
            cls.FUNC_START: "e",
            cls.FUNC_END: "r",
            cls.FUNC_STACK: "+",
            cls.FUNC_UNSTACK: "-",
            cls.FUNC_CALL: "c",
            cls.FUNC_GOTO: "j",
            cls.FUNC_ARG: "a",
            cls.FUNC_VAR: "v",
            cls.FUNC_IN: "i",
            cls.FUNC_OUT: "o",
            cls.LOOP_START: "l",
        }.get(name, "")


def _code_misc_default():
    return 0
