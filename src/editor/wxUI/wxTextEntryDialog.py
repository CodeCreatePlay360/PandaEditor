import wx

ID_BUTTON_OK = wx.NewId()
ID_BUTTON_CANCEL = wx.NewId()


class TextEntryDialog(wx.Frame):
    def __init__(self, parent, title, start_text):
        wx.Frame.__init__(self, parent)
        self.parent = parent

        self.title = title
        self.start_text = start_text

        self.SetTitle(title)
        self.SetMaxSize((350, 130))

    def init_dialog(self):
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(4, 4)

        self.static_text = wx.StaticText(panel, label=self.title)
        sizer.Add(self.static_text,
                  pos=(0, 0),
                  flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        self.text_ctrl = wx.TextCtrl(panel, value=self.start_text)
        sizer.Add(self.text_ctrl,
                  pos=(1, 0),
                  span=(0, 5),
                  flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        buttonOk = wx.Button(panel, label="Ok", size=(90, 28), id=ID_BUTTON_OK)
        buttonClose = wx.Button(panel, label="Close", size=(90, 28), id=ID_BUTTON_CANCEL)

        # bind events
        self.Bind(wx.EVT_BUTTON, self.on_button_ok, id=ID_BUTTON_OK)
        self.Bind(wx.EVT_BUTTON, self.on_button_cancel, id=ID_BUTTON_CANCEL)

        sizer.Add(buttonOk, pos=(2, 3))
        sizer.Add(buttonClose, pos=(2, 4), flag=wx.RIGHT | wx.BOTTOM, border=10)

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(2)
        panel.SetSizer(sizer)

        self.Center()
        self.Show(True)

    def on_button_ok(self, e):
        text = self.text_ctrl.GetLineText(0)
        self.parent.on_file_operation(self.title, text)
        e.Skip()
        self.Close()

    def on_button_cancel(self, e):
        e.Skip()
        self.Close()
