# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from PySide2.QtGui import QStandardItem, QBrush
from amoco.system.structs import StructCore,Field

from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")

from amoco.ui.render import highlight

class StructItem(QStandardItem):
    def __init__(self,label,data=None,offset=None):
        super().__init__(label)
        if isinstance(data,StructCore):
            self.struct = data
            self.offset = offset
            cname = data.__class__.__name__
            for f in data.fields:
                try:
                    val = data[f.name]
                except AttributeError:
                    logger.warn("%s.%s has no value"%(cname,f.name))
                    i = [StructItem(f.name),
                         StructItem("None"),
                         StructItem("%d"%len(f))]
                else:
                    if isinstance(val,StructCore):
                        # insert an expandable row:
                        i = [StructItem(f.name,val,
                                        offset=self.offset+data.offset_of(f.name)),
                             StructItem(""),
                             StructItem("%d"%len(f))]
                    else:
                        # insert a terminating row with name/value/size columns:
                        value = data.fkeys[f.name](f.name,val,cname,"Null")
                        i = [StructItem(f.name),
                             StructItem(value),
                             StructItem("%d"%len(f))]
                self.appendRow(i)

    def colorize(self,color):
        self.setBackground(QBrush(color))
