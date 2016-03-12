# -*- coding: utf-8 -*-

from amoco.config import conf
from amoco.logger import Log
logger = Log(__name__)

from grandalf.layouts import SugiyamaLayout

from amoco.ui.graphics import Engine
from amoco.ui.render import Token,vltable

class View(Engine):
    _is_block = False
    _is_func  = False
    _is_xfunc = False

    def __init__(self,of=None):
        self.of = of

    @property
    def obj(self):
        try:
            return self._obj
        except AttributeError:
            self._obj = self.engine.builder(self)
            return self._obj

    def setw(self,w):
        self.engine.setw(self,w)
    def getw(self):
        return self.engine.getw(self)
    w = property(getw,setw)

    def seth(self,h):
        self.engine.seth(self,h)
    def geth(self):
        return self.engine.geth(self)
    h = property(geth,seth)

    def setxy(self,xy):
        self.engine.setxy(self,xy)
    def getxy(self):
        return self.engine.getxy(self)
    xy = property(getxy,setxy)


class blockView(View):
    _is_block = True

    def __init__(self,block):
        super(blockView,self).__init__(of=block)

    def _vltable(self,**kargs):
        T = vltable(**kargs)
        n = len(self.of.instr)
        for i in self.of.instr:
            ins2 = i.toks()
            if isinstance(ins2,str): ins2 = [(Token.Literal,ins2)]
            ins = [ (Token.Address,'{:<10}'.format(i.address)),
                    (Token.Column,''),
                    (Token.Literal,"'%s'"%(i.bytes.encode('hex'))),
                    (Token.Column,'') ]
            T.addrow(ins+ins2)
        if conf.getboolean('block','bytecode'):
            pad = conf.getint('block','padding') or 0
            T.colsize[1] += pad
        if conf.getboolean('block','header'):
            T.header = ('# --- block %s ---' % self.of.name).ljust(T.width,'-')
        if conf.getboolean('block','footer'):
            T.footer = '-'*T.width
        return T

    def __str__(self):
        return str(self._vltable())


class funcView(View):
    _is_func = True
    def __init__(self,func):
        super(funcView,self).__init__(of=func)
        self.layout = SugiyamaLayout(func.cfg)

class xfuncView(View):
    _is_xfunc = True
    def __init__(self,xfunc):
        super(xfuncView,self).__init__(of=xfunc)
