import sys
import pathlib
import wx
import wx.richtext as rich_text
from editor.constants import ICONS_PATH
from editor.ui.splitwindow import SplitWindow
from editor.ui.custom.controlGroup import BasicButton, ToggleButton
from editor.globals import editor


Models_icon = str(pathlib.Path(ICONS_PATH + "/3D-objects-icon.png"))
Textures_icon = str(pathlib.Path(ICONS_PATH + "/images.png"))
Sounds_icon = str(pathlib.Path(ICONS_PATH + "/music.png"))
Scripts_icon = str(pathlib.Path(ICONS_PATH + "/script_code.png"))
Image_Clear = str(pathlib.Path(ICONS_PATH + "/Console/trashBin.png"))


class LogPanel(SplitWindow):
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

            self.toggle_clear_on_play = ToggleButton(self, 1, "ClearOnPlay ", select_func=self.on_toggle,
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

        def write(self, text, txt_color: () = None):
            if txt_color is None:
                self.textCtrl.BeginTextColour(editor.ui_config.color_map("Text_Secondary"))
            else:
                self.textCtrl.BeginTextColour(txt_color)

            self.terminal.write(text)
            self.textCtrl.WriteText(text)

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))
        self.create_header()
        self.clear_on_reload = False
        self.clear_on_play = False

        # toolbar
        self.tool_bar = LogPanel.ToolBar(self)

        # build log text control
        self.tc = rich_text.RichTextCtrl(self, style=wx.VSCROLL | wx.NO_BORDER)
        self.tc.SetBackgroundColour(wx.Colour(70, 70, 70, 255))

        font = wx.Font(wx.FontInfo().Family(wx.FONTFAMILY_SWISS))
        self.tc.SetFont(font)

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
        self.sizer = self.GetSizer()
        # self.SetSizer(self.sizer)

        self.sizer.Add(static_line_0, 0, wx.EXPAND)
        self.sizer.Add(self.tool_bar, 0, wx.EXPAND | wx.BOTTOM, border=0)
        self.sizer.Add(static_line_1, 0, wx.EXPAND)
        self.sizer.Add(self.tc, 1, wx.EXPAND | wx.LEFT, border=-3)
        
        return self

    def on_ed_reload(self):
        if self.clear_on_reload:
            self.tc.Clear()

    def on_enter_game_state(self):
        if self.clear_on_play:
            self.tc.Clear()

    def clear_console(self):
        self.tc.Clear()
