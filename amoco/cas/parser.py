# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

from .expressions import bot, top, reg, ext

# expression parser:
# -------------------

import pyparsing as pp

# terminals:
p_bottop = pp.oneOf("⊥ T")
p_symbol = pp.Word(pp.alphas)
p_extern = pp.Suppress("@") + p_symbol
p_cst = pp.Suppress("0x") + pp.Combine(pp.Optional("-") + pp.Regex("[0-9a-f]+"))
p_int = pp.Word(pp.nums).setParseAction(lambda r: int(r[0]))
p_slc = "[" + p_int.setResultsName("start") + ":" + p_int.setResultsName("stop") + "]"
p_op1 = pp.oneOf("~ -")
p_op2 = pp.oneOf("+ - / // * & | ^ << >> < > == <= >= != ? :")
p_term = p_bottop | p_symbol | p_extern | p_cst

# nested expressions:
p_expr = pp.Forward()

p_csl = pp.Suppress("|") + p_slc + pp.Suppress("->")
p_comp = pp.Group(pp.Suppress("{") + pp.ZeroOrMore(p_expr) + pp.Suppress("| }"))
p_mem = "M" + p_int + pp.Optional(p_symbol)

operators = [
    (p_op1, 1, pp.opAssoc.RIGHT),
    (p_mem, 1, pp.opAssoc.RIGHT),
    (p_slc, 1, pp.opAssoc.LEFT),
    (p_op2, 2, pp.opAssoc.LEFT),
    (p_csl, 1, pp.opAssoc.RIGHT),
]

p_expr << pp.operatorPrecedence(p_term | p_comp, operators)

p_bottop.setParseAction(lambda r: bot if r[0] == "_" else top)
p_symbol.setParseAction(lambda r: reg(r[0]))
p_extern.setParseAction(lambda r: ext(r[0]))
p_cst.setParseAction(lambda r: int(r[0], 16))
p_slc.setParseAction(lambda r: slice(r["start"], r["stop"]))


def parse(s):
    return p_expr.parseString(s, True)


def test_parser():
    while 1:
        try:
            res = raw_input("amoco[test_parser]>")
            E = p_expr.parseString(res, True)
            print(E)
        except EOFError:
            return
