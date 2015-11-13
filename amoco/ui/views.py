# -*- coding: utf-8 -*-

from amoco.config import conf
from amoco.logger import Log
logger = Log(__name__)

from grandalf.layouts import SugiyamaLayout

from amoco.ui import graphics

class View(object):
    backend   = graphics.default

    def __init__(self,w=1,h=1,of=None):
        self.w = w
        self.h = h
        self.xy = None
        self.of = of

class blockView(View):
    def __init__(self,block):
        super(blockView,self).__init__(of=block)

class funcView(View):
    def __init__(self,func):
        super(funcView,self).__init__(of=func)
        self.layout = SugiyamaLayout(func.cfg)

class xfuncView(View):
    def __init__(self,xfunc):
        super(xfuncView,self).__init__(of=xfunc)
