#!/usr/bin/python
import itertools, random, pickle
import wx
import wx.lib.intctrl
import wx.lib.wxcairo
import cairo

from pmfm import *

def GetNeighbors(world, w, h, max_w, max_h):
    neighbors = []
    # Left and Right
    if(w - 1) < 0:
        neighbors.append(Dead())
        neighbors.append(world[w + 1][h])
    elif(w + 1) > (max_w - 1):
        neighbors.append(world[w - 1][h])
        neighbors.append(Dead())
    else:
        neighbors.append(world[w - 1][h])
        neighbors.append(world[w + 1][h])
    # Up and Down
    if(h - 1) < 0:
        neighbors.append(world[w][h + 1])
        neighbors.append(Dead())
    elif(h + 1) > (max_h - 1):
        neighbors.append(Dead())
        neighbors.append(world[w][h - 1])
    else:
        neighbors.append(world[w][h + 1])
        neighbors.append(world[w][h - 1])
    return neighbors

def SetNeighbors(world, w, h, neighbors, max_w, max_h):
    # Left and Right
    if(w - 1) < 0:
        world[w + 1][h] = neighbors[1]
    elif(w + 1) > (max_w - 1):
        world[w - 1][h] = neighbors[0]
    else:
        world[w - 1][h] = neighbors[0]
        world[w + 1][h] = neighbors[1]
    # Up and Down
    if(h - 1) < 0:
        world[w][h + 1] = neighbors[2]
    elif(h + 1) > (max_h - 1):
        world[w][h - 1] = neighbors[3]
    else:
        world[w][h + 1] = neighbors[2]
        world[w][h - 1] = neighbors[3]

