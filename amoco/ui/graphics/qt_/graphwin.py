from .items import *
from grandalf.routing import *

class GraphScene(QGraphicsScene):

    def __init__(self,sug=None):
        super(GraphScene,self).__init__()
        p  = QPen()
        p.setColor(QColor('red'))
        self.addLine(-5,0,5,0,p)
        self.addLine(0,-5,0,5,p)
        self.sug = sug
        if self.sug:
            self.sug.route_edge = route_with_lines
            self.sug.dx,self.sug.dy = 5,5
            self.sug.dirvh=0
            for n in self.sug.g.sV: self.connect_add(n.view)
            for e in self.sug.g.sE:
                e.view = Edge_basic(e.v[0].view.obj,e.v[1].view.obj)
                self.addItem(e.view)

    def connect_add(self,nv):
        self.addItem(nv.obj)

    def Draw(self,N=1,stepflag=False,constrained=False,opt=False):
        #self.sug.init_all(cons=constrained,optimize=opt)
        if stepflag:
            self.drawer=self.sug.draw_step()
            self.greens=[]
        else:
            self.sug.draw(N)
        #for e in self.sug.alt_e: e.view.set_properties(stroke_color='red')
        for e in self.sug.g.sE:
            #self.parent.root.add_child(e.view)
            # move edge start/end to CX points:
            e.view.update_points()

from math import pow
from PyQt5.QtCore import Qt,QRectF

class GraphView(QGraphicsView):

    def __init__(self,scene):
        super(GraphView,self).__init__(scene)
        self.setRenderHints(QPainter.Antialiasing)
        self.setBackgroundBrush(QBrush(QColor('#dff')))
        #self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        #self.setDragMode(QGraphicsView.ScrollHandDrag)
        #self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        #self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Plus:
            self.scaleView(1.2)
        elif key == Qt.Key_Minus:
            self.scaleView(1 / 1.2)
        else:
            super(GraphView, self).keyPressEvent(event)

    def wheelEvent(self, event):
        self.scaleView(pow(2.0, -event.angleDelta().y() / 240.0))

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)

