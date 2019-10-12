#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

import pyparsing as pp

from amoco.logger import Log
logger = Log(__name__)
logger.debug('loading module')
#logger.level = 10

from amoco.arch.msp430.cpu import instruction_msp430 as instruction
from amoco.arch.msp430 import env

#------------------------------------------------------------------------------
# parser for MSP430 assembler syntax.
class msp430_syntax:

    divide = False
    noprefix = False

    comment = pp.Regex(r'\#.*')
    symbol  = pp.Regex(r'[A-Za-z_.$][A-Za-z0-9_.$]*').setParseAction(lambda r: env.ext(r[0],size=32))
    mnemo   = pp.LineStart() + symbol + pp.Optional(pp.Literal(',a'))
    mnemo.setParseAction(lambda r: r[0].ref.lower()+''.join(r[1:]))
    integer = pp.Regex(r'[1-9][0-9]*').setParseAction(lambda r: int(r[0],10))
    hexa    = pp.Regex(r'0[xX][0-9a-fA-F]+').setParseAction(lambda r: int(r[0],16))
    octa    = pp.Regex(r'0[0-7]*').setParseAction(lambda r: int(r[0],8))
    bina    = pp.Regex(r'0[bB][01]+').setParseAction(lambda r: int(r[0],2))
    char    = pp.Regex(r"('.)|('\\\\)").setParseAction(lambda r: ord(r[0]))
    number  = integer|hexa|octa|bina|char
    number.setParseAction(lambda r: env.cst(r[0],32))

    term    = symbol|number

    exp     = pp.Forward()

    op_one  = pp.oneOf("- ~")
    op_sig  = pp.oneOf("+ -")
    op_mul  = pp.oneOf("* /")
    op_cmp  = pp.oneOf("== != <= >= < > <>")
    op_bit  = pp.oneOf("^ && || & |")

    operators = [(op_one,1,pp.opAssoc.RIGHT),
                 (op_sig,2,pp.opAssoc.LEFT),
                 (op_mul,2,pp.opAssoc.LEFT),
                 (op_cmp,2,pp.opAssoc.LEFT),
                 (op_bit,2,pp.opAssoc.LEFT),
                ]
    reg = pp.Suppress('%')+pp.NotAny(pp.oneOf('hi lo'))+symbol
    hilo = pp.oneOf('%hi %lo')+pp.Suppress('(')+exp+pp.Suppress(')')
    exp << pp.operatorPrecedence(term|reg|hilo,operators)

    adr = pp.Suppress('[')+exp+pp.Suppress(']')
    mem = adr #+pp.Optional(symbol|imm)
    mem.setParseAction(lambda r: env.mem(r[0]))

    opd = exp|mem|reg
    opds = pp.Group(pp.delimitedList(opd))

    instr = mnemo + pp.Optional(opds) + pp.Optional(comment)

    def action_reg(toks):
        rname = toks[0]
        return env.reg(rname.ref)

    def action_hilo(toks):
        v = toks[1]
        return env.hi(v) if toks[0]=='%hi' else env.lo(v).zeroextend(32)

    def action_exp(toks):
        tok = toks[0]
        if isinstance(tok,env.exp): return tok
        if len(tok)==2:
            op=tok[0]
            r=tok[1]
            if isinstance(r,list): r=action_exp(r)
            return env.oper(op,r)
        elif len(tok)==3:
            op=tok[1]
            l=tok[0]
            r=tok[2]
            if isinstance(l,list): l=action_exp(l)
            if isinstance(r,list): r=action_exp(r)
            return env.oper(op,l,r)
        else:
            return tok

    def action_instr(toks):
        i = instruction(b'')
        i.mnemonic = toks[0]
        if len(toks)>1: i.operands = toks[1][0:]
        return asmhelper(i)

    # actions:
    reg.setParseAction(action_reg)
    hilo.setParseAction(action_hilo)
    exp.setParseAction(action_exp)
    instr.setParseAction(action_instr)

def asmhelper(i):
    if i.mnemonic=='mov':
        i.mnemonic = 'or'
        i.operands.insert(0,env.g0)
    return i

# ----------------------------
# for testing:

def test_parser(cls):
    while 1:
        try:
            res = raw_input('%s>'%cls.__name__)
            E = cls.instr.parseString(res,True)
            print(E)
        except pp.ParseException:
            logger.error("ParseException")
            return E
        except EOFError:
            return


if __name__=='__main__':
    test_parser(msp430_syntax)
