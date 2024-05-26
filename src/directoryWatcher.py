import os.path
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from direct.task.TaskManagerGlobal import taskMgr


class DirEventProcessor(FileSystemEventHandler):
    def __init__(self, **kwargs):
        self.__any_evt_callback = kwargs.pop("any_evt_callback", None)
        self.__delay = 3.5
        self.__set = False

    def on_any_event(self, event):
        '''
        print("-- [Directory Watcher] RecievedEvent  Path: '{0}' Type '{1}'".format(
               event.src_path, event.event_type))
        '''
                
        '''
        # ignore event we are not interested in
        if event.event_type == "opened" or event.event_type == "modified":
            return
        
        # ignore cache dirs / files
        # TODO check type of os and set split operator accordingly
        src_path = str(Path(event.src_path))
        
        if "__pycache__" in src_path.split("//"):
            return
        
        if src_path.split(".")[-1] == "pyc":
            return
        
        if event.event_type == "created" and os.path.isdir(src_path):
            print("empty dir event")
            return
        '''
        
        if not self.__set:
            timer = threading.Timer(self.__delay, self.reset)
            timer.start()
            self.__set = True
        
    def reset(self):
        self.__set = False
        
        if self.__any_evt_callback:
            self.__any_evt_callback()


class DirWatcher:
    def __init__(self, *args, **kwargs):
        self.__observer = Observer()
        self.__observer.setDaemon(daemonic=True)
        self.__dir_event_processor = DirEventProcessor(**kwargs)

        self.__observer_paths = {}
        
        self.unschedule_all()
        self.run()

    def get_observer(self):
        return self.__observer

    def get_observer_paths(self):
        return self.__observer_paths

    def run(self):
        self.__observer.start()
        # self.observer.join()

    def schedule(self, path, append=True):
        if not append:
            self.__observer.unschedule_all()

        observer_object = self.__observer.schedule(self.__dir_event_processor, path, recursive=True)
        self.__observer_paths[path] = observer_object
        print("-- Path [{0}] scheduled for watch".format(path))

    def unschedule(self, path):
        observer_object = self.__observer_paths[path]
        self.__observer.unschedule(observer_object)
        del self.__observer_paths[path]

    def unschedule_all(self):
        self.__observer.unschedule_all()
        self.__observer_paths.clear()
