import sys
import pathlib
import wx
import wx.richtext as richText
import editor.constants as constants
from editor.ui.custom.controlGroup import BasicButton, ToggleButton
from editor.globals import editor

Models_icon = str(pathlib.Path(constants.ICONS_PATH + "/3D-objects-icon.png"))
Textures_icon = str(pathlib.Path(constants.ICONS_PATH + "/images.png"))
Sounds_icon = str(pathlib.Path(constants.ICONS_PATH + "/music.png"))
Scripts_icon = str(pathlib.Path(constants.ICONS_PATH + "/script_code.png"))
Image_Clear = str(pathlib.Path(constants.ICONS_PATH + "/Console/trashBin.png"))


class LogPanel(wx.Panel):
    """
    Simple wxPanel containing a text control which will display the stdout and
    stderr streams.
    """

    class ToolBar(wx.Panel):
        def __init__(self, *args, **kwargs):
            wx.Panel.__init__(self, *args)
            self.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))

            self.parent = args[0]

            self.sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.SetSizer(self.sizer)

            # add controls to sizer
            self.toggle_clear_on_reload = ToggleButton(self, 0, "ClearOnReload ", select_func=self.on_toggle,
                                                       deselect_func=self.on_toggle_off)
            self.toggle_clear_on_reload.SetMinSize(wx.Size(80, -1))

            self.toggle_clear_on_play = ToggleButton(self, 1, "ClearConsole ", select_func=self.on_toggle,
                                                     deselect_func=self.on_toggle_off)

            self.clear_console_btn = BasicButton(self, 2, "ClearConsole ", select_func=self.on_button)

            # add controls to sizer
            self.sizer.Add(self.toggle_clear_on_reload, 0)
            self.sizer.Add(self.toggle_clear_on_play, 1, wx.EXPAND | wx.LEFT, 1)
            self.sizer.Add(self.clear_console_btn, 0, wx.LEFT, 1)

        def on_toggle(self, idx, data):
            if idx == 0:
                self.parent.clear_on_reload = True
            elif idx == 1:
                self.parent.clear_on_play = True

        def on_toggle_off(self, idx):
            if idx == 0:
                self.parent.clear_on_reload = False
            elif idx == 1:
                self.parent.clear_on_play = False

        def on_button(self, idx, data):
            self.parent.clear_console()

    class RedirectText(object):
        def __init__(self, terminal, text_ctrl):
            self.terminal = terminal
            self.textCtrl = text_ctrl

            # Set err to True if the stream is stderr
            self.err = False
            if terminal is sys.stderr:
                self.err = True

        def write(self, text):
            self.terminal.write(text)
            self.textCtrl.WriteText(text)

            # If the text came from stderr, thaw the top window of the 
            # application or else we won't see the message!
            if self.err:
                wx.CallAfter(self.thaw_top_window)

        def thaw_top_window(self):
            """
            If the application has thrown an assertion while the top frame has
            been frozen then we won't be able to see the text. This method once
            called after to write() method above will make sure the top frame
            is thawed - making the text visible.
            """
            top_win = wx.GetApp().GetTopWindow()
            if top_win.IsFrozen():
                top_win.Thaw()

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))

        self.clear_on_reload = False
        self.clear_on_play = False

        # toolbar
        self.tool_bar = LogPanel.ToolBar(self)

        # build log text control
        self.tc = richText.RichTextCtrl(self, style=wx.VSCROLL | wx.NO_BORDER)
        self.tc.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))
        self.tc.BeginTextColour(editor.ui_config.color_map("Text_Secondary"))

        # static line
        static_line_0 = wx.Panel(self)
        static_line_0.SetMaxSize(wx.Size(-1, 3))
        static_line_0.SetBackgroundColour(wx.Colour(50, 50, 50, 255))

        static_line_1 = wx.Panel(self)
        static_line_1.SetMaxSize(wx.Size(-1, 3))
        static_line_1.SetBackgroundColour(wx.Colour(50, 50, 50, 255))

        # redirect text here
        sys.stdout = self.RedirectText(sys.stdout, self.tc)
        sys.stderr = self.RedirectText(sys.stderr, self.tc)

        # build sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.sizer.Add(static_line_0, 0, wx.EXPAND)
        self.sizer.Add(self.tool_bar, 0, wx.EXPAND | wx.BOTTOM, border=0)
        self.sizer.Add(static_line_1, 0, wx.EXPAND)
        self.sizer.Add(self.tc, 1, wx.EXPAND | wx.LEFT, border=-3)

    def on_ed_reload(self):
        if self.clear_on_reload:
            self.tc.Clear()

    def on_enter_game_state(self):
        if self.clear_on_play:
            self.tc.Clear()

    def clear_console(self):
        self.tc.Clear()
