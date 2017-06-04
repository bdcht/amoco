# -*- coding: utf-8 -*-
from builtins import bytes

from amoco.config import conf
from amoco.logger import Log
logger = Log(__name__)

from amoco.cas.expressions import regtype
from amoco.ui.graphics import Engine
from amoco.ui.render import Token,vltable

class View(Engine):
    _is_block = False
    _is_map   = False
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
            ins = [ (Token.Address,u'{:<20}'.format(str(i.address))),
                    (Token.Column,u''),
                    (Token.Literal,u"'%s'"%(u''.join([u"%02x"%x for x in bytes(i.bytes)]))),
                    (Token.Column,u'') ]
            T.addrow(ins+ins2)
        if conf.getboolean('block','bytecode'):
            pad = conf.getint('block','padding') or 0
            T.colsize[1] += pad
        if conf.getboolean('block','header'):
            T.header = (u'# --- block %s ---' % self.of.name).ljust(T.width,'-')
        if conf.getboolean('block','footer'):
            T.footer = u'-'*T.width
        return T

    def __str__(self):
        return str(self._vltable())

class mapView(View):
    _is_map = True

    def __init__(self,m):
        super(mapView,self).__init__(of=m)

    def _vltable(self,**kargs):
        t = vltable(**kargs)
        t.rowparams['sep'] = ' <- '
        for (l,v) in self.of:
            if l._is_reg:
                if l.type == regtype.FLAGS:
                    t.addrow(l.toks(**kargs)+[(Token.Literal,':')])
                    for pos,sz in l._subrefs:
                        t.addrow([(Token.Literal,'| ')]+
                                 l[pos:pos+sz].toks(**kargs)+
                                 [(Token.Column,u'')]+
                                 v[pos:pos+sz].toks(**kargs))
                    continue
                v = v[0:v.size]
            lv = (l.toks(**kargs)+
                  [(Token.Column,u'')]+
                  v.toks(**kargs))
            t.addrow(lv)
        return t

    def __str__(self):
        return self._vltable().__str__()

class funcView(View):
    _is_func = True
    def __init__(self,func):
        from grandalf.layouts import SugiyamaLayout
        super(funcView,self).__init__(of=func)
        self.layout = SugiyamaLayout(func.cfg)

class xfuncView(View):
    _is_xfunc = True
    def __init__(self,xfunc):
        super(xfuncView,self).__init__(of=xfunc)
