from panda3d.core import WindowProperties
from editor.showBase import ShowBase
from editor.wxUI.wxMain import WxFrame
from editor.levelEditor import LevelEditor
from editor.p3d import wxPanda
from editor.constants import object_manager, wx
from editor.actionManager import ActionManager


class MyApp(wxPanda.App):
    wx_main = None
    show_base = None
    _mouse_mode = None
    level_editor = None
    obs = None

    def init(self):
        object_manager.add_object("P3dApp", self)

        # self.obs = Observable()
        self.wx_main = WxFrame(parent=None, title="PandaEditor (Default Project)", size=(800, 600))
        self.show_base = ShowBase(self.wx_main.ed_viewport_panel)

        self.wx_main.Show()
        self.ReplaceEventLoop()

        wx.CallAfter(self.finish_init)

    def finish_init(self):
        self.show_base.finish_init()
        self.level_editor = LevelEditor(self)
        self.wx_main.finish_init()
        self.level_editor.start()

    MOUSE_MODE_MAP = {"Absolute": WindowProperties.M_absolute,
                      "Relative": WindowProperties.M_relative,
                      "Confined": WindowProperties.M_confined}

    def set_mouse_mode(self, mode):
        if mode not in self.MOUSE_MODE_MAP.keys():
            print("[PandaApp] Incorrect mouse mode {0}, current mouse mode set to {1}".format(mode, "Absolute"))
            self._mouse_mode = self.MOUSE_MODE_MAP[0]
            return

        mode = self.MOUSE_MODE_MAP[mode]
        self._mouse_mode = mode
        wp = WindowProperties()
        wp.setMouseMode(mode)
        self.wx_main.ed_viewport_panel.GetWindow().requestProperties(wp)

    def set_cursor_hidden(self, hidden=False):
        wp = WindowProperties()
        wp.setCursorHidden(hidden)
        self.wx_main.game_viewport_panel.GetWindow().requestProperties(wp)

    def get_mouse_mode(self):
        return self._mouse_mode
