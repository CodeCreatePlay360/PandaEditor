import editor.constants as constants
from panda3d.core import WindowProperties
from editor.showBase import ShowBase
from editor.wxUI.wxMain import WxFrame
from editor.levelEditor import LevelEditor
from editor.p3d import wxPanda
from editor.commandManager import CommandManager, Command


class MyApp(wxPanda.App):
    wx_main = None
    show_base = None
    _mouse_mode = None
    level_editor = None
    obs = None
    command_manager = None

    def init(self):
        constants.object_manager.add_object("P3dApp", self)

        # self.obs = Observable()
        self.wx_main = WxFrame(parent=None, title="PandaEditor (Default Project)", size=(800, 600))
        self.show_base = ShowBase(self.wx_main.ed_viewport_panel)

        self.wx_main.Show()
        self.ReplaceEventLoop()

        constants.wx.CallAfter(self.finish_init)

    def finish_init(self):
        constants.p3d_app = self
        self.show_base.finish_init()
        self.level_editor = LevelEditor(self)
        self.wx_main.finish_init()
        self.level_editor.start()
        self.command_manager = CommandManager()

        self.set_mouse_mode("Confined")

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
        wp.setMouseMode(WindowProperties.M_confined)
        self.show_base.main_win.requestProperties(wp)

    def get_mouse_mode(self):
        return self._mouse_mode
