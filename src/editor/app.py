import os.path
import pathlib
import wx
import editor.constants as constants

from direct.showbase.ShowBase import taskMgr
from direct.showbase import ShowBase as sb
from editor.workspace import EditorWorkspace
from editor.ui.wxMain import WxFrame
from editor.ui.config import UI_Config
from editor.levelEditor import LevelEditor
from editor.p3d import wxPanda
from editor.commandManager import CommandManager, Command
from editor.build import BuildScript
from editor.globals import editor
from thirdparty.event.observable import Observable


class Showbase(sb.ShowBase):
    def __init__(self):
        sb.ShowBase.__init__(self)


class MyApp(wxPanda.App):
    wx_main = None
    observer = None
    show_base = None
    editor_workspace = None
    level_editor = None
    command_manager = None
    ui_config = None

    __current_ui_update_interval = 0
    __ui_update_delay = 1
    __max_get_handle_attempts = 7
    __current_get_handle_attempts = 0

    def init(self, path):
        constants.EDITOR_PATH = path
        constants.DEFAULT_PROJECT_PATH = os.path.join(path, "defaultProject")

        self.ui_config = UI_Config(str(pathlib.Path("src/config.xml")))
        editor.set_ui_config(self.ui_config)

        self.observer = Observable()
        editor.set_observer(self.observer)

        self.wx_main = WxFrame(parent=None, title="PandaEditor (defaultProject)", size=(800, 600))
        # self.show_base = ShowBase(self.wx_main.ed_viewport_panel)
        self.show_base = Showbase()
        self.editor_workspace = EditorWorkspace(self.show_base, self.wx_main.ed_viewport_panel)

        self.replace_event_loop()
        self.wx_main.do_after()

        wx.CallLater(50, self.init_editor)

    def foo(self):
        import editor.eventHandler
        from editor.ui.eventhandler import WxEventHandler
        self.ui_evt_hanlder = WxEventHandler

    def init_editor(self):
        if self.wx_main.ed_viewport_panel.GetHandle() == 0 and \
                self.__current_get_handle_attempts < self.__max_get_handle_attempts:
            wx.CallLater(50, self.init_editor)
            self.__max_get_handle_attempts += 1
            return

        if self.wx_main.ed_viewport_panel.GetHandle() == 0:
            print("Unable to find platform specific Handle, exiting.")
            self.quit()

        self.__current_get_handle_attempts = 0
        # self.show_base.finish_init()
        self.editor_workspace.initialize()
        self.command_manager = CommandManager()
        self.level_editor = LevelEditor(self)

        # initialize globals
        editor.init(
            app=self,
            command_mgr=self.command_manager,
            level_editor=self.level_editor,

            wx_main=self.wx_main,
            resource_browser=self.wx_main.resource_browser,
            scene_graph=self.wx_main.scenegraph.scene_graph,
            inspector=self.wx_main.inspector_panel,
            console=self.wx_main.console_panel
        )

        self.foo()
        editor.set_ui_evt_handler(self.ui_evt_hanlder)
        self.level_editor.start()
        editor.observer.trigger("EditorReload")
        # # setup some defaults
        # self.wx_main.resource_browser.tree.create_or_rebuild_tree(self.level_editor.project.project_path,
        #                                                           rebuild_event=False)
        # self.level_editor.register_user_modules(self.wx_main.resource_browser.tree.resources["py"])
        # self.level_editor.register_text_files(editor.resource_browser.resources["txt"])
        # self.wx_main.resource_browser.tree.collapse_all()
        #
        # item_to_sel_path = os.path.join(constants.DEFAULT_PROJECT_PATH, "Samples/Basics_01")
        # item_to_sel_path = str(pathlib.Path(item_to_sel_path))
        # item_to_sel = self.wx_main.resource_browser.tree.get_item_by_path(item_to_sel_path)
        # self.wx_main.resource_browser.tree.SelectItem(item_to_sel)
        # self.wx_main.resource_browser.tree.Expand(item_to_sel)
        # self.wx_main.resource_browser.tree.Refresh()

    def on_win_event(self):
        """panda3D window_event"""
        pass

    def run_build_script(self, *args, **kwargs):
        BuildScript.run(
            project_path=self.level_editor.project.project_path,
            output_dir="E:\Final\P3D_Build",
            *args, **kwargs)

    def wx_step(self, task=None):
        super(MyApp, self).wx_step(task)

        if task is not None:
            # sometimes on linux/ubuntu panda window looses focus even when in focus so force set it to foreground
            if False and \
                    self.wx_main.ed_viewport_panel._initialized and \
                    self.show_base.ed_mouse_watcher_node.hasMouse() and \
                    not self.wx_main.ed_viewport_panel._win.getProperties().getForeground():
                self.wx_main.ed_viewport_panel.set_focus()

            # Todo do something about this ui update
            if task.time > self.__current_ui_update_interval:
                self.wx_main.status_panel.write_tasks_info(len(taskMgr.getAllTasks()))
                self.__current_ui_update_interval += self.__ui_update_delay
            # ----------------------------------------------------------------------------

            if self.level_editor:
                self.level_editor.update(task)

            return task.cont
