# -*- coding: utf-8 -*-

# Copyright (C) 2010 Axel Tillequin (bdcht3@gmail.com)
# This code is part of Amoco
# published under GPLv2 license

import gtk

from grandalf.routing import *

from .items import *

#------------------------------------------------------------------------------
class GraphScene(object):

  def __init__(self,c,sug):
    self.parent = c
    self.sug = sug
    self.sug.route_edge = route_with_lines
    self.sug.dx,self.sug.dy = 5,5
    self.sug.dirvh=0
    c.parent.connect_object("button-press-event",GraphScene.eventhandler,self)
    c.parent.connect_object("button-release-event",GraphScene.eventhandler,self)
    c.parent.connect_object("key-press-event",GraphScene.eventhandler,self)
    c.parent.connect_object("key-release-event",GraphScene.eventhandler,self)
    for n in self.sug.g.sV: self.connect_add(n.view)
    for e in self.sug.g.sE:
        e.view = Edge_basic(e.v[0].view.obj,e.v[1].view.obj,head=True)

  def Draw(self,N=1,stepflag=False,constrained=False,opt=False):
    #self.sug.init_all(cons=constrained,optimize=opt)
    if stepflag:
        self.drawer=self.sug.draw_step()
        self.greens=[]
    else:
        self.sug.draw(N)
    for e in self.sug.alt_e: e.view.set_properties(stroke_color='red')
    for e in self.sug.g.sE:
        self.parent.root.add_child(e.view)
        # move edge start/end to CX points:
        e.view.update_points()

  def connect_add(self,item):
    self.parent.root.add_child(item.obj)

  def disconnect(self):
    self.parent.parent.disconnect_by_func(GraphScene.eventhandler)


  def clean(self):
    r = self.parent.root
    for v in self.sug.g.sV:
      r.remove_child(v.view.obj)
    for e in self.sug.g.sE:
      for cx in e.view.cx:
        cx.unregister(e.view)
      r.remove_child(e.view)

  # Scene-Wide (default) event handler on items events:
  def eventhandler(self,e):
    if e.type == gtk.gdk.KEY_PRESS:
      if e.keyval == ord('p'):
        for l in self.sug.layers:
          for v in l:
            v.view.xy = (self.sug.grx[v].x[self.sug.dirvh],v.view.xy[1])
        self.sug.draw_edges()
        self.sug.dirvh = (self.sug.dirvh+1)%4
      if e.keyval == ord('W'):
          self.sug.xspace += 1
          self.sug.setxy()
          self.sug.draw_edges()
      if e.keyval == ord('w'):
          self.sug.xspace -= 1
          self.sug.setxy()
          self.sug.draw_edges()
      if e.keyval == ord('H'):
          self.sug.yspace += 1
          self.sug.setxy()
          self.sug.draw_edges()
      if e.keyval == ord('h'):
          self.sug.yspace -= 1
          self.sug.setxy()
          self.sug.draw_edges()
      if e.keyval == ord(' '):
        try:
          l,mvmt = next(self.drawer)
          for x in self.greens:
              x.view.shadbox.set_properties(fill_color='grey44')
          self.greens=[]
          for x in l:
              if hasattr(x.view,'_obj'):
                  x.view._obj.shadbox.set_properties(fill_color='green')
                  if x in mvmt: x.view._obj.shadbox.set_properties(fill_color='orange')
                  self.greens.append(x)
        except StopIteration:
            print 'drawer terminated'
            del self.drawer
            del self.greens
        except AttributeError:
            print 'drawer created'
            self.drawer=self.sug.draw_step()
            self.greens=[]

