# -*- coding: utf-8 -*-

class engine(object):

    @staticmethod
    def setw(view,w):
        pass

    @staticmethod
    def getw(view):
        if view._is_block:
            return view._vltable().width
        else:
            return len(str(view.of))

    @staticmethod
    def seth(view,h):
        pass

    @staticmethod
    def geth(view):
        if view._is_block:
            return view._vltable().nrows
        else:
            return 1

    @staticmethod
    def setxy(view,xy):
        view._xy = xy

    @staticmethod
    def getxy(view):
        return view._xy
