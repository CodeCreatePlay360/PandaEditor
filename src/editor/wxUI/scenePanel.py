import wx
from wx.lib.scrolledpanel import ScrolledPanel
from editor.wx.fileBrowser import FileBrowser
from editor.wx.propertiesPanel import PropertiesPanel


class ScenePanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.wxMain = parent

        self.properties_panel = PropertiesPanel(self)

        self.file_browser_panel = ScrolledPanel(self)
        self.file_browser = FileBrowser(self.file_browser_panel, self.wxMain)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.file_browser, 1, wx.EXPAND)
        self.file_browser_panel.SetSizer(sizer)

        self.file_browser_panel.Layout()
        self.file_browser_panel.SetupScrolling()

        # self.Bind(wx.EVT_MOTION, self.on_evt_resize)
        # self.Bind(wx.EVT_ENTER_WINDOW, self.on_evt_resize)
        self.Bind(wx.EVT_SIZE, self.on_evt_size)

    def on_evt_size(self, e):
        size = self.GetSize()
        self.properties_panel.SetPosition((0, 0))
        self.properties_panel.SetSize((size.x, size.y/2))
        # self.properties_panel.Refresh()

        self.file_browser_panel.SetPosition((0, (size.y - size.y/2)))
        self.file_browser_panel.SetSize((size.x, size.y/2))

        e.Skip()
