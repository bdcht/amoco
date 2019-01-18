try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import *
except ImportError:
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import *

class StatsWin(QGraphicsView):
    def __init__(self,parent=None,cur=None):
        super(StatsWin,self).__init__(parent)
