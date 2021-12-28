# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from os import path

from PySide2.QtCore import Qt, QUrl
from PySide2.QtWidgets import (QMainWindow,
                               QDockWidget,
                               QTreeView,
                               QAction,
                              )

from PySide2.QtQuickWidgets import QQuickWidget

from . import rc_icons

from .binfmtview import BinFmtView
from .infoview import InfoView
from .hexview import HexView

__all__ = ['TaskWindow','HexView']

class TaskWindow(QMainWindow):
    def __init__(self, v):
        super().__init__()
        self.setWindowTitle(repr(v.of))
        self.createMenus()
        self.createDocks(v.of)
        self.createCentral(v)
        if self.binfmt is not None:
            self.binfmt.clicked.connect(self.binfmt_clicked)
            self.hexview.clicked.connect(self.hexview_clicked)
        self.statusBar().showMessage("TaskWindow ready")

    def createMenus(self):
        self.viewMenu = self.menuBar().addMenu("&Views")
        self.editMenu = self.menuBar().addMenu("&Edit")

    def createDocks(self,task):
        self.createDockBin(task)
        self.createDockInfo(task)

    def createDockBin(self,task):
        # TreeView for ELF/PE/Mach-O structure
        dock = QDockWidget("[task].view.obj.binfmt", self)
        #dock.setAllowedAreas(Qt.TopDockWidgetArea)
        dock.setFeatures(dock.DockWidgetClosable|\
                         dock.DockWidgetMovable|\
                         dock.DockWidgetFloatable)
        dock.setMinimumWidth(364)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        a = dock.toggleViewAction()
        self.viewMenu.addAction(a)
        self.binfmt = BinFmtView(task)
        if self.binfmt is not None:
            dock.setWidget(self.binfmt)
            enabled = True
        else:
            dock.hide()
            enabled = False
        a.setEnabled(enabled)
        a.setChecked(enabled)

    def createDockInfo(self,task):
        dock = QDockWidget("[task].view.obj.info", self)
        dock.setFeatures(dock.DockWidgetClosable|\
                         dock.DockWidgetMovable|\
                         dock.DockWidgetFloatable)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        a = dock.toggleViewAction()
        self.viewMenu.addAction(a)
        self.info = InfoView(task)
        if self.info is not None:
            dock.setWidget(self.info)
            enabled = True
        else:
            dock.hide()
            enabled = False
        a.setEnabled(enabled)
        a.setChecked(enabled)

    def createCentral(self,v):
        self.hexview = HexView(self)
        self.setCentralWidget(self.hexview)
        # the HexView wants to access the raw data bytes
        # of the current binary:
        self.hexview.setData(v.of.bin.dataio)

    def binfmt_clicked(self,index):
        name_index = index.siblingAtColumn(0)
        m = self.binfmt.model()
        item = m.itemFromIndex(name_index)
        color = self.hexview.select_color
        item.colorize(color)
        self.binfmt.update()
        if hasattr(item,'struct'):
            offset = item.offset
            size = len(item.struct)
        else:
            parent = item.parent()
            if parent is None: return
            offset = parent.offset + parent.struct.offset_of(item.text())
            size = int(m.data(index.siblingAtColumn(2)))
        self.statusBar().showMessage("%d bytes @ %+08x"%(size,offset))
        self.hexview.colorize(offset,size,color)
        n = self.hexview.height()/self.hexview.line.height
        self.hexview.vb.setValue(self.hexview.addrToLine(offset)-n/2)
        self.hexview.update()

    def hexview_clicked(self,*args):
        m = self.binfmt.model()
        self.statusBar().showMessage(str(args))

