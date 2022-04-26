import wx
import editor.p3d


class Viewport(p3d.wxPanda.Viewport):
    def __init__(self, *args, **kwargs):
        p3d.wxPanda.Viewport.__init__(self, *args, **kwargs)
        self.app = wx.GetApp()
        
    def Initialize(self, useMainWin=True):
        super(PModBase, self).Initialize(useMainWin)

