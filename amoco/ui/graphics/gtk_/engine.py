# -*- coding: utf-8 -*-

from .mainwin import gtkWindow
from .items import *

def builder(view):
    if view._is_block:
        return Node_codeblock(str(view.of))
    else:
        return Node_basic(name=str(view.of),r=50)

def setw(view,w):
    view.obj.set_properties('width',w)

def seth(view,h):
    view.obj.set_properties('height',h)

def getw(view):
    return view.obj.wh[0]

def geth(view):
    return view.obj.wh[1]

def setxy(view,xy):
    view.obj.xy = xy

def getxy(view):
    return view.obj.xy

