# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from PySide6.QtCore import Qt, Signal, QObject, QAbstractItemModel

class DataIOModel(QObject):
    UPDATED = Signal()
    def __init__(self,parent=None,data=None):
        super().__init__(parent)
        self.data = data
        self.full = data[0:]
        self.cur = 0
        self.linesize = 16

    def cursor(self):
        return self.cur

    def iterlines(self,count):
        sz = self.linesize
        offset = sz*(self.cur)
        for i in range(count):
            l = self.data[offset:offset+sz]
            t = []
            for c in l:
                if 32<=c<=127:
                    t.append(chr(c))
                else:
                    t.append('.')
            if len(l)==0:
                break
            yield (offset,l,t)
            offset += sz

#--------------------------------------------------------------------------------------------------

class StructModel(QAbstractItemModel):
    def __init__(self, parent=None, S=None):
        super().__init__(parent)
        self.insertColumns(0,3)
        if S is not None:
            self.of = S
            self.insertRows(0,len(S.fields))

