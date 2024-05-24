import os.path
from panda3d.core import get_model_path, Filename
from game import Game


class Project(object):
    def __init__(self, demon):

        self.project_name = ""
        self.path = ""
        
        self.__game = Game(self.path, demon)

    def set_project(self, path: str):
        assert os.path.exists(path), "Path does not exists."
        assert os.path.isdir(path), "Path is not a directory"
        
        # TODO make sure directory is empty
                
        self.project_name = "PandaEditorProject"
        self.path = path

        # set window title
        # self.app.wx_main.SetTitle("PandaEditor (defaultProject)")

        # clear panda3d's current model paths and set new according to new project path
        panda_path = Filename.fromOsSpecific(path)
        get_model_path().prependDirectory(panda_path)
        
        print("-- Project created successfully")
        
    @property
    def game(self):
        return self.__game
