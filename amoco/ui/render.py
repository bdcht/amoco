# -*- coding: utf-8 -*-

from cStringIO import StringIO

from amoco.logger import Log
logger = Log(__name__)

import re

try:
    from pygments.token import Token
    from pygments.style import Style
    from pygments.lexer import RegexLexer
    from pygments.formatters import *
except ImportError:
    logger.info("pygments package not found, no renderer defined")
    has_pygments = False

    class TokenType(type):
        def __getattr__(cls,key):
            return key
    class Token:
        __metaclass__ = TokenType

    class NullFormatter(object):
        def __init__(self,**options):
            self.options = options
        def format(self,tokensource,outfile):
            for t,v in tokensource:
                outfile.write(v)
    Formats = {
      'Null':NullFormatter(),
    }
else:
    logger.info("pygments package imported")
    has_pygments = True
    class DarkStyle(Style):
        default_style = ""
        styles = {
          #Token.Literal:  '#fff',
          Token.Address:  '#fb0',
          Token.Constant: '#f30',
          #Token.Prefix:   '#fff',
          Token.Mnemonic: 'bold',
          Token.Register: '#33f',
          Token.Memory:   '#3ff',
          Token.Comment:  '#8f8',
          Token.Name:     'underline',
          Token.Tainted:  'bold #f00',
          Token.Column:   '#bbb',
          Token.Hide:     '#222',
        }
    class LightStyle(Style):
        default_style = ""
        styles = {
          Token.Literal:  '#000',
          Token.Address:  '#b58900',
          Token.Constant: '#dc322f',
          Token.Prefix:   '#000',
          Token.Mnemonic: 'bold',
          Token.Register: '#268bd2',
          Token.Memory:   '#859900',
          Token.Comment:  '#93a1a1',
          Token.Name:     'underline',
          Token.Tainted:  'bold #f00',
          Token.Column:   '#222',
          Token.Hide:     '#bbb',
        }
    DefaultStyle = DarkStyle

    Formats = {
      'Null':NullFormatter(),
      'Terminal':TerminalFormatter(style=DefaultStyle),
      'Terminal256':Terminal256Formatter(style=DefaultStyle),
      'TerminalDark':Terminal256Formatter(style=DarkStyle),
      'TerminalLight':Terminal256Formatter(style=LightStyle),
      'Html':HtmlFormatter(style=LightStyle,nowrap=True),
    }

default_formatter = NullFormatter()

def configure(**kargs):
    from amoco.config import get_module_conf
    conf = get_module_conf('ui')
    conf.update(kargs)
    f = conf['formatter']
    global default_formatter
    default_formatter = Formats.get(f,default_formatter)

configure()

def highlight(toks,formatter=None,outfile=None):
    formatter = formatter or default_formatter
    if isinstance(formatter,str): formatter = Formats[formatter]
    outfile = outfile or StringIO()
    formatter.format(toks,outfile)
    return outfile.getvalue()

def TokenListJoin(j,lst):
    if isinstance(j,str):
        j = (Token.Literal,j)
    res = lst[0:1]
    for x in lst[1:]:
        res.append(j)
        res.append(x)
    return res

