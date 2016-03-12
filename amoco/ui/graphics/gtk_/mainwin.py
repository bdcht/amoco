# -*- coding: utf-8 -*-
# Copyright (C) 2008 Axel Tillequin (bdcht3@gmail.com)
# This code is part of Amoco
# published under GPLv2 license

import pygtk
pygtk.require('2.0')
import gtk
import os

#if os.name=='posix':
#    gtk.gdk.threads_init()

class gtkWindow(object):
    def __init__(self):
        self.window = None
        self.canvas = None
        self.events = None
        self.gui    = None

    # called by Masr init :
    def initWindow(self):
        # we provide only the main gtk window here, not the drawing area:
        self.window = gtk.Window()
        self.window.set_title("amoco-gtk")
        # handler of events on the X11 window (close,kill,etc):
        self.window.connect("destroy", gtk.main_quit)
        self.window.connect("delete_event", gtk.main_quit)
        self.window.set_border_width(0)
        #self.window.fullscreen()
        # add a vertical stacking box for menu/canvas/statusbar:
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        self.initCanvas()

    def initCanvas(self):
        from .canvas import Canvas
        # the canvas will be added to a scrollable window:
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(2)
        ## always show h,v scroll bars
        scrolled_window.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
        # create canvas object which holds the layout:
        self.canvas = Canvas(parent=scrolled_window)
        # add it to vpan widget:
        self.vpan = gtk.VPaned()
        self.vbox.add(self.vpan)
        self.vpan.add(scrolled_window)

    def mainLoop(self):
        # create the gtk window and everything in it:
        self.window.show_all()
        self.window.set_focus(self.canvas)
        # let gtk handle the event loop:
        gtk.main()
