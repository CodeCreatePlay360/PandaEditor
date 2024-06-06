from utils import SingleTask
from .resource import Resource
from system import Systems


class Script(Resource, SingleTask):
    def __init__(self, path, name):
        Resource.__init__(self, path)
        SingleTask.__init__(self, name)
        
        self.__win = Systems.win
        self.__mouse_watcher = Systems.game.mouse_watcher
        self.__render = Systems.game.active_scene.render
        self.__render2d = Systems.game.active_scene.render2d
        self.__aspect2d = Systems.game.active_scene.aspect2d
        
    def win(self):
        return self.__win
    
    def mouse_watcher(self):
        return self.__mouse_watcher
    
    def render(self):
        return self.__render
        
    def render2d(self):
        return self.__render2d
    
    def aspect2d(self):
        return self.__aspect2d
