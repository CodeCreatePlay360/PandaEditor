from thirdparty.event.observable import Observable
from editor.utils import ObjectRepository
from editor.constants import TAG_GAME_OBJECT


class Editor:
    """The Globals class provide a common interface to most common systems, to avoid repeated imports in individual
    modules"""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Editor, cls).__new__(cls)
        return cls.instance

    __observer = Observable()
    __repository = ObjectRepository()

    __p3d_app = None
    __game = None
    __wx_main = None
    __level_editor = None
    __command_mgr = None
    __resource_browser = None
    __scene_graph = None
    __inspector = None
    __console = None

    def init(self, p3d_pp, game, wx_main, level_editor, command_mgr, resource_browser, scene_graph, inspector_panel,
             console):
        self.__p3d_app = p3d_pp
        self.__game = game
        self.__wx_main = wx_main
        self.__level_editor = level_editor
        self.__command_mgr = command_mgr

        self.__resource_browser = resource_browser.tree
        self.__scene_graph = scene_graph
        self.__inspector = inspector_panel
        self.__console = console

    def do_after(self):
        """called after editor is initialized"""
        self.__game = self.__level_editor.project.game

    @property
    def observer(self):
        return self.__observer

    @property
    def repository(self):
        return self.repository

    @property
    def p3d_app(self):
        return self.__p3d_app

    @property
    def game(self):
        return self.__game

    @property
    def wx_main(self):
        return self.__wx_main

    @property
    def level_editor(self):
        return self.__level_editor

    @property
    def command_mgr(self):
        return self.__command_mgr

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


editor = Editor()
