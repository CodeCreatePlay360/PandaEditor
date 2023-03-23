import os.path

import editor.constants as constants
import sys
import wx

from panda3d.core import WindowProperties
from direct.showbase.ShowBase import taskMgr
from editor.showBase import ShowBase
from editor.eventHandler import *
from editor.wxUI.wxMain import WxFrame
from editor.levelEditor import LevelEditor
from editor.p3d import wxPanda
from editor.commandManager import CommandManager, Command
from editor.globals import editor


class MyApp(wxPanda.App):
    wx_main = None
    show_base = None
    _mouse_mode = None
    level_editor = None
    command_manager = None

    __current_ui_update_interval = 0
    __ui_update_delay = 1

    def init(self, path):
        constants.EDITOR_PATH = path
        constants.DEFAULT_PROJECT_PATH = os.path.join(path, "Default Project")

        self.wx_main = WxFrame(parent=None, title="PandaEditor (Default Project)", size=(800, 600))
        self.show_base = ShowBase(self.wx_main.ed_viewport_panel)
        self.replace_event_loop()
        self.wx_main.do_after()
        wx.CallLater(50, self.init_editor)

    def init_editor(self):
        if self.wx_main.ed_viewport_panel.GetHandle() == 0:
            wx.CallLater(50, self.init_editor)
            print("WARNING: Unable to get platform specific handle...!")
            return

        self.show_base.finish_init()
        self.command_manager = CommandManager()
        self.level_editor = LevelEditor(self)

        # manually do some setup
        self.level_editor.create_new_project("DefaultProject", constants.DEFAULT_PROJECT_PATH)

        # initialize globals
        editor.init(
            observer=self.observer,
            app=self,
            wx_main=self.wx_main,
            command_mgr=self.command_manager,
            level_editor=self.level_editor,
            game=self.level_editor.project.game,
            resource_browser=self.wx_main.resource_browser,
            scene_graph=self.wx_main.scene_graph_panel.scene_graph,
            inspector_panel=self.wx_main.inspector_panel,
            console=self.wx_main.console_panel,
        )

        # finally, create your first scene
        self.level_editor.create_new_scene(True)

        self.wx_main.resource_browser.tree.remove_all_libs()
        self.wx_main.resource_browser.tree.create_or_rebuild_tree(self.level_editor.project.project_path,
                                                                  rebuild_event=False)
        self.level_editor.register_user_modules(self.wx_main.resource_browser.tree.resources["py"])
        self.level_editor.register_text_files(editor.resource_browser.resources["txt"])
        self.wx_main.resource_browser.tree.schedule_dir_watcher()

    def wx_step(self, task=None):
        super(MyApp, self).wx_step(task)

        if task is not None:
            # sometimes on linux/ubuntu panda window looses focus even when in focus so force set it to foreground
            if sys.platform == "linux" and \
                    self.wx_main.ed_viewport_panel._initialized and \
                    self.show_base.ed_mouse_watcher_node.hasMouse() and \
                    not self.wx_main.ed_viewport_panel._win.getProperties().getForeground():
                self.wx_main.ed_viewport_panel.set_focus()

            if task.time > self.__current_ui_update_interval:
                self.wx_main.status_panel.write_tasks_info(len(taskMgr.getAllTasks()))
                self.__current_ui_update_interval += self.__ui_update_delay

            if self.level_editor:
                self.level_editor.update(task)

            return task.cont

    @property
    def observer(self):
        # defined in event_handler
        return obs

    def set_mouse_mode(self, mode):
        if mode not in [WindowProperties.M_absolute, WindowProperties.M_relative, WindowProperties.M_confined]:
            print("[PandaApp] Incorrect mouse mode {0}, current mouse mode set to {1}".format(mode, "Absolute"))
            self._mouse_mode = WindowProperties.M_absolute
            return

        self._mouse_mode = mode
        wp = WindowProperties()
        wp.setMouseMode(WindowProperties.M_confined)
        self.show_base.main_win.requestProperties(wp)
