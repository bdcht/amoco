# -*- coding: utf-8 -*-
try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    from PySide2.QtWidgets import QApplication
    from PySide2.QtCore import QPointF

from amoco.ui.render import Formats
from .graphwin import *
from .mainwin import *

app = QApplication([])


def builder(view):
    if view._is_block:
        fmt = Formats["Html"]
        tbl = view._vltable(formatter=fmt)
        tbl.rowparams["head"] = "<tr><td>"
        tbl.rowparams["sep"] = "</td><td>"
        tbl.rowparams["tail"] = "</td></tr>"
        tbl.header = (
            "<html><head><style>\n%s\n</style></head>\n<body>\n<table bgcolor='#fdf6e3'>\n"
            % fmt.get_style_defs()
        )
        tbl.footer = "</table>\n</body>\n</html>"
        return Node_codeblock(str(tbl))
    elif view._is_func:
        r = len(view.of.blocks) * 5
        return Node_basic(str(view.of), r)
    else:
        return Node_basic(str(view.of))


def setw(view, w):
    pass


def seth(view, h):
    pass


def getw(view):
    return view.obj.boundingRect().width()


def geth(view):
    return view.obj.boundingRect().height()


def setxy(view, xy):
    view.obj.setPos(QPointF(*xy) - view.obj.center())


def getxy(view):
    pt = view.obj.center()
    return (pt.x(), pt.y())
