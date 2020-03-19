# -*- coding: utf-8 -*-

from .env import *
from amoco.arch.core import Formatter


def mnemo(i):
    return i.mnemonic.lower().ljust(8, " ")


def op0(i):
    return str(i.operands[0])


def rel0(i):
    return "*%s" % i.misc["to"]


def op1(i):
    return ", " + str(i.operands[1])


def dest1(i):
    return ", %s" % str(i.dst)


def bitb(i):
    return ", %d" % i.operands[1]


def accessbank(i):
    return ", BANKED" if i.a == 1 else ", ACCESS"


def adr(i):
    x = str(i.operands[0])
    return x + ", fast" if i.misc["fast"] == True else x


def tblrw(i):
    m = i.mnemonic.lower()
    if i.misc["postinc"]:
        return m + "*+"
    elif i.misc["postdec"]:
        return m + "*-"
    elif i.misc["preinc"]:
        return m + "+*"
    return m


format_byte = [mnemo, op0, dest1, accessbank]
format_bit = [mnemo, op0, bitb, accessbank]
format_imm = [mnemo, op0]
format_rel = [mnemo, rel0]
format_call = [mnemo, adr]

PIC_full_formats = {
    "byte_oriented": format_byte,
    "bit_oriented": format_bit,
    "control": format_imm,
    "control_rel": format_rel,
    "noop": [mnemo],
    "tblrw": [tblrw],
    "literal": format_imm,
    "LFSR": [mnemo, op0, op1],
    "decode_movff": [mnemo, op0, op1],
    "CALL": format_call,
    "MOVWF": [mnemo, op0, accessbank],
    "CLRF": [mnemo, op0, accessbank],
    "MULWF": [mnemo, op0, accessbank],
}

PIC_full = Formatter(PIC_full_formats)
