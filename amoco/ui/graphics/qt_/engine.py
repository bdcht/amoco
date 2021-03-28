# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from os import path
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QPointF

from amoco.ui.render import Formats
#from . import rc_icons

app = QApplication.instance() or QApplication([])
app.setApplicationName("amoco-qt")

# set default styleSheet:
current_path = path.abspath(path.dirname(__file__))
filename = path.join(current_path, 'style.qss')
with open(filename,'r') as f:
    _style = f.read()
    app.setStyleSheet(_style)

try:
    # integrate Qt mainloop into IPython console:
    # (the name qt4 here is a relic of the API but what happens
    # really is not restricted to Qt4...)
    from IPython.lib.guisupport import start_event_loop_qt4
    start_event_loop_qt4(app)
except ImportError:
    pass

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

def builder(view):
    """
    Implements the main API that allows view instances to
    build their graphic object for display.
    """
    t = view.__class__.__name__
    try:
        return DefineBuilder.All[t](view)
    except KeyError:
        logger.error("no builder defined for %s"%t)
        return None

class DefineBuilder(object):
    """
    A generic decorator that associates the view class name
    with its builder function.
    """

    All = {}

    def __init__(self,name):
        self.name = name
    def __call__(self,f):
        self.All[self.name] = f

# -----------------------------------------------------------------------------

from .graphwin import *

@DefineBuilder("blockView")
def blockView_builder(view):
    # get the HTML-formatted vltable for the view:
    fmt = Formats["Html"]
    tbl = view._vltable(formatter=fmt)
    # add HTML row decorators to output a table:
    tbl.rowparams["head"] = "<tr><td>"
    tbl.rowparams["sep"] = "</td><td>"
    tbl.rowparams["tail"] = "</td></tr>"
    tbl.header = ("<html>\n"
                  "<head><style>\n"
                  "%s\n"
                  "</style></head>\n"
                  "<body><table bgcolor='#fdf6e3'>\n"%fmt.get_style_defs())
    tbl.footer = "</table>\n</body>\n</html>"
    # return the associated Node_codeblock graphic object:
    return Node_codeblock(str(tbl))


@DefineBuilder("funcView")
def funcView_builder(view):
    r = len(view.of.blocks) * 5
    return Node_basic(str(view.of), r)

@DefineBuilder("xfuncView")
def xfuncView_builder(view):
    return Node_basic(str(view.of))

# -----------------------------------------------------------------------------

from .taskwin  import *

@DefineBuilder("dataView")
def dataView_builder(view):
    return HexView(data=view.of)

@DefineBuilder("execView")
def execView_builder(view):
    return TaskWindow(view)

# -----------------------------------------------------------------------------

# common (generic) API

# resizing Qt objects happens only from within Qt itself, not from amoco code:
def setw(view, w):
    pass

def seth(view, h):
    pass

# amoco graph drawing needs to know to bounding size of Qt nodes to compute
# the object's coordinates:
def getw(view):
    return view.obj.boundingRect().width()


def geth(view):
    return view.obj.boundingRect().height()


# amoco graph drawing will set Qt object positions through this API:
def setxy(view, xy):
    view.obj.setPos(QPointF(*xy) - view.obj.center())


# adaptive amoco graph drawing needs to know the current position of objects:
def getxy(view):
    pt = view.obj.center()
    return (pt.x(), pt.y())

# define how the engine prints a view on the terminal console.
# This allows to work simultaneously with Qt objects drawn on a Qt Window while
# still being able to print views on a terminal console (ipython or qtconsole).
def pp(view):
    return view._vltable().__str__()


# -----------------------------------------------------------------------------

# utilities

def is_dark(color):
    r, g, b = color.red(), color.green(), color.blue()
    luminance = (0.2126*r + 0.7152*g + 0.0722*b)/256
    return luminance < 0.5
