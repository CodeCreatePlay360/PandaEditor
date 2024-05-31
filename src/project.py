import os.path
from pathlib import Path
from directoryWatcher import DirWatcher
from panda3d.core import get_model_path, Filename


class Project(object):
    def __init__(self, demon):
 
        self.__name = ""
        self.__path = ""
        self.__demon = demon
        self.__game = demon.game
        
        self.__dir_watcher = DirWatcher(any_evt_callback=demon.on_dir_event)
        
    def set_project(self, path: str):
        assert os.path.exists(path), "Path does not exists."
        assert os.path.isdir(path), "Path is not a directory"
        
        # TODO make sure directory is empty
        self.__name = "PandaEditorProject"
        self.__path = path

        # set window title
        pass

        # clear panda3d's current model paths and set
        # new according to new project path
        # panda_path = Filename.fromOsSpecific(path)
        get_model_path().prependDirectory(path)
        
        self.__dir_watcher.schedule(path)
        
        print("-- Project created successfully")
        
    def reload(self):
        pass
        
    def get_all_scripts(self):
        ext = "py"
        path = Path(self.__path)
        return [str(file) for file in path.rglob(f'*{ext}')]

    @property
    def path(self):
        return self.__path