class vltable(object):
    '''
    variable length table:
    '''
    def __init__(self,rows=None,formatter=None,outfile=None):
        if rows is None: rows = []
        self.rows = rows
        self.rowparams = {'colsize':{},
                          'hidden_c': set(),
                          'squash_c': True,
                          'formatter':formatter,
                          'outfile':outfile,
                         }
        self.maxlength = float('inf')
        self.hidden_r  = set()
        self.hidden_c  = self.rowparams['hidden_c']
        self.squash_r  = True
        self.colsize   = self.rowparams['colsize']
        self.update()
        self.header    = ''
        self.footer    = ''

    def update(self,*rr):
        for c in range(self.ncols):
            cz = self.colsize.get(c,0) if len(rr)>0 else 0
            self.colsize[c] = max(cz,self.getcolsize(c,rr,squash=False))

    def getcolsize(self,c,rr=None,squash=True):
        cz = 0
        if not rr: rr = range(self.nrows)
        for i in rr:
            if self.rowparams['squash_c'] and (i in self.hidden_r):
                if squash: continue
            cz = max(cz,self.rows[i].colsize(c))
        return cz

    @property
    def width(self):
        sep = self.rowparams.get('sep','')
        cs = self.ncols*len(sep)
        return sum(self.colsize.values(),cs)

    def setcolsize(self,c,value):
        self.colsize[c] = value

    def addrow(self,toks):
        self.rows.append(tokenrow(toks))
        self.update(-1)
        return self

    def hiderow(self,n):
        self.hidden_r.add(n)
    def showrow(self,n):
        self.hidden_r.remove(n)

    def hidecolumn(self,n):
        self.hidden_c.add(n)
    def showcolumn(self,n):
        self.hidden_c.remove(n)

    def showall(self):
        self.hidden_r = set()
        self.rowparams['hidden_c'] = set()
        self.hidden_c = self.rowparams['hidden_c']
        return self

    def grep(self,regex,col=None,invert=False):
        L = set()
        R = range(self.nrows)
        for i in R:
            if i in self.hidden_r: continue
            C = self.rows[i].rawcols(col)
            for c,s in enumerate(C):
                if c in self.hidden_c:
                    continue
                if re.search(regex,s):
                    L.add(i)
                    break
        if not invert: L = set(R)-L
        for n in L: self.hiderow(n)
        return self

    @property
    def nrows(self):
        return len(self.rows)

    @property
    def ncols(self):
        if self.nrows>0:
            return max((r.ncols for r in self.rows))
        else:
            return 0

    def __str__(self):
        s = []
        formatter=self.rowparams['formatter']
        outfile=self.rowparams['outfile']
        for i in range(self.nrows):
            if i in self.hidden_r:
                if not self.squash_r:
                    s.append(highlight([(Token.Hide,
                                         self.rows[i].show(raw=True,**self.rowparams))],
                                       formatter,
                                       outfile,
                                       ))
            else:
                s.append(self.rows[i].show(**self.rowparams))
        if len(s)>self.maxlength:
            s = s[:self.maxlength-1]
            s.append(highlight([(Token.Literal,'...')],formatter,outfile))
        if self.header: s.insert(0,self.header)
        if self.footer: s.append(self.footer)
        return '\n'.join(s)


class tokenrow(object):
    def __init__(self,toks=None):
        if toks is None: toks = []
        self.toks      = [(t,unicode(s)) for (t,s) in toks]
        self.maxwidth  = float('inf')
        self.align     = '<'
        self.fill      = ' '
        self.separator = ''
        self.cols      = self.cut()

    def cut(self):
        C = []
        c = []
        for t in self.toks:
            c.append(t)
            if t[0]==Token.Column:
                C.append(c)
                c = []
        C.append(c)
        return C

    def colsize(self,c):
        if c>=len(self.cols): return 0
        return sum((len(t[1]) for t in self.cols[c] if t[0]!=Token.Column))

    @property
    def ncols(self):
        return len(self.cols)

    def rawcols(self,j=None):
        r = []
        cols = self.cols
        if j is not None: cols = self.cols[j:j+1]
        for c in cols:
            r.append(''.join([t[1] for t in c]))
        return r

    def show(self,raw=False,**params):
        formatter = params.get('formatter',None)
        outfile   = params.get('outfile',None)
        align     = params.get('align',self.align)
        fill      = params.get('fill',self.fill)
        sep       = params.get('sep',self.separator)
        width     = params.get('maxwidth',self.maxwidth)
        colsz     = params.get('colsize')
        hidden_c  = params.get('hidden_c',set())
        squash_c  = params.get('squash_c',True)
        head      = params.get('head','')
        tail      = params.get('tail','')
        if raw:
            formatter='Null'
            outfile=None
        r = [head]
        tz = 0
        for i,c in enumerate(self.cols):
            toks = []
            sz   = 0
            mz   = colsz[i]
            tz  += mz
            if tz>width: mz = mz-(tz-width)
            skip = False
            for tt,tv in c:
                if tt==Token.Column: break
                if skip: continue
                toks.append([tt,tv])
                sz += len(tv)
                if sz>mz:
                    q = (sz-mz)
                    toks[-1][1] = tv[0:-q]+'###'
                    skip = True
            if sz<mz:
                pad = fill*(mz-sz)
                if   align=='<': toks[-1][1] += pad
                elif align=='>': toks[0][1] = pad+toks[0][1]
            if i in hidden_c:
                if not squash_c:
                    toks = [(TokenHide,highlight(toks,'Null',None))]
                else:
                    toks = []
            r.append(highlight(toks,formatter,outfile))
            if tt==Token.Column and sep: r.append(sep)
        r.append(tail)
        return ''.join(r)
