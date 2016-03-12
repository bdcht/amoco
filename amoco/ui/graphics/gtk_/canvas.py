#  -*- coding: utf-8 -*-
#  Copyright (C) 2008 Axel Tillequin (bdcht3@gmail.com) 
# This code is part of Masr
# published under GPLv2 license

from  goocanvas import Canvas as GooCanvas
from  goocanvas import polyline_new_line,Grid,LineDash
from  goocanvas import ITEM_VISIBLE,ITEM_INVISIBLE
import gtk

#------------------------------------------------------------------------------
#  just a wrapper above GooCanvas class, with texture dict added.
#  we just wrap it so that introspection/debug is easy...
class  Canvas(GooCanvas):
    textures = {}

    def __init__(self,**args):
        GooCanvas.__init__(self,**args)
        # infinite world should replace scroll_region
        self.set_properties(automatic_bounds=True,
                            integer_layout=False,
                            bounds_from_origin=False,
                            bounds_padding=100)

        self.root = self.get_root_item()
        self.root.set_properties(fill_color='white')

        polyline_new_line(self.root,-5,0,5,0,stroke_color='red')
        polyline_new_line(self.root,0,-5,0,5,stroke_color='red')

        self.zoom = False

        # GooCanvas will transmit all keyboard events to
        # its parent unless one of its item has focus.
        self.parent.connect_object("key_press_event",
                                   Canvas.eventhandler,self)
        self.parent.connect_object("key_release_event",
                                   Canvas.eventhandler,self)
        self.connect("event",Canvas.eventhandler)

    def eventhandler(self,e):
        if e.type == gtk.gdk.KEY_PRESS:
            kvn = gtk.gdk.keyval_name(e.keyval)
            if kvn == 'a':
                self.scroll_to(0,0)
            if kvn == 'Control_L':
                if not self.zoom:
                    self.zoom = True
            elif kvn == 'plus' and self.zoom:
                self.props.scale *= 1.2
            elif kvn == 'minus' and self.zoom:
                self.props.scale *= 0.8
            return False
        elif e.type == gtk.gdk.KEY_RELEASE:
            if gtk.gdk.keyval_name(e.keyval) == 'Control_L':
                self.zoom = False
                return True
        elif e.type == gtk.gdk.SCROLL and self.zoom:
            if e.direction == gtk.gdk.SCROLL_UP:
                self.props.scale *= 1.2
            elif e.direction == gtk.gdk.SCROLL_DOWN:
                self.props.scale *= 0.8
            return True
        elif e.type == gtk.gdk.BUTTON_PRESS:
            print "click:(%d,%d)"%e.get_coords()
        return False

