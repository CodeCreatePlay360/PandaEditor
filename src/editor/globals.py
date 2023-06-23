from editor.utils import ObjectRepository


class Editor:
    """The Globals class provide a common interface to most common systems, to avoid repeated imports in individual
    modules"""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Editor, cls).__new__(cls)
        return cls.instance

    __repository = ObjectRepository()

    __observer = None
    __app = None
    __game = None
    __wx_main = None
    __level_editor = None
    __command_mgr = None
    __resource_browser = None
    __scene_graph = None
    __inspector = None
    __console = None

    __ui_config = None

    def init(self,
             observer,
             app,
             wx_main,
             command_mgr,
             level_editor,
             game,
             resource_browser,
             scene_graph,
             inspector,
             console):

        self.__observer = observer
        self.__app = app
        self.__wx_main = wx_main
        self.__command_mgr = command_mgr
        self.__level_editor = level_editor
        self.__game = game

        self.__resource_browser = resource_browser.tree
        self.__scene_graph = scene_graph
        self.__inspector = inspector
        self.__console = console

    def set_ui_config(self, ui_config):
        self.__ui_config = ui_config

    @property
    def observer(self):
        return self.__observer

    @property
    def repository(self):
        return self.repository

    @property
    def p3d_app(self):
        return self.__app

    @property
    def wx_main(self):
        return self.__wx_main

    @property
    def command_mgr(self):
        return self.__command_mgr

    @property
    def level_editor(self):
        return self.__level_editor

    @property
    def game(self):
        return self.__game

    @property
    def resource_browser(self):
        return self.__resource_browser

    @property
    def scene_graph(self):
        return self.__scene_graph

    @property
    def inspector(self):
        return self.__inspector

    @property
    def console(self):
        return self.__console

    @property
    def ui_config(self):
        return self.__ui_config


editor = Editor()
