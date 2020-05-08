# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

class engine(object):

    @staticmethod
    def builder(view):
        return view._vltable()

    @staticmethod
    def setw(view, w):
        pass

    @staticmethod
    def getw(view):
        try:
            return view._vltable().width
        except Exception:
            return len(str(view.of))

    @staticmethod
    def seth(view, h):
        pass

    @staticmethod
    def geth(view):
        try:
            return view._vltable().nrows
        except Exception:
            return 1

    @staticmethod
    def setxy(view, xy):
        pass

    @staticmethod
    def getxy(view):
        return None

    @staticmethod
    def pp(view):
        return view._vltable().__str__()


