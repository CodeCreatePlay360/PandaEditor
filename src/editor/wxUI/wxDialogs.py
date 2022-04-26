import wx


class DialogManager:
    """"Manages creation and destruction of dialogues"""

    def __init__(self):
        self.dialogues = {"YesNoDialog": WxYesNoDialog,
                          "TextEntryDialog": WxTextEntryDialog,
                          "ProjectDialog": ProjectDialog
                          }

        # list of all active dialogues
        self.active_dialogues = []

    def create_dialog(self, dialog_type: str, *args, **kwargs):
        if len(self.active_dialogues) > 0:
            print("DialogManager --> Another dialog is already opened.")

        elif dialog_type in self.dialogues.keys():
            dialog = self.dialogues[dialog_type]
            dialog = dialog(*args, **kwargs)

            dialog.create()
            dialog.Center()
            dialog.Show()

            self.active_dialogues.append(dialog_type)

            return dialog

        else:
            print("DialogManager --> dialogue type: {0} not found".format(dialog_type))


class WxCustomDialog(wx.Frame):
    def __init__(self, _title, dialog_manager, _close_method=None, *args, **kwargs):
        super(WxCustomDialog, self).__init__(parent=None, title=_title)

        self.dialog_manager = dialog_manager
        self.dialog_type = None

        # method to be called when ok/yes button of dialog is clicked
        self.ok_call = kwargs.pop("ok_call", None)

        # method to be called when cancel button of dialog is clicked
        self.cancel_call = kwargs.pop("cancel_call", None)

        # method to be called when dialog is closed without pressing close button
        self.close_call = kwargs.pop("close_call", None)

        self.descriptor_text = kwargs.pop("descriptor_text", "")

        self.ok_button_id = None
        self.cancel_button_id = None

        # set min, max and current sizes for this dialog
        self.SetMinSize((300, 140))
        self.SetMaxSize((450, 140))
        self.SetSize((400, 140))

        self.Bind(wx.EVT_SIZE, self.on_event_size)
        self.Bind(wx.EVT_CLOSE, self.on_event_close)

    def create(self):
        """create widgets for dialogs here, this method must be called before calling dialog.Show()"""
        pass

    def on_ok_button(self, event):
        event.Skip()
        # self.dialog_manager.active_dialogues.remove(self.d)

    def on_cancel_button(self, event):
        if self.cancel_call is not None:
            self.cancel_call()
        self.Close()
        event.Skip()

    def on_event_close(self, event):
        if self.close_call is not None:
            self.close_call()

        self.dialog_manager.active_dialogues.remove(self.dialog_type)

        event.Skip()

    def on_event_size(self, event):
        event.Skip()


class WxTextEntryDialog(WxCustomDialog):
    def __init__(self, *args, **kwargs):
        WxCustomDialog.__init__(self, *args, **kwargs)

        self.dialog_type = "TextEntryDialog"

        if self.descriptor_text is None:
            self.descriptor_text = "Enter text"

        self.initial_text = kwargs.pop("initial_text", "")

        self.wx_text_ctrl = None

    def on_ok_button(self, event):
        if self.ok_call is not None:
            self.ok_call(self.wx_text_ctrl.GetValue())
        self.Close()
        event.Skip()

    def create(self):
        panel = wx.Panel(self)

        text = wx.StaticText(panel, label=self.descriptor_text)
        self.wx_text_ctrl = wx.TextCtrl(panel, value=self.initial_text)

        self.ok_button_id = wx.NewId()
        self.cancel_button_id = wx.NewId()

        static_line = wx.StaticLine(panel, style=wx.LI_HORIZONTAL)

        button_ok = wx.Button(panel, label="Ok", size=(90, 28), id=self.ok_button_id)
        button_close = wx.Button(panel, label="Close", size=(90, 28), id=self.cancel_button_id)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add(text, flag=wx.LEFT | wx.TOP | wx.RIGHT | wx.EXPAND, border=5)
        v_sizer.Add(self.wx_text_ctrl, flag=wx.LEFT | wx.TOP | wx.RIGHT | wx.EXPAND, border=5)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add(button_ok, flag=wx.TOP, border=5)
        h_sizer.Add(button_close, flag=wx.TOP, border=5)

        v_sizer.AddSpacer(7)
        v_sizer.Add(static_line, flag=wx.RIGHT | wx.LEFT | wx.EXPAND, border=5)

        v_sizer.AddSpacer(8)
        v_sizer.Add(h_sizer, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=5)

        panel.SetSizer(v_sizer)

        self.Bind(wx.EVT_BUTTON, self.on_ok_button, id=self.ok_button_id)
        self.Bind(wx.EVT_BUTTON, self.on_cancel_button, id=self.cancel_button_id)


class WxYesNoDialog(WxCustomDialog):
    def __init__(self, *args, **kwargs):
        WxCustomDialog.__init__(self, *args, **kwargs)

        self.dialog_type = "YesNoDialog"

        if self.descriptor_text is None:
            self.descriptor_text = "Are you sure you want to perform this action ?"

        self.wx_text_ctrl = None

        # set min, max and current sizes for this dialog
        self.SetMinSize((300, 115))
        self.SetMaxSize((450, 115))
        self.SetSize((400, 115))

    def on_ok_button(self, event):
        if self.ok_call is not None:
            self.ok_call()

        self.Close()
        event.Skip()

    def create(self):
        panel = wx.Panel(self)

        text = wx.StaticText(panel, label=self.descriptor_text)

        self.ok_button_id = wx.NewId()
        self.cancel_button_id = wx.NewId()

        button_ok = wx.Button(panel, label="Yes", size=(90, 28), id=self.ok_button_id)
        button_close = wx.Button(panel, label="No", size=(90, 28), id=self.cancel_button_id)

        static_line = wx.StaticLine(panel, style=wx.LI_HORIZONTAL)

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add(text, flag=wx.LEFT | wx.TOP | wx.RIGHT | wx.EXPAND, border=5)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add(button_ok, flag=wx.TOP, border=5)
        h_sizer.Add(button_close, flag=wx.TOP, border=5)

        v_sizer.AddSpacer(7)
        v_sizer.Add(static_line, flag=wx.RIGHT | wx.LEFT | wx.EXPAND, border=5)

        v_sizer.AddSpacer(8)

        v_sizer.Add(h_sizer, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=5)

        panel.SetSizer(v_sizer)

        self.Bind(wx.EVT_BUTTON, self.on_ok_button, id=self.ok_button_id)
        self.Bind(wx.EVT_BUTTON, self.on_cancel_button, id=self.cancel_button_id)


