import os.path
from panda3d.core import get_model_path, Filename
from game import Game


class Project(object):
    def __init__(self, demon):
 
        self.__name = ""
        self.__path = ""
        self.__game = Game(demon)
        
    def set_project(self, path: str):
        assert os.path.exists(path), "Path does not exists."
        assert os.path.isdir(path), "Path is not a directory"
        
        # TODO make sure directory is empty
        self.__name = "PandaEditorProject"
        self.__path = path

        # set window title
        pass

        # clear panda3d's current model paths and set new according to new project path
        panda_path = Filename.fromOsSpecific(path)
        get_model_path().prependDirectory(panda_path)
        
        print("-- Project created successfully")
        
        self.__game.init()
        
    @property
    def game(self):
        return self.__game

    @property
    def path(self):
        return self.__path
