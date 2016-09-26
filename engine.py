#!/usr/bin/python
import itertools, random
import wx
import wx.lib.wxcairo
import cairo

from pmfm import *

GRID_H = 5
GRID_W = 5

class DrawingArea(wx.Panel):

    def __init__ (self , *args , **kw):
        super(DrawingArea , self).__init__ (*args , **kw)
        self.field = [[Empty.__name__ for x in range(GRID_W)] for y in
                      range(GRID_H)]

        self.SetDoubleBuffered(True)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, e):

        dc = wx.PaintDC(self)
        cr = wx.lib.wxcairo.ContextFromDC(dc)
        self.DoDrawing(cr)

    def DoDrawing(self, cr):
        # Draw grid
        for h, w in itertools.product(range(GRID_H), range(GRID_W)):
            sq = self.field[w][h]
            if sq == Dead.__name__:
                cr.set_source_rgb (0.1 , 0.1 , 0.1)
            elif sq == Medium.__name__:
                cr.set_source_rgb (0.2 , 0.23 , 0.9)
            else:
                cr.set_source_rgb (0.8 , 0.8 , 0.8)
            cr.rectangle(h*30 , w*30, 25, 25)
            cr.fill()

class Frame(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Frame, self).__init__(*args, **kwargs)
        self.canvas = None

        self.InitUI()

    def InitUI(self):
        #----------------------------------------------------
        # Build menu bar and submenus

        menubar = wx.MenuBar()
        # file menu containing quit menu item
        fileMenu = wx.Menu()
        quit_item = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit\tCtrl+W')
        fileMenu.AppendItem(quit_item)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        menubar.Append(fileMenu, '&File')

        # help menu containing about menu item
        helpMenu = wx.Menu()
        about_item = wx.MenuItem(helpMenu, wx.ID_ABOUT, '&About\tCtrl+A')
        helpMenu.AppendItem(about_item)
        #~ self.Bind(wx.EVT_MENU, self.OnAboutBox, about_item)
        menubar.Append(helpMenu, '&Help')

        self.SetMenuBar(menubar)

        #----------------------------------------------------
        # Build window layout

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(vbox)

        self.canvas = DrawingArea(panel)
        vbox.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 2)


        smallPan = wx.Panel(panel)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(smallPan, 0, wx.EXPAND|wx.ALL, 12)
        smallPan.SetSizer(hbox2)

        #----------------------------------------------------
        # Place buttons in correct box corresponding with panel

        close_button = wx.Button(smallPan, wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self.OnQuit, close_button)

        hbox2.Add(close_button)

        refresh_button = wx.Button(smallPan, wx.ID_REFRESH)
        self.Bind(wx.EVT_BUTTON, self.OnRefresh, refresh_button)

        hbox2.Add(refresh_button)

        #----------------------------------------------------
        # Set window properties

        #~ self.SetSize((1600, 1200))
        self.SetSize((400, 350))
        #~ self.Maximize()
        self.SetTitle('PROGRAM NAME')
        self.Centre()

    def OnQuit(self, e):
        self.Close()

    def OnRefresh(self, e):
        # Add random dead cell
        self.canvas.field[random.randint(0, GRID_W - 1)][random.randint(0, GRID_H - 1)] = Dead.__name__
        self.Refresh()

def main():
    ex = wx.App()
    f = Frame(None)
    f.Show(True)
    ex.MainLoop()

if __name__ == '__main__':
    main()
