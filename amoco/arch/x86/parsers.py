#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2013 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

import pyparsing as pp

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")
# logger.level = 10

# ------------------------------------------------------------------------------
# parser for x86 or x64 AT&T assembler syntax.

# Because of the recent patches of amoco, and to avoid code duplication
# between x86 and x64, att_syntax is now created by att_syntax_gen.

# The function 'action_instr' contains many ad hoc hooks, which could be
# made useless if this information is made available by the spec_*.py
# files; but currently it is not the case :-(
# Note also that 'action_instr' is not sufficient to generate a valid
# amoco instruction; in particular, i.spec and i.type are missing
# i.spec can be extracted from one of the spec_*.ISPECS, but while it
# is easy to filter the specs to retain only the ones corresponding to
# the value of i.mnemonic, it is difficult to find which one is the
# right one: it depends on the arguments types and sizes.
# I will try to provide a way to determine the right i.spec, and also
# it should allow to assemble an instruction... stay tuned!

from amoco.arch.x86.formats import (
    mnemo_string_rep,
    mnemo_sse_cmp_predicate,
    att_mnemo_suffix_one_ptr,
    att_mnemo_suffix_one_iflt,
    att_mnemo_float_optional_suffix,
    att_mnemo_correspondance,
)
from amoco.cas import expressions