class ProjectDialog(WxCustomDialog):
    def __init__(self, *args, **kwargs):
        WxCustomDialog.__init__(self, *args, **kwargs)

        self.dialog_type = "ProjectDialog"

        self.project_name = ""
        self.path = ""

        self.project_set = False

        self.proj_path_txtctrl = None
        self.proj_name_txtctrl = None

        self.ok_button_id = wx.NewId()
        self.cancel_button_id = wx.NewId()
        self.browse_btn_id = wx.NewId()

        self.Bind(wx.EVT_BUTTON, self.on_ok_button, id=self.ok_button_id)
        self.Bind(wx.EVT_BUTTON, self.on_cancel_button, id=self.cancel_button_id)
        self.Bind(wx.EVT_BUTTON, self.on_browse_btn, id=self.browse_btn_id)

        self.SetMaxSize((1000, 1000))
        self.SetMinSize((500, 275))
        # self.SetMaxSize((450, 600))
        self.SetSize((450, 275))

    def create(self):
        panel = wx.Panel(self)

        sizer = wx.GridBagSizer(5, 5)

        main_label = wx.StaticText(panel, label="Create New Project")
        sizer.Add(main_label, pos=(0, 0), flag=wx.TOP | wx.LEFT, border=10)

        # icon = wx.StaticBitmap(panel, bitmap=wx.Bitmap('exec.png'))
        # sizer.Add(icon, pos=(0, 4), flag=wx.TOP | wx.RIGHT | wx.ALIGN_RIGHT, border=5)

        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(1, 0), span=(1, 5), flag=wx.EXPAND | wx.BOTTOM, border=5)

        # project name and text field to type the project name
        project_name = wx.StaticText(panel, label="Name")
        sizer.Add(project_name, pos=(2, 0), flag=wx.LEFT, border=10)
        self.proj_name_txtctrl = wx.TextCtrl(panel)
        sizer.Add(self.proj_name_txtctrl, pos=(2, 1), span=(1, 3), flag=wx.TOP | wx.EXPAND)

        # project path field and text field to type the project path and a browser button to
        # set the project otherwise
        proj_path = wx.StaticText(panel, label="Path")
        sizer.Add(proj_path, pos=(3, 0), flag=wx.LEFT | wx.TOP, border=10)
        self.proj_path_txtctrl = wx.TextCtrl(panel)
        sizer.Add(self.proj_path_txtctrl, pos=(3, 1), span=(1, 3), flag=wx.TOP | wx.EXPAND, border=5)
        proj_path_browse_btn = wx.Button(panel, label="Browse...", id=self.browse_btn_id)
        sizer.Add(proj_path_browse_btn, pos=(3, 4), flag=wx.TOP | wx.RIGHT, border=5)

        # optional settings
        sb = wx.StaticBox(panel, label="Optionals")

        boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        boxsizer.Add(wx.CheckBox(panel, label="Optional 1"), flag=wx.LEFT | wx.TOP, border=5)
        boxsizer.Add(wx.CheckBox(panel, label="Optional 2"), flag=wx.LEFT | wx.TOP | wx.BOTTOM, border=5)
        boxsizer.Add(wx.CheckBox(panel, label="Optional 3"), flag=wx.LEFT | wx.BOTTOM, border=5)
        sizer.Add(boxsizer, pos=(4, 0), span=(1, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=10)

        help_btn = wx.Button(panel, label='Help')
        sizer.Add(help_btn, pos=(5, 0), flag=wx.LEFT, border=10)

        ok_btn = wx.Button(panel, label="Ok", id=self.ok_button_id)
        sizer.Add(ok_btn, pos=(5, 3))

        cancel_btn = wx.Button(panel, label="Cancel", id=self.cancel_button_id)
        sizer.Add(cancel_btn, pos=(5, 4), span=(1, 1), flag=wx.BOTTOM | wx.RIGHT, border=10)

        sizer.AddGrowableCol(2)

        panel.SetSizer(sizer)

    def set_project_info(self, name, path):
        self.project_name = name
        self.path = path
        # print("project name {0} project path {1}".format(self.project_name, self.path))

    def on_ok_button(self, event):
        if self.ok_call is not None:
            self.ok_call(self.proj_name_txtctrl.GetValue(), self.proj_path_txtctrl.GetValue())
        event.Skip()

    def on_browse_btn(self, evt):
        default_path = "C:/Users/Obaid ur Rehman/Desktop/Panda3d/P3dLevelEditor/game"
        dir_dialog = wx.DirDialog(None,
                                  style=wx.DD_DEFAULT_STYLE,
                                  defaultPath=default_path)

        if dir_dialog.ShowModal() == wx.ID_OK:
            self.proj_path_txtctrl.SetValue(dir_dialog.GetPath())
            self.set_project_info(self.proj_name_txtctrl.GetValue(), dir_dialog.GetPath())
            dir_dialog.Destroy()

        else:
            evt.Skip()
