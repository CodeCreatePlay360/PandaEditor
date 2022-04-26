import wx
from wx.lib.scrolledpanel import ScrolledPanel


class AuxiliaryPanel(ScrolledPanel):
    def __init__(self, parent, *args, **kwargs):
        ScrolledPanel.__init__(self, parent, *args, **kwargs)

        self.bg_colour = kwargs.pop("BG_colour", wx.Colour(127, 127, 127, 255))
        self.win_style_flag = kwargs.pop("WinStyleFlag", wx.BORDER_SUNKEN)

        self.SetBackgroundColour(self.bg_colour)
        self.SetWindowStyleFlag(self.win_style_flag)
