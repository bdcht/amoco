# -*- coding: utf-8 -*-
try:
    from builtins import bytes
except ImportError:
    pass

from amoco.config import conf

from amoco.logger import Log
logger = Log(__name__)
logger.debug('loading module')

from amoco.cas.expressions import regtype
from amoco.ui.graphics import Engine
from amoco.ui.render import Token,vltable

#-------------------------------------------------------------------------------

class View(Engine):
    """Class that implements common API for views.
    A view represents an amoco element (either a block, a map or a function) as
    a positionable "boxed" object, ie an object with (width,height) and (x,y)
    coords. A view is bound to the configured graphics engine through its parent
    Engine class and offers a common API to display its object.

    Args:
        of: the amoco element associated with this view.

    Attributes:
        of: the amoco element associated with this view.
        obj: the engine's graphical object that represents "of".
        w: the width of the view.
        h: the height of the view.
        xy (tuple[int]): the (x,y) coords of the view.
    """
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

#-------------------------------------------------------------------------------

class blockView(View):
    """Class that implements view of code.block objects.
    A blockView additionnally implements the _vltable method which allows to
    pretty print the block through ui.render.highlight method.
    The str() representation of a blockView instance uses this pretty printer.
    """
    _is_block = True

    def __init__(self,block):
        super(blockView,self).__init__(of=block)

    def _vltable(self,**kargs):
        T = vltable(**kargs)
        n = len(self.of.instr)
        for i in self.of.instr:
            ins2 = i.toks()
            if isinstance(ins2,str): ins2 = [(Token.Literal,ins2)]
            b = [u"%02x"%x for x in bytes(i.bytes)]
            ins = [ (Token.Address,u'{:<20}'.format(str(i.address))),
                    (Token.Column,u''),
                    (Token.Literal,u"'%s'"%(u''.join(b))),
                    (Token.Column,u'') ]
            T.addrow(ins+ins2)
        if conf.Code.bytecode:
            pad = conf.Code.padding
            T.colsize[1] += pad
        if conf.Code.header:
            th = u'# --- block %s ---'
            T.header = (th % self.of.address).ljust(T.width,'-')
        if conf.Code.footer:
            T.footer = u'-'*T.width
        return T

    def __str__(self):
        return str(self._vltable())

#-------------------------------------------------------------------------------

class mapView(View):
    """Class that implements view of mapper objects.
    A mapView additionnally implements the _vltable method which allows to
    pretty print the map through ui.render.highlight method.
    The str() representation of a mapView instance uses this pretty printer.
    """
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

#-------------------------------------------------------------------------------

class funcView(View):
    """Class that implements view of func objects.
    A funcView additionnally implements the _vltable method which allows to
    pretty print the function through ui.render.highlight method.
    """
    _is_func = True
    def __init__(self,func):
        from grandalf.layouts import SugiyamaLayout
        super(funcView,self).__init__(of=func)
        self.layout = SugiyamaLayout(func.cfg)

    def _vltable(self,**kargs):
        t = vltable(**kargs)
        w = t.width
        th = u'[func %s, signature: %s]'
        t.header = (th%(self.of,self.of.sig())).ljust(w,'-')
        t.footer = u'_'*w

#-------------------------------------------------------------------------------

class xfuncView(View):
    _is_xfunc = True
    def __init__(self,xfunc):
        super(xfuncView,self).__init__(of=xfunc)

#-------------------------------------------------------------------------------
