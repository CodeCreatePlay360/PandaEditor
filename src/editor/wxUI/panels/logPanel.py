import sys
import wx
import editor.edPreferences as edPreferences
import editor.constants as constants
from editor.wxUI.custom import ControlGroup, SelectionButton, ToggleButton

Models_icon = constants.ICONS_PATH + "//" + "3D-objects-icon.png"
Textures_icon = constants.ICONS_PATH + "//" + "images.png"
Sounds_icon = constants.ICONS_PATH + "//" + "music.png"
Scripts_icon = constants.ICONS_PATH + "//" + "script_code.png"


class LogPanel(wx.Panel):
    """
    Simple wxPanel containing a text control which will display the stdout and
    stderr streams.
    """

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
        self.SetBackgroundColour(edPreferences.Colors.Panel_Dark)
        # self.SetWindowStyleFlag(wx.BORDER_SUNKEN)

        # build top controls bar
        # create control buttons
        # self.control_group = ControlGroup(self, self.on_control_btn_select, max_size=wx.Size(-1, 14))
        # self.control_group.SetBackgroundColour(edPreferences.Colors.Panel_Dark)
        #
        # clear_on_play_btn = ToggleButton(parent=self.control_group, btn_index=1, label_text="ClearOnPlay",
        #                                  text_pos=(15, -1), center_text=True,
        #                                  select_func=self.on_control_btn_select,
        #                                  deselect_func=self.on_control_btn_deselect)
        #
        # clear_on_reload_btn = ToggleButton(parent=self.control_group, btn_index=1, label_text="ClearOnReload",
        #                                    text_pos=(2, -1), center_text=True,
        #                                    select_func=self.on_control_btn_select,
        #                                    deselect_func=self.on_control_btn_deselect)
        #
        # clear_on_play_btn.deselect()
        # clear_on_reload_btn.deselect()
        #
        # self.control_group.add_button(clear_on_play_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
        # self.control_group.add_button(clear_on_reload_btn, flags=wx.EXPAND | wx.RIGHT, border=1)

        # build log text control
        self.tc = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.NO_BORDER)
        self.tc.SetBackgroundColour(edPreferences.Colors.Panel_Normal)
        self.tc.SetForegroundColour(edPreferences.Colors.Console_Text)

        # redirect text here
        sys.stdout = self.RedirectText(sys.stdout, self.tc)
        sys.stderr = self.RedirectText(sys.stderr, self.tc)

        # build sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.sizer.Add(self.control_group, 1, wx.EXPAND | wx.BOTTOM, border=1)
        self.sizer.Add(self.tc, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.tc.Bind(wx.EVT_LEFT_UP, self.on_evt_left_up)

    def on_control_btn_select(self, index):
        pass

    def on_control_btn_deselect(self, index):
        pass

    def on_evt_left_up(self, evt):
        constants.obs.trigger("OnMouse1up", self)
        evt.Skip()
