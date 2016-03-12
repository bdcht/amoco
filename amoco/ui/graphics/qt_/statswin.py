from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

class StatsWin(QWebEngineView):
    def __init__(self,parent=None,cur=None):
        super(StatsWin,self).__init__(parent)
