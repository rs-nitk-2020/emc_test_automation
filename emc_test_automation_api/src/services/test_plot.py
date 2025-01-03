#!/bin/python
""" A minimal demo of the asc_viewer package. There is a menu bar for loading schematics,
and a status bar for showing net names.

Having the user load symbol paths each time is obviously bad design, and in a real project
you would pass symbol paths to AscCanvas's constructor.
"""

import wx
from asc_viewer import AscCanvas


class AscViewer(wx.Frame):
    def __init__(self):
        super().__init__(None, title="LTspice ASC Viewer", size=(400, 300))

        # Menu Bar
        self.menu = wx.MenuBar()
        menu = wx.Menu()
        entry = menu.Append(wx.ID_ANY, "Open ASY directory...", "Open ASY directory")
        self.Bind(wx.EVT_MENU, self.open_asy, entry)
        entry = menu.Append(wx.ID_ANY, "Open ASC...", "Open ASC file")
        self.Bind(wx.EVT_MENU, self.open_asc, entry)
        self.menu.Append(menu, "&File")
        self.SetMenuBar(self.menu)

        # Status Bar
        self.statusbar = self.CreateStatusBar(1, wx.STB_DEFAULT_STYLE)

        # Canvas for ASC Schematics
        self.asc_canvas = AscCanvas(self)
        self.asc_canvas.Bind(wx.EVT_MOTION, self.on_motion)
        self.Layout()

    def open_asy(self, event):
        path = wx.DirSelector("Choose a symbol folder")
        if not path.strip():
            return
        self.asc_canvas.load_symbols([path])

    def open_asc(self, event):
        d = wx.FileDialog(
            None, "Select schematic", wildcard="Schematic files (.asc)|*.asc"
        )
        if d.ShowModal() == wx.ID_CANCEL:
            return

        filename = d.GetPath()
        if filename[-3:] != "asc":
            wx.MessageDialog(
                None, "Invalid schematic", "Error", wx.OK | wx.ICON_QUESTION
            ).ShowModal()
            return

        self.asc_canvas.load_asc(filename)

    def on_motion(self, event):
        net = self.asc_canvas.get_net_under_mouse(event)
        status_text = net.name if net else ""
        self.statusbar.SetStatusText(status_text)
        event.Skip()


app = wx.App()
frame = AscViewer()
frame.Show()
app.MainLoop()