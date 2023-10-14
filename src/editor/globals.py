
class Editor:
    """The Globals class provide a common interface to most common systems, to avoid repeated imports in individual
    modules"""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Editor, cls).__new__(cls)
        return cls.instance

    __app = None
    __observer = None
    __command_mgr = None
    __level_editor = None

    __ui_config = None,
    __ui_evt_handler = None,

    __wx_main = None
    __resource_browser = None
    __scene_graph = None
    __inspector = None
    __console = None

    def init(self,
             app,
             command_mgr,
             level_editor,

             wx_main,
             resource_browser,
             scene_graph,
             inspector,
             console):

        self.__app = app
        self.__command_mgr = command_mgr
        self.__level_editor = level_editor

        self.__wx_main = wx_main
        self.__resource_browser = resource_browser.tree
        self.__scene_graph = scene_graph
        self.__inspector = inspector
        self.__console = console

    def get_ui_evt_handler(self):
        return self.__ui_evt_handler

    def set_ui_config(self, ui_config):
        self.__ui_config = ui_config

    def set_ui_evt_handler(self, handler):
        self.__ui_evt_handler = handler

    def set_observer(self, observer):
        self.__observer = observer

    @property
    def observer(self):
        return self.__observer

    @property
    def repository(self):
        return self.repository

    @property
    def p3D_app(self):
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
