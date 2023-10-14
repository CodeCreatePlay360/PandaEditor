import os.path

from panda3d.core import get_model_path, Filename
from game.game import Game


class Project(object):
    def __init__(self, app):

        self.app = app
        self.game = None

        self.project_name = ""
        self.project_path = ""

        self.user_modules = []

    def set_project(self, name: str, path):
        assert os.path.exists(path)
        assert os.path.isdir(path)
        # TODO make sure directory is empty assert dir.is_empty

        self.project_name = name
        self.project_path = path

        # set window title
        self.app.wx_main.SetTitle("PandaEditor (defaultProject)")

        # sys.path.append(self.project_path)
        # clear panda3d's current model paths and set new according to new project path
        panda_path = Filename.fromOsSpecific(path)
        get_model_path().prependDirectory(panda_path)

        self.game = Game(
            ProjectPath=self.project_path,
            show_base=self.app.show_base,
            win=self.app.editor_workspace.main_win,
            render=self.app.show_base.render,
        )
