from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow,QDockWidget
from PyQt5.QtGui import QFont,QKeySequence
from PyQt5.Qt import QBrush, QPen, QColor

from .graphwin import GraphScene,GraphView
from .statswin import StatsWin

class MainWindow(QMainWindow):
    def __init__(self,z=None,session=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle("amoco-g")
        self.createSession(z,session)
        self.createActions()
        self.createMenus()
        self.createDockWindows()
        self.statusBar().showMessage("GUI ready")

    def createSession(self,z,session):
        from amoco.db import Session
        self.session = session or Session('/tmp/amoco.db')
        self.z = z
        self.statusBar().showMessage("session created (/tmp/amoco.db)")

    def createFuncGraph(self,f):
        self.grscene = GraphScene(f.view.layout)
        self.graphwin = GraphView(self.grscene)
        self.setCentralWidget(self.graphwin)
        self.grscene.Draw()

    def createActions(self):
        pass

    def createMenus(self):
        self.viewMenu = self.menuBar().addMenu("&View")

    def createDockWindows(self):
        self.createDockStats()
        self.createDockBin()
        self.createDockMap()
        self.createDockFuncs()

    def createDockStats(self):
        dock = QDockWidget('stats',self)
        dock.setAllowedAreas(Qt.TopDockWidgetArea)
        dock.setFeatures(dock.DockWidgetClosable|dock.DockWidgetVerticalTitleBar)
        self.statsui = StatsWin(dock,cur=self)
        self.statsui.setMaximumHeight(100)
        dock.setWidget(self.statsui)
        self.addDockWidget(Qt.TopDockWidgetArea, dock)
        a = dock.toggleViewAction()
        self.viewMenu.addAction(a)
        a.setEnabled(True)

    def createDockBin(self):
        pass

    def createDockMap(self):
        pass

    def createDockFuncs(self):
        pass

