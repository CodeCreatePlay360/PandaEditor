import wx
from wx.lib.scrolledpanel import ScrolledPanel
from constants import *


class WxPanel(wx.Panel):
    def __init__(self, parent, label, style, color):
        wx.Panel.__init__(self, parent)
        self.SetWindowStyleFlag(style)
        self.SetBackgroundColour(color)
        self.label = label
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.base_panel = None
        self.buttons_panel = None

        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_evt_resize)

    def create_layout(self):
        self.buttons_panel = wx.Panel(self)
        self.buttons_panel.SetMinSize((self.GetClientSize().x, 24))
        self.buttons_panel.SetBackgroundColour(DARK_GREY)
        self.buttons_panel.SetWindowStyle(wx.BORDER_SIMPLE)
        self.label = wx.StaticText(self.buttons_panel, label=self.label)
        self.label.SetPosition((2, 4))

        # create base panel & setup it's sizer
        self.base_panel = wx.Panel(self)
        self.base_panel.SetBackgroundColour(GREY)
        self.base_panel.SetWindowStyle(wx.BORDER_SIMPLE)
        self.base_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.base_panel.SetSizer(self.base_panel_sizer)

        self.sizer.Add(self.buttons_panel, 0, wx.EXPAND)
        self.sizer.Add(self.base_panel, 1, wx.EXPAND)

        self.sizer.Layout()
        self.Layout()
        self.Refresh()

    def on_evt_resize(self, evt):
        if self.buttons_panel is not None:
            self.buttons_panel.SetMinSize((self.GetClientSize().x, 24))
        self.Refresh()
        evt.Skip()


class WxScrolledPanel(ScrolledPanel):
    def __init__(self, parent, label, style, color):
        ScrolledPanel.__init__(self, parent)
        self.SetWindowStyleFlag(style)
        self.SetBackgroundColour(color)

        self.buttons = []
        self.label = label
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.base_panel = None
        self.base_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.buttons_panel = None
        self.btn_sizer = None

        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE, self.on_evt_resize)

    def create_layout(self):
        self.buttons_panel = wx.Panel(self)
        self.buttons_panel.SetMinSize((self.GetClientSize().x, 24))
        self.buttons_panel.SetBackgroundColour(DARK_GREY)
        self.buttons_panel.SetWindowStyle(wx.BORDER_SIMPLE)
        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons_panel.SetSizer(self.btn_sizer)

        # self.label = wx.StaticText(self.buttons_panel, label=self.label)
        # self.label.SetPosition((2, 4))

        # create base panel & setup it's sizer
        self.base_panel = wx.Panel(self)
        self.base_panel.SetBackgroundColour(GREY)
        self.base_panel.SetWindowStyle(wx.BORDER_SIMPLE)
        self.base_panel.SetSizer(self.base_panel_sizer)

        self.sizer.Add(self.buttons_panel, 0, wx.EXPAND)
        self.sizer.Add(self.base_panel, 1, wx.EXPAND)

        self.SetupScrolling()
        self.sizer.Layout()
        self.Layout()
        self.Refresh()

    def create_buttons(self):
        pass

    def on_evt_menu(self, evt):
        evt.Skip()

    def on_evt_resize(self, evt):
        self.Refresh()
        evt.Skip()
