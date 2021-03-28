# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTreeView, QHeaderView
from PySide2.QtGui import QStandardItemModel

from .structview import StructItem

def BinFmtView(task):
    if task.bin.is_PE:
        v = PEView(task.bin)
    elif task.bin.is_ELF:
        v = ELFView(task.bin)
    elif task.bin.is_MachO:
        v = MachOView(task.bin)
    else:
        v = None
    return v

# ------------------------------------------------------------------------------

class PEView(QTreeView):
    def __init__(self, p):
        super().__init__()
        self.setEditTriggers(QTreeView.NoEditTriggers)
        self.setSelectionMode(QTreeView.ExtendedSelection)
        m = QStandardItemModel()
        m.setColumnCount(3)
        m.setHorizontalHeaderLabels(["name","value","size"])
        r = m.invisibleRootItem()
        S = StructItem("PE")
        S.appendRow(StructItem("DOS",p.DOS))
        S.appendRow(StructItem("NT",p.NT))
        S.appendRow(StructItem("Opt",p.Opt))
        for s in p.sections:
            S.appendRow(StructItem(s.name,s))
        r.appendRow(S)
        self.setModel(m)
        self.setUniformRowHeights(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        #expand PE root structure:
        x = m.index(0,0)
        self.expand(x)
        #expand the DOS structure:
        self.expand(self.indexBelow(x))

# ------------------------------------------------------------------------------

class ELFView(QTreeView):
    def __init__(self, p=None):
        super().__init__(None)
        self.setEditTriggers(QTreeView.NoEditTriggers)
        self.setSelectionMode(QTreeView.ExtendedSelection)
        m = QStandardItemModel()
        m.setHorizontalHeaderLabels(["name","value","size"])
        r = m.invisibleRootItem()
        S = StructItem("ELF")
        S.appendRow([StructItem("Ehdr",p.Ehdr,offset=0),
                     StructItem(""),
                     StructItem("%d"%len(p.Ehdr))])
        offset = p.Ehdr.e_phoff
        for i,s in enumerate(p.Phdr):
            S.appendRow([StructItem("Phdr[%d]"%i,s,offset),
                         StructItem(""),
                         StructItem("%d"%len(s))])
            offset += p.Ehdr.e_phentsize
        offset = p.Ehdr.e_shoff
        for s in p.Shdr:
            S.appendRow([StructItem(s.name,s,offset),
                         StructItem(""),
                         StructItem("%d"%len(s))])
            offset += p.Ehdr.e_shentsize
        r.appendRow(S)
        self.setModel(m)
        self.setUniformRowHeights(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        #expand ELF root structure:
        x = m.index(0,0)
        self.expand(x)
        h = self.indexBelow(x)
        #expand the Ehdr structure:
        self.expand(h)
        #expand the Ehdr.e_ident structure:
        self.expand(self.indexBelow(h))

# ------------------------------------------------------------------------------

class MachOView(QTreeView):
    def __init__(self, p=None):
        super().__init__(None)
