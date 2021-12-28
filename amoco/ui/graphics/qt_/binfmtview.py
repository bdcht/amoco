# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTreeView, QHeaderView
from PySide2.QtGui import QStandardItemModel, QFont

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

class BinFmtView_core(QTreeView):
    def __init__(self, p):
        super().__init__()
        # enforce monospaced font:
        f = QFont("Monospace")
        f.setPointSize(8)
        self.setFont(f)
        self.setEditTriggers(QTreeView.NoEditTriggers)
        self.setSelectionMode(QTreeView.ExtendedSelection)
        m = QStandardItemModel()
        m.setColumnCount(3)
        m.setHorizontalHeaderLabels(["name","value","size"])
        r = m.invisibleRootItem()
        S = self.setup_(p)
        if S:
            r.appendRow(S)
        self.setModel(m)
        self.m = m
        self.setUniformRowHeights(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.header().setFont(f)

    def setup_(self,p):
        return None

# ------------------------------------------------------------------------------

class PEView(BinFmtView_core):
    def __init__(self,p):
        super().__init__(p)
        #expand PE root structure:
        x = self.m.index(0,0)
        self.expand(x)
        #expand the DOS structure:
        self.expand(self.indexBelow(x))
    def setup_(self, p):
        S = StructItem("PE")
        S.appendRow(StructItem("DOS",p.DOS))
        S.appendRow(StructItem("NT",p.NT))
        S.appendRow(StructItem("Opt",p.Opt))
        for s in p.sections:
            S.appendRow(StructItem(s.name,s))
        return S

# ------------------------------------------------------------------------------

class ELFView(BinFmtView_core):
    def __init__(self, p=None):
        super().__init__(p)
        #expand ELF root structure:
        x = self.m.index(0,0)
        self.expand(x)
        h = self.indexBelow(x)
        #expand the Ehdr structure:
        self.expand(h)
        #expand the Ehdr.e_ident structure:
        self.expand(self.indexBelow(h))
    def setup_(self,p):
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
        return S

# ------------------------------------------------------------------------------

class MachOView(BinFmtView_core):
    def __init__(self, p=None):
        super().__init__(p)

