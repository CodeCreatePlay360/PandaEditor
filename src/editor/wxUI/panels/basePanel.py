import wx
from editor.constants import obs


class BasePanel(wx.Panel):
    def __init__(self, parent, panel_label, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.label = panel_label

    def on_enter(self, evt):
        evt.Skip()

    def on_leave(self, evt):
        evt.Skip()

    def on_mouse1_down(self, evt):
        evt.Skip()

    def on_mouse1_up(self, evt):
        evt.Skip()

    def on_resize_event(self, evt):
        evt.Skip()

    def on_hover(self, evt):
        evt.Skip()
