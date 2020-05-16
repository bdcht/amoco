# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
render.py
=========

This module ...
"""

from io import BytesIO as StringIO

from amoco.config import conf

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

import re

try:
    from pygments.token import Token
    from pygments.style import Style
    from pygments.lexer import RegexLexer
    from pygments.formatters import *
except ImportError:
    logger.verbose("pygments package not found, no renderer defined")
    has_pygments = False

    # metaclass definition, with a syntax compatible with python2 and python3
    class TokenType(type):
        def __getattr__(cls, key):
            return key

    Token_base = TokenType("Token_base", (), {})

    class Token(Token_base):
        pass

    class NullFormatter(object):
        def __init__(self, **options):
            self.options = options

        def format(self, tokensource, outfile):
            for t, v in tokensource:
                outfile.write(v.encode("utf-8"))

    Formats = {
        "Null": NullFormatter(),
    }
else:
    logger.verbose("pygments package imported")
    has_pygments = True

    dark = {
        Token.Literal  : "#fff",
        Token.Address  : "#fb0",
        Token.Orange   : "#fb0",
        Token.Constant : "#f30",
        Token.Red      : "#f30",
        Token.Prefix   : "#fff",
        Token.Mnemonic : "bold",
        Token.Register : "#33f",
        Token.Memory   : "#3ff",
        Token.String   : "#3f3",
        Token.Segment  : "#888",
        Token.Comment  : "#f8f",
        Token.Green    : "#8f8",
        Token.Good     : "bold #8f8",
        Token.Name     : "bold",
        Token.Alert    : "bold #f00",
        Token.Column   : "#000",
    }
    S = {}
    for k in dark.keys():
        S[getattr(k,'Mark')]  = "bg:#224"
        S[getattr(k,'Taint')] = "bg:#422"
        S[getattr(k,'Hide')]  = "noinherit #222"
    dark.update(S)

    class DarkStyle(Style):
        default_style = ""
        styles = dark

    light = {
        Token.Literal  : "",
        Token.Address  : "#c30",
        Token.Orange   : "#c30",
        Token.Constant : "#d00",
        Token.Red      : "#d00",
        Token.Prefix   : "#000",
        Token.Mnemonic : "bold",
        Token.Register : "#00f",
        Token.Memory   : "#00c0c0",
        Token.String   : "#008800",
        Token.Segment  : "#888",
        Token.Comment  : "#a3a",
        Token.Green    : "#008800",
        Token.Good     : "bold #008800",
        Token.Name     : "bold",
        Token.Alert    : "bold #f00",
        Token.Column   : "#fff",
    }
    S = {}
    for k in light.keys():
        S[getattr(k,'Mark')]  = "bg:#aaaaff"
        S[getattr(k,'Taint')] = "bg:#ffaaaa"
        S[getattr(k,'Hide')]  = "noinherit #fff"
    light.update(S)

    class LightStyle(Style):
        default_style = ""
        styles = light

    DefaultStyle = DarkStyle

    Formats = {
        "Null"         : NullFormatter(encoding="utf-8"),
        "Terminal"     : TerminalFormatter(style=DefaultStyle, encoding="utf-8"),
        "Terminal256"  : Terminal256Formatter(style=DefaultStyle, encoding="utf-8"),
        "TerminalDark" : Terminal256Formatter(style=DarkStyle, encoding="utf-8"),
        "TerminalLight": Terminal256Formatter(style=LightStyle, encoding="utf-8"),
        "Html"         : HtmlFormatter(style=LightStyle, encoding="utf-8"),
    }


def highlight(toks, formatter=None, outfile=None):
    formatter = formatter or Formats.get(conf.UI.formatter,"Null")
    if isinstance(formatter, str):
        formatter = Formats[formatter]
    outfile = outfile or StringIO()
    formatter.format(toks, outfile)
    return outfile.getvalue().decode("utf-8")


def TokenListJoin(j, lst):
    if isinstance(j, str):
        j = (Token.Literal, j)
    res = lst[0]
    if not isinstance(res,list):
        res = [res]
    for x in lst[1:]:
        res.append(j)
        if isinstance(x,list):
            res.extend(x)
        else:
            res.append(x)
    return res


class vltable(object):
    """
    variable length table relies on pygments to pretty print tabulated data.

    Arguments:
        rows (list): optional argument with initial list of tokenrows.
        formatter (Formatter): optional pygment's formatter to use
                               (defaults to conf.UI.formatter.)
        outfile (file): optional output file passed to the formatter
                               (defaults to StringIO.)

    Attributes:
        rows (list of tokenrow): lines of the table, with tabulated data.
        rowparams (dict): parameters associated with a line.
        maxlength: maximum number of lines (default to infinity).
        hidden_r (set): rows that should be hidden.
        squash_r (bool): row is removed if True or empty if False.
        hidden_c (set): columns that should be hidden.
        squash_c (bool): column is removed if True or empty if False.
        colsize  (dict): mapping column index to its required width.
        width (int): total width of the table.
        height (int): total heigth of the table.
        nrows (int): total number of rows (lines).
        ncols (int): total number of columns.
        header (str): table header line (empty by default).
        footer (str): table footer line (empty by default).
    """

    def __init__(self, rows=None, formatter=None, outfile=None):
        if rows is None:
            rows = []
        self.rows = rows
        self.rowparams = {
            "colsize": {},
            "hidden_c": set(),
            "squash_c": True,
            "formatter": formatter,
            "outfile": outfile,
        }
        self.maxlength = float("inf")
        self.hidden_r = set()
        self.hidden_c = self.rowparams["hidden_c"]
        self.squash_r = True
        self.colsize = self.rowparams["colsize"]
        self.update()
        self.header = ""
        self.footer = ""

    def update(self, *rr):
        "recompute the column width over rr range of rows, and update colsize array"
        for c in range(self.ncols):
            cz = self.colsize.get(c, 0) if len(rr) > 0 else 0
            self.colsize[c] = max(cz, self.getcolsize(c, rr, squash=False))

    def getcolsize(self, c, rr=None, squash=True):
        "compute the given column width (over rr list of row indices if not None.)"
        cz = 0
        if not rr:
            rr = range(self.nrows)
        for i in rr:
            if self.rowparams["squash_c"] and (i in self.hidden_r):
                if squash:
                    continue
            cz = max(cz, self.rows[i].colsize(c))
        return cz

    @property
    def width(self):
        sep = self.rowparams.get("sep", "")
        cs = self.ncols * len(sep)
        return sum(self.colsize.values(), cs)

    def setcolsize(self, c, value):
        "set column size to value"
        i = range(self.ncols)[c]
        self.colsize[i] = value

    def addcolsize(self, c, value):
        "set column size to value"
        i = range(self.ncols)[c]
        self.colsize[i] += value

    def addrow(self, toks):
        "add row of given list of tokens and update table"
        self.rows.append(tokenrow(toks))
        self.update()
        return self

    def addcolumn(self,lot,c=None):
        "add column with provided toks (before index c if given) and update table"
        if c is None:
            c = self.ncols
        for ir,toks in enumerate(lot):
            if ir < self.nrows:
                r = self.rows[ir]
                for _ in range(r.ncols,c):
                    r.cols.append([(Token.Column, "")])
                toks.insert(0,(Token.Column, ""))
                r.cols.insert(c,toks)
            else:
                logger.warning("addcolumn: to much rows in provided list of tokens")
                break
        self.update()
        return self

    def hiderow(self, n):
        "hide given row"
        self.hidden_r.add(n)

    def showrow(self, n):
        "show given row"
        self.hidden_r.remove(n)

    def hidecolumn(self, n):
        "hide given column"
        self.hidden_c.add(n)

    def showcolumn(self, n):
        "show given column"
        self.hidden_c.remove(n)

    def showall(self):
        "remove all hidden rows/cols"
        self.hidden_r = set()
        self.rowparams["hidden_c"] = set()
        self.hidden_c = self.rowparams["hidden_c"]
        return self

    def grep(self, regex, col=None, invert=False):
        "search for a regular expression in the table"
        L = set()
        R = range(self.nrows)
        for i in R:
            if i in self.hidden_r:
                continue
            C = self.rows[i].rawcols(col)
            for c, s in enumerate(C):
                if c in self.hidden_c:
                    continue
                if re.search(regex, s):
                    L.add(i)
                    break
        if not invert:
            L = set(R) - L
        for n in L:
            self.hiderow(n)
        return self

    @property
    def nrows(self):
        return len(self.rows)

    @property
    def ncols(self):
        if self.nrows > 0:
            return max((r.ncols for r in self.rows))
        else:
            return 0

    def __str__(self):
        s = []
        formatter = self.rowparams["formatter"]
        outfile = self.rowparams["outfile"]
        for i in range(self.nrows):
            if i in self.hidden_r:
                if not self.squash_r:
                    s.append(
                        highlight(
                            [
                                (
                                    Token.Hide,
                                    self.rows[i].show(raw=True, **self.rowparams),
                                )
                            ],
                            formatter,
                            outfile,
                        )
                    )
            else:
                s.append(self.rows[i].show(**self.rowparams))
        if len(s) > self.maxlength:
            s = s[: self.maxlength - 1]
            s.append(highlight([(Token.Literal, icons.dots)], formatter, outfile))
        if self.header:
            s.insert(0, self.header)
        if self.footer:
            s.append(self.footer)
        return "\n".join(s)


class tokenrow(object):
    """
    A vltable row (line) of tabulated data tokens.

    Attributes:
        toks (list): list of tokens tuple (Token.Type, str).
        maxwidth: maximum authorized width of this row.
        align (str): left/center/right aligment indicator (default to "<" left).
        fill (str): fill character used for padding to required size.
        separator (str): character used for separation of columns.
        cols (list): list of columns of tokens.
        ncols (int): number of columns in this row.
    """
    def __init__(self, toks=None):
        if toks is None:
            toks = []
        self.maxwidth = float("inf")
        self.align = "<"
        self.fill = " "
        self.separator = ""
        toks = [(t, "%s" % s) for (t, s) in toks]
        self.cols = self.cut(toks)

    def cut(self,toks):
        "cut the raw list of tokens into a list of column of tokens"
        C = []
        c = []
        for t in toks:
            c.append(t)
            if t[0] == Token.Column:
                C.append(c)
                c = []
        C.append(c)
        return C

    def colsize(self, c):
        "return the column size (width)"
        if c >= len(self.cols):
            return 0
        return sum((len(t[1]) for t in self.cols[c] if t[0] != Token.Column))

    @property
    def ncols(self):
        return len(self.cols)

    def rawcols(self, j=None):
        "return the raw (undecorated) string of this row (j-th column if given)"
        r = []
        cols = self.cols
        if j is not None:
            cols = self.cols[j : j + 1]
        for c in cols:
            r.append("".join([t[1] for t in c]))
        return r

    def show(self, raw=False, **params):
        "highlight the row with optional parameters"
        formatter = params.get("formatter", None)
        outfile = params.get("outfile", None)
        align = params.get("align", self.align)
        fill = params.get("fill", self.fill)
        sep = params.get("sep", self.separator)
        width = params.get("maxwidth", self.maxwidth)
        colsz = params.get("colsize")
        hidden_c = params.get("hidden_c", set())
        squash_c = params.get("squash_c", True)
        head = params.get("head", "")
        tail = params.get("tail", "")
        if raw:
            formatter = "Null"
            outfile = None
        r = [head]
        tz = 0
        for i, c in enumerate(self.cols):
            toks = []
            sz = 0
            mz = colsz[i]
            tz += mz
            if tz > width:
                mz = mz - (tz - width)
            skip = False
            for tt, tv in c:
                if tt == Token.Column:
                    break
                if skip:
                    continue
                toks.append([tt, "%s" % tv])
                sz += len(tv)
                if sz > mz:
                    q = (sz - mz) + 3
                    toks[-1][1] = tv[0:-q] + "###"
                    skip = True
            if sz < mz:
                pad = fill * (mz - sz)
                if align == "<":
                    toks[-1][1] += pad
                elif align == ">":
                    toks[0][1] = pad + toks[0][1]
            if i in hidden_c:
                if not squash_c:
                    toks = [(Token.Hide, highlight(toks, "Null", None))]
                else:
                    toks = []
            r.append(highlight(toks, formatter, outfile))
            if tt == Token.Column and sep:
                r.append(sep)
        r.append(tail)
        return "".join(r)

class Icons:
    sep   = ' | '
    dots  = '...'
    tri   = ' > '
    lar   = ' <- '
    dbl   = '='
    hor   = '-'
    ver   = '|'
    top   = 'T'
    bot   = '_'
    usep  = ' \u2502 '
    udots = '\u2504 '
    utri  = ' \u25b6 '
    ular  = ' \u21fd '
    udbl  = '\u2550'
    uhor  = '\u2500'
    uver  = '\u2502'
    utop  = '\u22A4'
    ubot  = '\u22A5'
    mop   = {}

    def __getattribute__(self,a):
        if a not in ('mop','op') and conf.UI.unicode:
            return super().__getattribute__('u'+a)
        else:
            return super().__getattribute__(a)
    def op(self,symbol):
        if conf.Cas.unicode:
            return self.mop.get(symbol,symbol)
        else:
            return symbol

icons = Icons()
# define operator unicode symbols:
icons.mop["-"]   = "\u2212"
icons.mop["**"]  = "\u2217"
icons.mop["&"]   = "\u2227"
icons.mop["|"]   = "\u2228"
icons.mop["^"]   = "\u2295"
icons.mop["~"]   = "\u2310"
icons.mop["=="]  = "\u225f"
icons.mop["!="]  = "\u2260"
icons.mop["<="]  = "\u2264"
icons.mop[">="]  = "\u2265"
icons.mop[">=."] = "\u22DD"
icons.mop["<."]  = "\u22D6"
icons.mop["<<"]  = "\u226a"
icons.mop[">>"]  = "\u226b"
icons.mop[".>>"] = "\u00B1\u226b"
icons.mop["<<<"] = "\u22d8"
icons.mop[">>>"] = "\u22d9"

def replace_mnemonic_token(l,value):
    for i in range(len(l)):
        tn,tv = l[i]
        if tn==Token.Mnemonic:
            tv = value.ljust(len(tv))
        l[i] = (tn,tv)

def replace_opn_token(l,n,value):
    index = 1+(2*n)
    if value is None:
        if index+1 < len(l):
            l.pop(index+1)
            l.pop(index)
    else:
        tn,tv = l[index]
        if isinstance(value,tuple):
            l[index] = value
        else:
            l[index] = (tn, value)
