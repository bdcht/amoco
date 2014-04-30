#!/usr/bin/env python

# This code is part of Amoco
# Copyright (C) 2013 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

import pyparsing as pp

from amoco.logger import Log
logger = Log(__name__)
#logger.level = 10

#------------------------------------------------------------------------------
# parser for x86 AT&T assembler syntax.
class att_syntax:

    divide = False
    noprefix = False

    pfx     = pp.oneOf([ 'data16', 'addr16', 'data32', 'addr32', 'lock', 'wait',
                     'rep', 'repe', 'repne'])
    comment = pp.Regex(r'\#.*')
    symbol  = pp.Regex(r'[A-Za-z_.$][A-Za-z0-9_.$]*')
    integer = pp.Regex(r'[1-9][0-9]*')
    hexa    = pp.Regex(r'0[xX][0-9a-fA-F]+')
    octa    = pp.Regex(r'0[0-7]+')
    bina    = pp.Regex(r'0[bB][01]+')
    char    = pp.Regex(r"('.)|('\\\\)")
    number  = integer|hexa|octa|bina|char

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
    exp << pp.operatorPrecedence(term,operators)

    reg = '%'+symbol

    bis = '('+pp.Optional(reg)+pp.Optional(','+reg+pp.Optional(','+exp))+')'
    adr = pp.Optional(exp)+bis
    mem = pp.Optional(reg+':')+adr

    imm = pp.Optional(pp.Literal('$'))+exp

    opd = mem|reg|imm
    opds = pp.Group(pp.delimitedList(opd))

    instr = pp.Optional(pfx) + symbol + pp.Optional(opds) + pp.Optional(comment)

#------------------------------------------------------------------------------
# parser for x86 INTEL assembler syntax.
class intel_syntax:

    divide = False
    noprefix = False

    pfx     = pp.oneOf([ 'data16', 'addr16', 'data32', 'addr32', 'lock', 'wait',
                     'rep', 'repe', 'repne'])
    spfx    = pp.oneOf([ 'dword', 'word', 'byte'], caseless=True)
    mpfx    = spfx+pp.oneOf([ 'ptr' ], caseless=True)
    sfx     = pp.oneOf([ 'far' ], caseless=True)
    comment = pp.Regex(r'\#.*')
    symbol  = pp.Regex(r'[A-Za-z_.$][A-Za-z0-9_.$]*')
    integer = pp.Regex(r'[1-9][0-9]*')
    hexa    = pp.Regex(r'0[xX][0-9a-fA-F]+')
    octa    = pp.Regex(r'0[0-7]+')
    bina    = pp.Regex(r'0[bB][01]+')
    char    = pp.Regex(r"('.)|('\\\\)")
    number  = integer|hexa|octa|bina|char

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
    exp << pp.operatorPrecedence(term,operators)

    adr = '['+exp+']'
    mem = pp.Optional(mpfx)+pp.Optional(symbol+':')+adr

    opd = mem|exp
    opds = pp.Group(pp.delimitedList(opd))

    instr = pp.Optional(pfx) + symbol + pp.Optional(sfx) + pp.Optional(opds) + pp.Optional(comment)

def test_parser(cls):
    while 1:
        try:
            res = raw_input('%s>'%cls.__name__)
            E = cls.instr.parseString(res,True)
            print E
        except EOFError:
            return


if __name__=='__main__':
    test_parser()