########################################################################
class ResizeDialog(wx.Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, width, height):
        """Constructor"""
        wx.Dialog.__init__(self, None, title="Resize Dialog")

        w_label =wx.StaticText(self, -1, "Width", style=wx.ALIGN_CENTRE)
        h_label =wx.StaticText(self, -1, "Height", style=wx.ALIGN_CENTRE)
        self.intCtrl_W = wx.lib.intctrl.IntCtrl(self)
        self.intCtrl_W.SetValue(width)
        self.intCtrl_H = wx.lib.intctrl.IntCtrl(self)
        self.intCtrl_H.SetValue(height)
        okBtn = wx.Button(self, wx.ID_OK)

        w_sizer = wx.BoxSizer(wx.HORIZONTAL)
        w_sizer.Add(w_label)
        w_sizer.Add(self.intCtrl_W)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add(h_label)
        h_sizer.Add(self.intCtrl_H)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(w_sizer, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(h_sizer, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(okBtn, 0, wx.ALL|wx.CENTER, 5)
        self.SetSizer(sizer)


########################################################################
class DrawingArea(wx.Panel):

    WIDTH = 30
    HIEGHT = 30
    GAP = 5

    def __init__ (self, *args , **kw):
        super(DrawingArea , self).__init__ (*args , **kw)
        self.w = 0
        self.h = 0
        self.displayField = None
        self.SetDoubleBuffered(True)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def ResizeField(self, width, height):
        self.w = width
        self.h = height
        self.displayField = [[((0.8, 0.8, 0.8), "")]*self.h for i in range(self.w)]

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        cr = wx.lib.wxcairo.ContextFromDC(dc)
        self.DoDrawing(cr)

    def GetWorldCoord(self, e):
        pos = e.GetPosition()
        w = pos[0]//self.WIDTH
        h = pos[1]//self.HIEGHT
        if(h >= self.h) | (w >= self.w):
            raise IndexError
        return (w, h)

    def DoDrawing(self, cr):
        # Draw grid
        cr.set_font_size(15)
        for w, h in itertools.product(range(self.w), range(self.h)):
            (color, text) = self.displayField[w][h]
            cr.set_source_rgb(*color)
            cr.rectangle(w*DrawingArea.WIDTH , h*DrawingArea.HIEGHT,
                         DrawingArea.WIDTH - DrawingArea.GAP,
                         DrawingArea.HIEGHT - DrawingArea.GAP)
            cr.fill()
            cr.move_to(w*DrawingArea.WIDTH + 8, h*DrawingArea.HIEGHT + 17)
            cr.set_source_rgb(1, 1, 1)
            cr.show_text(text)

    def UpdateDisplayField(self, world):
        for w, h in itertools.product(range(self.w), range(self.h)):
            sq = world[w][h]
            if isinstance(sq, Dead):
                color = (0.1 , 0.1 , 0.1)
                text = ""
            elif isinstance(sq, Medium):
                color = (0.2 , 0.2 , 0.8)
                text = str(sq.dist)
            elif isinstance(sq, Barrier):
                color = (0.8 , 0.1 , 0.1)
                text = ""
            else:
                color = (0.8 , 0.8 , 0.8)
                text = ""
            self.displayField[w][h] = (color, text)

########################################################################
class Frame(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Frame, self).__init__(*args, **kwargs)
        self.canvas = None
        self.elem_sel = None
        self.w = 5
        self.h = 5
        self.ResetWorld()
        self.InitUI()

    def ResetWorld(self):
        self.world = [[Empty()]*self.h for i in range(self.w)]

    def InitUI(self):
        #----------------------------------------------------
        # Build menu bar and submenus

        menubar = wx.MenuBar()
        # file menu containing quit menu item
        fileMenu = wx.Menu()
        # Quit Item
        quit_item = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit\tCtrl+W')
        fileMenu.AppendItem(quit_item)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        #Resize Item
        resize_item = wx.MenuItem(fileMenu, wx.ID_DEFAULT, '&Resize\tCtrl+R')
        fileMenu.AppendItem(resize_item)
        self.Bind(wx.EVT_MENU, self.OnResize, resize_item)
        # Save Item
        save_item = wx.MenuItem(fileMenu, wx.ID_SAVE, '&Save\tCtrl+S')
        fileMenu.AppendItem(save_item)
        self.Bind(wx.EVT_MENU, self.SaveFile, save_item)
        # Open Item
        open_item = wx.MenuItem(fileMenu, wx.ID_OPEN, '&Open\tCtrl+O')
        fileMenu.AppendItem(open_item)
        self.Bind(wx.EVT_MENU, self.OpenFile, open_item)

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
        self.canvas.ResizeField(self.w, self.h)
        self.canvas.UpdateDisplayField(self.world)
        self.canvas.Bind(wx.EVT_LEFT_UP, self.OnCanvasLClick)
        self.canvas.Bind(wx.EVT_RIGHT_UP, self.OnCanvasRClick)
        vbox.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 2)

        smallPan = wx.Panel(panel)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(smallPan, 0, wx.EXPAND|wx.ALL, 12)
        smallPan.SetSizer(hbox2)

        #----------------------------------------------------
        # Place buttons in correct box corresponding with panel

        clear_button = wx.Button(smallPan, wx.ID_CLEAR)
        self.Bind(wx.EVT_BUTTON, self.OnClear, clear_button)
        hbox2.Add(clear_button)

        step_button = wx.Button(smallPan, wx.ID_FORWARD)
        self.Bind(wx.EVT_BUTTON, self.OnStep, step_button)
        hbox2.Add(step_button)

        go_button = wx.Button(smallPan, wx.ID_EXECUTE)
        self.Bind(wx.EVT_BUTTON, self.OnGo, go_button)
        hbox2.Add(go_button)

        self.elem_sel = wx.RadioBox(smallPan, choices=("Barrier","Medium", "Dead"))
        hbox2.Add(self.elem_sel)

        #----------------------------------------------------
        # Set window properties

        #~ self.SetSize((1600, 1200))
        self.SetSize((600, 500))
        #~ self.Maximize()
        self.SetTitle('PROGRAM NAME')
        self.Centre()

        # Open Default World
        try:
            with open("./res/default.p", "rb") as handle:
                self.w, self.h, self.world = pickle.load(handle)
                self.canvas.ResizeField(self.w, self.h)
                self.canvas.UpdateDisplayField(self.world)
                self.Refresh()
        except (OSError, IOError):
            pass

    def OnQuit(self, e):
        self.Close()

    def OnResize(self, e):
        dlg = ResizeDialog(self.w, self.h)
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            self.w = dlg.intCtrl_W.GetValue()
            self.h = dlg.intCtrl_H.GetValue()
            self.ResetWorld()
            self.canvas.ResizeField(self.w, self.h)
            self.canvas.UpdateDisplayField(self.world)
            self.Refresh()
        dlg.Destroy()

    #----------------------------------------------------------------------
    def OpenFile(self, event):
        openFileDialog = wx.FileDialog(self, "Open", "", "",
                                       "Pickled files (*.p)|*.p",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        res = openFileDialog.ShowModal()
        if res == wx.ID_OK:
            path = openFileDialog.GetPath()
            with open(path, "rb") as handle:
                self.w, self.h, self.world = pickle.load(handle)
                self.canvas.ResizeField(self.w, self.h)
                self.canvas.UpdateDisplayField(self.world)
                self.Refresh()
        openFileDialog.Destroy()

    #----------------------------------------------------------------------
    def SaveFile(self, event):
        saveFileDialog = wx.FileDialog(self, "Save As", "", "",
                                       "Pickled files (*.p)|*.p",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        res = saveFileDialog.ShowModal()
        if res == wx.ID_OK:
            path = saveFileDialog.GetPath()
            with open(path, "wb") as handle:
                pickle.dump([self.w, self.h, self.world], handle)
        saveFileDialog.Destroy()

    def OnClear(self, e):
        self.ResetWorld()
        self.canvas.UpdateDisplayField(self.world)
        self.Refresh()

    def OnStep(self, e):
        # Step
        for w, h in itertools.product(range(self.w), range(self.h)):
            neighbors = GetNeighbors(self.world, w, h, self.w, self.h)
            if(self.world[w][h].ProcAtomicDir(neighbors)):
                SetNeighbors(self.world, w, h, neighbors, self.w, self.h)

        # Update display
        self.canvas.UpdateDisplayField(self.world)
        self.Refresh()

    def OnGo(self, e):
        for x in range(100):
            self.OnStep(e)

    def OnCanvasRClick(self, e):
        try:
            w, h = self.canvas.GetWorldCoord(e)
        except IndexError:
            return None

        self.world[w][h] = Empty()
        # Update display
        self.canvas.UpdateDisplayField(self.world)
        self.Refresh()

    def OnCanvasLClick(self, e):
        try:
            w, h = self.canvas.GetWorldCoord(e)
        except IndexError:
            return None

        if self.elem_sel.GetStringSelection() == "Barrier":
            elem = Barrier()
        elif self.elem_sel.GetStringSelection() == "Medium":
            elem = Medium()
        elif self.elem_sel.GetStringSelection() == "Dead":
            elem = Dead()
        else:
            elem = Empty()
        self.world[w][h] = elem
        # Update display
        self.canvas.UpdateDisplayField(self.world)
        self.Refresh()

def main():
    ex = wx.App()
    f = Frame(None)
    f.Show(True)
    ex.MainLoop()

if __name__ == '__main__':
    main()