def att_syntax_gen(env, CONDITION_CODES, cpu_addrsize, instruction):
    pfx = pp.oneOf(
        [
            "data16",
            "addr16",
            "data32",
            "addr32",
            "lock",
            "rep",
            "repz",
            "repe",
            "repne",
            "repnz",
        ]
    )

    # Putting everything in one regex is faster than having pyparsing
    # work with an alternative, e.g.  number = integer|hexa|octa|bina
    # We cannot generate an expressions.cst here, because we don't know
    # what will be the integer size; e.g. it will be 32 for %esp+10 but
    # it will be 64 for %rsp+10, and it will depend on the instruction
    # for $0
    number = pp.Regex(r"(0[xX][0-9a-fA-F]+|0[bB][01]+|[0-9]+)")
    number.setParseAction(lambda toks: expressions.cst(int(toks[0], 0), 64))

    symbol = pp.Regex(
        "([a-zA-Z_][a-zA-Z0-9_.$]*|\.L[a-zA-Z0-9_.]+)(@[a-zA-Z]+)?|[1-9][0-9]*[bf]|\[\.-\.L[A-Z]*[0-9]*\]"
    )
    char = pp.Regex(r"('.)|('\\\\)")

    term = symbol | number | char

    def action_term(toks):
        if isinstance(toks[0], str):
            return expressions.lab(toks[0], size=cpu_addrsize)

    term.setParseAction(action_term)

    exp = pp.Forward()

    op_one = pp.oneOf("- ~")
    op_sig = pp.oneOf("+ -")
    op_mul = pp.oneOf("* /")
    op_cmp = pp.oneOf("== != <= >= < > <>")
    op_bit = pp.oneOf("^ && || & |")

    operators = [
        (op_one, 1, pp.opAssoc.RIGHT),
        (op_sig, 2, pp.opAssoc.LEFT),
        (op_mul, 2, pp.opAssoc.LEFT),
        (op_cmp, 2, pp.opAssoc.LEFT),
        (op_bit, 2, pp.opAssoc.LEFT),
    ]
    exp << pp.operatorPrecedence(term, operators)

    def action_exp(toks):
        if len(toks) != 1:
            NEVER
        toks = toks[0]
        if not isinstance(toks, pp.ParseResults):
            return
        for idx in range(len(toks)):
            if isinstance(toks[idx], pp.ParseResults):
                toks[idx] = action_exp([toks[idx]])
        if len(toks) == 2 and toks[0] == "-" and toks[1]._is_cst:
            return expressions.cst(-toks[1].value, size=toks[1].size)
        # We need to uniformize the sizes, else amoco will complain
        # The real size value is set later, it depends on other arguments
        if toks[2]._is_cst:
            toks[2].size = toks[0].size
            toks[2].v &= toks[2].mask
        elif toks[2]._is_lab:
            toks[0].size = toks[2].size
            if toks[0]._is_cst:
                toks[0].v &= toks[0].mask
        if len(toks) >= 5:
            toks[4].size = toks[0].size
        if len(toks) == 7:
            toks[6].size = toks[0].size
        # We could prefer to use a generic analysis of toks, but
        # dealing with specific cases one by one gives more control
        # on the output
        if toks[1] == "-":
            toks[2] = -toks[2]
        else:
            assert toks[1] == "+"
        if len(toks) == 3:
            return toks[0] + toks[2]
        if toks[3] == "-":
            toks[4] = -toks[4]
        else:
            assert toks[3] == "+"
        if len(toks) == 5:
            return toks[0] + toks[2] + toks[4]
        if toks[5] == "-":
            toks[6] = -toks[6]
        else:
            assert toks[5] == "+"
        if len(toks) == 7:
            return toks[0] + toks[2] + toks[4] + toks[6]
        else:
            print("EXP %s" % toks)
            FAIL

    exp.setParseAction(action_exp)

    imm = "$" + exp
    imm.setParseAction(lambda toks: toks[1])

    fpreg = "st(" + pp.Regex(r"[0-7]") + ")"
    reg = "%" + fpreg | "%" + symbol

    def action_reg(toks):
        r = toks[1]
        if r == "st":
            return env.st(0)
        if r == "st(":
            return env.st(int(toks[2]))
        if r.startswith("mm"):
            return env.mmregs[int(r[2:])]
        if r.startswith("xmm"):
            return env.xmmregs[int(r[3:])]
        if r.startswith("cr"):
            return env.cr(int(r[2:]))
        if r.startswith("dr"):
            return env.dr(int(r[2:]))
        if r[0] == "r" and r[-1] == "b":
            # gcc or clang use 'r8b' instead of 'R8L' from Intel specs
            r = r[:-1] + "l"
        return env.__dict__[r]

    reg.setParseAction(action_reg)

    bis = "(" + pp.Optional(reg) + pp.Optional("," + reg + pp.Optional("," + exp)) + ")"

    def action_bis(toks):
        if len(toks) == 3:
            addr = toks[1]
        elif len(toks) == 5 and toks[2] == ",":
            addr = expressions.op("+", toks[1], toks[3])
            if env.internals.get("keep_order"):
                addr.prop |= 16
        elif len(toks) == 6 and toks[1] == "," and toks[3] == ",":
            toks[4].size = toks[2].size  # cst size set to register size
            addr = expressions.oper("*", toks[2], toks[4])
        elif len(toks) == 7 and toks[2] == "," and toks[4] == ",":
            toks[5].size = toks[3].size  # cst size set to register size
            addr = expressions.op("+", toks[1], expressions.oper("*", toks[3], toks[5]))
            if env.internals.get("keep_order"):
                addr.prop |= 16
        else:
            NEVER
        return addr

    bis.setParseAction(action_bis)

    adr = exp + bis | bis | exp
    mem = pp.Optional(reg + ":") + adr

    def action_mem(toks):
        # we use str(_) because != is redefined for amoco expressions
        # and fails when comparing with strings
        r = [str(_) for _ in toks]
        if ":" in r:
            assert len(r) == 3
            assert ":" == r[1]
            seg = toks[0]
            toks.pop(0)
            toks.pop(0)
        else:
            seg = ""
        if len(toks) == 2:
            addr = toks[1]
            disp = toks[0]
            if hasattr(disp, "value"):
                disp = disp.value
            else:
                assert disp.size == addr.size
        else:
            addr = toks[0]
            disp = 0
        return expressions.mem(addr, cpu_addrsize, disp=disp, seg=seg)

    mem.setParseAction(action_mem)

    opd = mem | reg | imm
    ind = "*" + opd
    opd_i = opd | ind
    opds = pp.Group(pp.delimitedList(opd_i))

    instr = pp.Optional(pfx) + symbol + pp.Optional(opds)

    mmx_with_suffix1 = [
        p + s
        for p in (
            "PSIGN",
            "PABS",
            "PADD",
            "PSUB",
            "PSADB",
            "PADDS",
            "PSUBS",
            "PSLL",
            "PSRL",
            "PHADD",
            "PHSUB",
            "PHADDS",
            "PHSUBS",
            "PMULHRS",
            "PMINS",
            "PMINU",
            "PMAXS",
            "PMAXU",
            "PAVG",
            "PCMPEQ",
            "PCMPGT",
        )
        for s in ("B", "W", "D", "Q")
    ]
    mmx_with_suffix2 = [
        p + s
        for p in (
            "UNPCKL",
            "UNPCKH",
            "MOV",
            "MOVNT",
            "HADD",
            "SQRT",
            "RSQRT",
            "RCP",
            "AND",
            "ANDN",
            "OR",
            "XOR",
            "ADD",
            "MUL",
            "SUB",
            "MIN",
            "DIV",
            "MAX",
            "COMI",
            "UCOMI",
            "CMP",
            "SHUF",
        )
        for s in ("PS", "PD", "SD", "SS")
    ]

    def action_instr(toks):
        i = instruction(b"")
        i.mnemonic = toks[0].upper()
        # Remove prefixes
        if i.mnemonic in ("REP", "REPZ", "REPNZ", "REPE", "REPNE", "LOCK"):
            if i.mnemonic in ("REP", "REPZ", "REPE"):
                i.misc.update({"pfx": ["rep", None, None, None], "rep": True})
            if i.mnemonic in ("REPNZ", "REPNE"):
                i.misc.update({"pfx": ["repne", None, None, None], "repne": True})
            if i.mnemonic in ("LOCK",):
                i.misc.update({"pfx": ["lock", None, None, None], "lock": True})
            del toks[0]  # toks.pop(0) is broken for pyparsing 2.0.2
            # https://bugs.launchpad.net/ubuntu/+source/pyparsing/+bug/1381564
            i.mnemonic = toks[0].upper()
        # Get operands
        if len(toks) > 1:
            i.operands = list(reversed(toks[1][0:]))
        # Convert mnemonics, set operand sizes
        if i.mnemonic in (
            "CALLL",
            "CALLQ",
            "JMPL",
            "JMPQ",
            "RETL",
            "RETQ",
            "BSWAPL",
            "BSWAPQ",
            "FUCOMPI",
        ):
            # clang on MacOS X
            if i.mnemonic[-1] in ("L", "Q"):
                i.mnemonic = i.mnemonic[:-1]
            else:
                i.mnemonic = "FUCOMIP"
        mnemo = i.mnemonic.lower()
        if i.mnemonic in ("CALL", "JMP"):
            if len(i.operands) == 2 and i.operands[1] == "*":
                i.operands.pop()
                if not i.operands[0]._is_mem and not i.operands[0]._is_reg:
                    i.operands[0] = expressions.mem(i.operands[0], cpu_addrsize)
            else:
                if i.operands[0]._is_mem:
                    i.operands[0] = i.operands[0].a.base + i.operands[0].a.disp
        elif i.mnemonic.startswith(("J", "SET", "CMOV")):
            for pfx in ("J", "SET", "CMOV"):
                if i.mnemonic.startswith(pfx):
                    break
            for i.cond in CONDITION_CODES.values():
                if i.mnemonic[len(pfx) :] in i.cond[0].split("/"):
                    break
            else:
                if pfx == "CMOV" and i.mnemonic[-1] in ("W", "L", "Q"):
                    # clang on MacOS X
                    for i.cond in CONDITION_CODES.values():
                        if i.mnemonic[len(pfx) : -1] in i.cond[0].split("/"):
                            break
                    else:
                        NEVER
                elif pfx == "SET" and i.mnemonic[-1] == "B":
                    # gcc 3.2.3
                    for i.cond in CONDITION_CODES.values():
                        if i.mnemonic[len(pfx) : -1] in i.cond[0].split("/"):
                            break
                    else:
                        NEVER
                else:
                    NEVER
            i.mnemonic = pfx + "cc"
            if pfx == "J":
                i.operands[0] = i.operands[0].a.base + i.operands[0].a.disp
            if pfx == "CMOV":
                if i.operands[0]._is_mem:
                    i.operands[0].size = i.operands[1].size
                if i.operands[1]._is_mem:
                    i.operands[1].size = i.operands[0].size
        elif mnemo in att_mnemo_correspondance:
            i.mnemonic = att_mnemo_correspondance[mnemo].upper()
            if i.mnemonic in ("CBW", "CWD", "IRET"):
                i.misc.update({"opdsz": 16, "pfx": [None, None, "opdsz", None]})
        elif mnemo[-1] == "w" and mnemo[:-1] in mnemo_string_rep:
            i.misc.update({"opdsz": 16, "pfx": [None, None, "opdsz", None]})
        elif i.mnemonic == "CMPSD" and len(i.operands) == 0:
            # String cmpsd, different from the SSE cmp*sd, has no arguments
            pass
        elif i.mnemonic == "MOVSL":
            # String movsd, different from the SSE movsd
            # Has no arguments
            i.mnemonic = "MOVSD"
            assert len(i.operands) == 0
        elif i.mnemonic[:-2] in ("MOVS", "MOVZ"):
            i.misc["opdsz"], sz = {
                "BW": (8, 16),
                "BL": (8, 32),
                "BQ": (8, 64),
                "WL": (16, 32),
                "WQ": (16, 64),
                "LQ": (32, 64),
            }[i.mnemonic[-2:]]
            if i.operands[1]._is_mem:
                i.operands[1].size = i.misc["opdsz"]
            assert i.operands[0].size == sz
            i.mnemonic = i.mnemonic[:-2] + "X"
        elif i.mnemonic == "MOVD":
            pass
        elif i.mnemonic in ("FLDCW", "FSTCW", "FNSTCW",):
            assert i.operands[0]._is_mem
            i.operands[0].size = 16
        elif i.mnemonic == "CMPXCHG":
            if i.operands[0]._is_mem:
                i.operands[0].size = i.operands[1].size
        elif i.mnemonic == "CMPXCHG8B":
            if i.operands[0]._is_mem:
                i.operands[0].size = 64
        elif i.mnemonic == "CMPXCHG16B":
            if i.operands[0]._is_mem:
                i.operands[0].size = 128
        elif i.mnemonic in mmx_with_suffix2 and len(i.operands):
            if i.mnemonic.endswith("SS"):
                if i.operands[1]._is_mem:
                    i.operands[1].size = 32
            elif i.mnemonic.endswith("SD"):
                if i.operands[0]._is_mem:
                    i.operands[0].size = 64
                if i.operands[1]._is_mem:
                    i.operands[1].size = 64
            else:
                if i.operands[1]._is_mem:
                    i.operands[1].size = 128
        elif i.mnemonic in (
            "CVTSI2SS",
            "CVTSI2SD",
            "CVTTSS2SI",
            "CVTTSS2SIL",
            "CVTTSS2SIQ",
        ):
            if i.operands[1]._is_mem:
                i.operands[1].size = 32
            # gcc 4.9.2 generates cvttss2siq %xmm0, %r15
            # which is useless, because the size of the output is
            # determined by the output register
            if i.mnemonic[-1] in "LQ":
                i.mnemonic = i.mnemonic[:-1]
        elif i.mnemonic in (
            "MOVLPD",
            "MOVLPS",
            "MOVHPD",
            "MOVHPS",
            "MOVDDUP",
            "PSHUFW",
            "CVTSD2SS",
            "CVTSD2SI",
            "CVTTSD2SI",
            "CVTTSD2SIL",
            "CVTTSD2SIQ",
            "CVTPI2PD",
            "CVTPI2PS",
            "CVTPS2PI",
            "CVTPS2PD",
            "CVTDQ2PD",
        ):
            if i.operands[0]._is_mem:
                i.operands[0].size = 64
            if i.operands[1]._is_mem:
                i.operands[1].size = 64
            if i.mnemonic[-1] in "LQ":
                i.mnemonic = i.mnemonic[:-1]
        elif i.mnemonic in (
            "PSHUFD",
            "PSHUFLW",
            "PSHUFHW",
            "MOVDQA",
            "MOVDQU",
            "MOVSLDUP",
            "MOVSHDUP",
            "MOVAPD",
            "MOVAPS",
            "MOVUPD",
            "MOVUPS",
            "CVTPD2PS",
            "CVTPD2PI",
            "CVTPD2DQ",
            "CVTTPD2DQ",
            "CVTTPD2PI",
            "CVTPS2DQ",
            "CVTTPS2PI",
            "CVTTPS2DQ",
            "CVTDQ2PS",
            "PUNPCKHQDQ",
        ):
            if i.operands[0]._is_mem:
                i.operands[0].size = 128
            if i.operands[1]._is_mem:
                i.operands[1].size = 128
        elif i.mnemonic in mmx_with_suffix1 or i.mnemonic in (
            "PSHUFB",
            "PAND",
            "PANDN",
            "POR",
            "PXOR",
        ):
            if i.operands[1]._is_mem:
                i.operands[1].size = i.operands[0].size
        elif i.mnemonic == "MOVABSQ":
            # gcc generates 'movabsq $cst, %reg' instead of 'movq $cst, %reg'
            i.mnemonic = "MOV"
            for _ in i.operands:
                if _._is_mem:
                    _.size = 64
                if _._is_cst:
                    _.size = 64
                    _.v &= _.mask
                if _._is_lab:
                    _.size = 64
        else:
            for _ in att_mnemo_suffix_one_ptr:
                if mnemo[:-1] != _:
                    continue
                # Detect MMX MOVQ instruction, not 64-bit register MOV for x64
                if (
                    i.mnemonic == "MOVQ"
                    and i.operands[1]._is_reg
                    and "mm" in i.operands[1].ref
                ):
                    if i.operands[0]._is_mem:
                        i.operands[0].size = 64
                    break
                if (
                    i.mnemonic == "MOVQ"
                    and i.operands[0]._is_reg
                    and "mm" in i.operands[0].ref
                ):
                    if i.operands[1]._is_mem:
                        i.operands[1].size = 64
                    break
                i.mnemonic = _.upper()
                sz = {"b": 8, "w": 16, "l": 32, "q": 64}[mnemo[-1]]
                if "q" == mnemo[-1]:
                    i.misc.update({"REX": (1, 0, 0, 0)})
                if "w" == mnemo[-1]:
                    i.misc.update({"opdsz": 16, "pfx": [None, None, "opdsz", None]})

                def set_size(e, sz):
                    if e._is_mem:
                        e.size = sz
                    if e._is_cst:
                        e.size = sz
                        e.v &= e.mask
                    if e._is_lab:
                        e.size = sz
                    if e._is_eqn:
                        e.size = sz
                        if e.l is not None:
                            set_size(e.l, sz)
                        set_size(e.r, sz)

                for _ in i.operands:
                    set_size(_, sz)
            for _ in att_mnemo_suffix_one_iflt:
                if mnemo[:-1] != _:
                    continue
                i.mnemonic = _.upper()
                sz = {"s": 16, "l": 32, "q": 64}[mnemo[-1]]
                for _ in i.operands:
                    if _._is_mem:
                        _.size = sz
            if mnemo[-2:] == "ll" and mnemo[:-2] in att_mnemo_suffix_one_iflt:
                # clang on MacOS X
                i.mnemonic = mnemo[:-2].upper()
                for _ in i.operands:
                    if _._is_mem:
                        _.size = 64
            for _ in att_mnemo_float_optional_suffix:
                if mnemo[:-1] != _:
                    continue
                if mnemo[-1] in ("i", "p", "r", "z", "1"):
                    continue
                i.mnemonic = _.upper()
                sz = {"s": 32, "l": 64, "t": 80}[mnemo[-1]]
                for _ in i.operands:
                    if _._is_mem:
                        _.size = sz
        # Implicit operands
        if i.mnemonic in ("AAD", "AAM"):
            if len(i.operands) == 0:
                i.operands.append(expressions.cst(10, 8))
            else:
                i.operands[0].size = 8
        elif (
            i.mnemonic in ("SAL", "SAR", "SHL", "SHR", "ROR", "ROL")
            and len(i.operands) == 1
        ):
            i.operands.append(expressions.cst(1, 32))
        elif i.mnemonic in ("SHLD", "SHRD") and len(i.operands) == 2:
            i.operands.append(env.__dict__["cl"])
        elif (
            i.mnemonic.startswith("CMP")
            and i.mnemonic.endswith(("PS", "PD", "SD", "SS"))
            and len(i.operands)
        ):
            idx = mnemo_sse_cmp_predicate.index(i.mnemonic[3:-2].lower())
            i.operands.append(expressions.cst(idx))
            i.mnemonic = i.mnemonic[:3] + i.mnemonic[-2:]
        elif (
            i.mnemonic
            in (
                "FADD",
                "FSUB",
                "FSUBR",
                "FMUL",
                "FDIV",
                "FDIVR",
                "FCOMI",
                "FCOMIP",
                "FUCOMI",
                "FUCOMIP",
            )
            and len(i.operands) == 1
            and not i.operands[0]._is_mem
        ):
            i.operands.insert(0, env.st(0))
        elif (
            i.mnemonic in ("FADDP", "FSUBP", "FSUBRP", "FMULP", "FDIVP", "FDIVRP",)
            and len(i.operands) == 1
            and not i.operands[0]._is_mem
        ):
            i.operands.append(env.st(0))
        elif (
            i.mnemonic in ("FCOM", "FCOMP", "FUCOM", "FUCOMP",) and len(i.operands) == 0
        ):
            i.operands.append(env.st(1))
        return i

    instr.setParseAction(action_instr)
    # Set instr.instr for compatibility with previous versions of amoco
    # where att_syntax is a namespace containing 'instr'.
    # Set instr.__name__ for test_parser
    instr.instr = instr
    instr.__name__ = "att_syntax"
    return instr


