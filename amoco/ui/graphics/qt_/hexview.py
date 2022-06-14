# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from itertools import cycle

from PySide6.QtCore import Qt, QRect, Signal, QPointF, QRectF, QSizeF
from PySide6.QtGui import QFont, QColor, QPen, QPainter, QPolygon
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QAbstractScrollArea

from . import brushes
from . import colors
from . import models

class HexView(QAbstractScrollArea):
    """
    HexView is a QAbstractScrollArea (not a QScrollArea in order to
    handle large list of hexlines to display. A QScrollArea would require
    that the viewport Widget associated to it be fully defined to handle
    the scrolling automatically. Here we really want to render the viewport
    dynamically based on scrolling events, not the opposite.)
    """
    clicked = Signal((int,int,QColor))

    def __init__(self, parent=None, dataio=None):
        super().__init__(parent)
        # enforce monospaced font:
        f = QFont("Monospace")
        f.setPointSize(8)
        self.setFont(f)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.palette = cycle(colors.palette_trbg.values())
        self.lastcolor = None
        # set default vertical scrolling steps:
        self.vb = self.verticalScrollBar()
        # addresses to be highlighted:
        self.highlight = {}
        self.selected = None
        # setup internal widgets:
        self.model = None
        self.statusbar = parent.statusBar() if parent else None
        if dataio:
            self.setData(dataio)

    @property
    def select_color(self):
        """
        get next color from (cycle) palette
        """
        self.lastcolor = next(self.palette)
        return self.lastcolor

    def setData(self,dataio):
        """
        Define the data model associated with the HexView and initialise
        the vertical bar values.
        """
        if self.model:
            self.model.deleteLater()
        # data should have DataIO API
        # the model is used as the interface with the data bytes
        self.model = models.DataIOModel(parent=self,data=dataio)
        # the view needs updating whenever the model emits a
        # "UPDATED" signal:
        self.model.UPDATED.connect(self.update)
        # since we are an "abstract" widget we need to compute the
        # vertical bar minimum/maximum values.
        self.vb.setMinimum(0)
        nb, r = divmod(self.model.data.size(), self.model.linesize)
        if r>0: nb += 1
        self.vb.setMaximum(nb)
        # set line definition (sizes):
        self.line = HexLine(self.fontMetrics(),self.model.linesize)
        # prepare grayscale image of the full model data:
        self.qimg = QImage(self.model.full,self.model.linesize,nb,
                           QImage.Format_Grayscale8)
        self.update()

    def update(self):
        "trigger an update of the viewport widget (ie a paintEvent)"
        # this will trigger update (paint) on the children as well:
        self.viewport().update()

    def paintEvent(self,e):
        "(re)draw everything inside the rectangle associated with event e"
        if self.model is not None:
            # get the painting area:
            w = QPainter(self.viewport())
            f = self.font()
            w.setFont(f)
            # get rectangle that needs paint:
            r = e.rect()
            # get line indices for this rectangle:
            line0 = self.vb.value()
            h = self.line.height
            first = line0 + r.top()//h
            last  = line0 + r.bottom()//h
            count = last-first
            # update drawing:
            self.paintlines(w,first,count,line0)
            self.paintframes(w)
            self.paintmap(w)

    def keyPressEvent(self,e):
        self.statusbar.showMessage("key: %d ('%s') [%08x]"%(e.key(),
                                                            e.text(),
                                                            e.modifiers()))
        if self.model is not None:
            if e.key()==int(Qt.Key_Escape):
                self.highlight = {}
            self.update()
        super().keyPressEvent(e)

    def addrToLine(self,addr):
        N = self.model.linesize
        l,off = divmod(addr,N)
        return l

    def xyToAddr(self,x,y):
        if x<self.line.x_map:
            h = self.line.height
            l = y//h
            # get base address
            a = self.model.linesize*(self.model.cur+l)
            # add byte index [0,16[
            return (a + self.line.index(x))
        h = self.viewport().height()
        a = int((y/h)*(self.qimg.height()*self.qimg.width()))
        a = (a//self.model.linesize)*self.model.linesize
        if a!=0 and self.selected and a!=(self.selected[0]):
            return a-1
        else:
            return a

    def colorize(self,a,nb,color):
        N = self.model.linesize
        base,o = divmod(a,N)
        a = base*N
        c = color
        while nb>0:
            n = min(N-o,nb)
            if a not in self.highlight:
                self.highlight[a] = [None]*N
            for i in range(o,o+n):
                self.highlight[a][i] = c
            nb -= n
            a += N
            o = 0

    def adjust_selected(self,e):
        x,y = e.x(), e.y()
        a = self.xyToAddr(e.x(),e.y())
        if self.selected:
            aa,nb_,c = self.selected
            if a!=aa:
                a,nb = (aa,a-aa) if aa<a else (a,aa-a)
                self.selected = (a,nb+1,c)
            else:
                nb = 1
            self.colorize(a,nb_,None)
        else:
            if x<self.line.x_end:
                nb = 1
            elif x<self.line.x_map:
                nb = self.model.linesize
                a = a-(nb-1)
            else:
                nb = self.model.linesize
            self.selected = (a,nb,self.select_color)
        msg = "selection: [addr=%08x, size=%d]"%(a,nb)
        self.statusbar.showMessage(msg)

    def mousePressEvent(self,e):
        self.adjust_selected(e)
        self.colorize(*self.selected)
        self.update()

    def mouseMoveEvent(self,e):
        if self.selected:
            self.adjust_selected(e)
            self.colorize(*self.selected)
            self.update()

    def mouseReleaseEvent(self,e):
        if self.selected:
            self.adjust_selected(e)
            self.colorize(*self.selected)
            self.update()
            self.clicked.emit(*self.selected)
            self.selected = None

    def wheelEvent(self,e):
        delta = 1 if e.angleDelta().y()<0 else -1
        v = self.vb.value() + delta
        self.vb.setValue(v)
        msg = "wheel: delta=%d, v=%d"%(delta,v)
        self.statusbar.showMessage(msg)
        self.update()

    def paintlines(self,surface,first,count,l0):
        "draws the data out of the model onto the qpainter surface"
        self.model.cur = first
        N = self.model.linesize
        h = self.line.height
        ww = surface.window().width()
        y = (first-l0)*h
        c0,c1 = brushes.xv_bg, brushes.xv_bg_alt
        pen = surface.pen()
        for address,data,txt in self.model.iterlines(count):
            # background rect (alternate)
            r = QRect(0,y,ww,h)
            surface.fillRect(r,c0)
            # address column:
            r.setWidth(self.line.x_hex)
            surface.drawText(r,
                             Qt.AlignHCenter | Qt.AlignVCenter,
                             "%08x"%address)
            # hex column:
            w = self.line.xb.width
            r.setWidth(w)
            r.translate(self.line.x_hex+self.line.pxpad,0)
            C = self.highlight.get(address,[None]*N)
            for i,c in enumerate(C):
                try:
                    s = "%02x"%(data[i])
                except IndexError:
                    break
                flg = Qt.AlignHCenter | Qt.AlignVCenter
                if c:
                    surface.fillRect(r,c)
                    surface.setPen(QPen(Qt.white))
                surface.drawText(r, flg, s)
                surface.setPen(pen)
                r.translate(w,0)
            # ascii column:
            w = self.line.xb.cw
            r.setX(self.line.x_txt+self.line.pxpad)
            r.setWidth(w)
            for i,c in enumerate(C):
                try:
                    s = txt[i]
                except IndexError:
                    break
                flg = Qt.AlignHCenter | Qt.AlignVCenter
                if c:
                    surface.fillRect(r,c)
                    surface.setPen(QPen(Qt.white))
                surface.drawText(r,flg,s)
                surface.setPen(pen)
                r.translate(w,0)
            # clear background endline:
            r.setX(self.line.x_end)
            r.setWidth(ww-self.line.x_end)
            surface.fillRect(r,brushes.xv_bg_alt)
            y += h
            c0,c1 = c1,c0

    def paintframes(self,surface):
        r = surface.window()
        ww = surface.window().width()
        # top & bottom lines:
        surface.drawLine(0,r.top(),
                         ww,r.top())
        surface.drawLine(0,r.bottom(),
                         ww,r.bottom())
        # vertical column lines:
        x = self.line.x_hex
        surface.drawLine(x,r.top(),
                         x,r.bottom())
        x = self.line.x_txt
        surface.drawLine(x,r.top(),
                         x,r.bottom())
        x = self.line.x_end
        surface.drawLine(x,r.top(),
                        x,r.bottom())

    def paintmap(self,surface):
        ww = surface.window().width()
        wh = surface.window().height()
        self.vb.setMaximum(self.qimg.height()-(wh//self.line.height))
        self.line.x_map = ww-32
        r = QRect(self.line.x_map,2,32,wh-4)
        surface.drawImage(r,self.qimg)
        factor = wh/self.qimg.height()
        pen = surface.pen()
        p = QPen(Qt.white)
        p.setCapStyle(Qt.RoundCap)
        p.setWidth(2)
        surface.setPen(p)
        l0 = self.vb.value()*factor
        l1 = l0+(wh//self.line.height)*factor
        pad = 4
        p1 = QPointF(self.line.x_map-pad,l0)
        p2 = QPointF(self.line.x_map-pad,l1)
        if l1-l0>4:
            p.setWidth(2)
            surface.drawLine(p1,p2)
            surface.drawLine(p1,QPointF(self.line.x_map,l0))
            surface.drawLine(p2,QPointF(self.line.x_map,l1))
        else:
            p.setWidth(4)
            surface.drawLine(p1,p2)
        surface.setPen(pen)

    def move(self,cur,e):
        return None

    def action(self,cur,e):
        return None

#--------------------------------------------------------------------------------------------------

class HexLine(object):
    pxpad = 4
    def __init__(self,fm,lz):
        cw =  fm.maxWidth()
        self.xb = HexByte(fm)
        self.lz = lz
        self.x_hex = self.pxpad+(8*cw)+self.pxpad
        self.x_txt = self.x_hex + self.pxpad + (lz*self.xb.width) + self.pxpad
        self.x_end = self.x_txt + cw*lz + self.pxpad

    @property
    def height(self):
        "returns the line height for the current font"
        return self.xb.fm.height()

    def index(self,x):
        x0 = x-(self.x_hex+self.pxpad)
        # trick for getting the line offset:
        if x0<0: return 0
        i = x0//self.xb.width
        if i<self.lz: return i
        x0 = x-(self.x_txt+self.pxpad)
        if x0<0: return 0
        i = x0//self.xb.cw
        if i<self.lz: return i
        return self.lz-1

#--------------------------------------------------------------------------------------------------

class HexByte(object):
    def __init__(self,fm):
        self.fm = fm
        self.cw = fm.maxWidth()
        r = fm.boundingRect("00")
        self.rect = r.adjusted(-2,-2,2,2)

    @property
    def height(self):
        "returns the line height for the current font"
        return self.fm.height()

    @property
    def width(self):
        "returns the width of a hexadecimal byte"
        return self.rect.width()