from amoco.arch.x86.cpu_x86 import instruction_x86
from amoco.arch.x86.utils import CONDITION_CODES
from amoco.arch.x86 import env

att_syntax = att_syntax_gen(env, CONDITION_CODES, 32, instruction_x86)


# ------------------------------------------------------------------------------
# parser for x86 INTEL assembler syntax.
# (not working)
class intel_syntax:

    divide = False
    noprefix = False

    pfx = pp.oneOf(
        ["data16", "addr16", "data32", "addr32", "lock", "rep", "repe", "repne"]
    )
    spfx = pp.oneOf(["dword", "word", "byte"], caseless=True)
    mpfx = spfx + pp.oneOf(["ptr"], caseless=True)
    sfx = pp.oneOf(["far"], caseless=True)
    comment = pp.Regex(r"\#.*")
    symbol = pp.Regex(r"[A-Za-z_.$][A-Za-z0-9_.$]*")
    integer = pp.Regex(r"[1-9][0-9]*")
    hexa = pp.Regex(r"0[xX][0-9a-fA-F]+")
    octa = pp.Regex(r"0[0-7]+")
    bina = pp.Regex(r"0[bB][01]+")
    char = pp.Regex(r"('.)|('\\\\)")
    number = integer | hexa | octa | bina | char

    term = symbol | number

    exp = pp.Forward()

    op_one = pp.oneOf("- ~")
    op_sig = pp.oneOf("+ -")
    op_mul = pp.oneOf("* /")
    op_cmp = pp.oneOf("== != <= >= < > <>")
    op_bit = pp.oneOf("^ && || & |")

    operators = [
        (op_one, 1, pp.opAssoc.RIGHT),
        (op_sig, 2, pp.opAssoc.LEFT),
        (op_mul, 2, pp.opAssoc.LEFT),
        (op_cmp, 2, pp.opAssoc.LEFT),
        (op_bit, 2, pp.opAssoc.LEFT),
    ]
    exp << pp.operatorPrecedence(term, operators)

    adr = "[" + exp + "]"
    mem = pp.Optional(mpfx) + pp.Optional(symbol + ":") + adr

    opd = mem | exp
    opds = pp.Group(pp.delimitedList(opd))

    instr = (
        pp.Optional(pfx)
        + symbol
        + pp.Optional(sfx)
        + pp.Optional(opds)
        + pp.Optional(comment)
    )


def test_parser(cls):
    while 1:
        try:
            res = raw_input("%s> " % cls.__name__)
            E = cls.instr.parseString(res, True)
            print(E)
        except EOFError:
            return


if __name__ == "__main__":
    test_parser(att_syntax)
