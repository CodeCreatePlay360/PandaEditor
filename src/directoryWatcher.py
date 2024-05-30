import os.path
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DirEventProcessor(FileSystemEventHandler):
    def __init__(self, **kwargs):
        self.__any_evt_callback = kwargs.pop("any_evt_callback", None)
        self.__delay = 3.5
        
        self.__thread = None
        self.__stop_event = threading.Event()

    def on_any_event(self, event):
        print(event)
        if os.path.isdir(event.src_path):
            return
                
        if event.src_path.split(".")[-1] == "pyc":
            return
        
        print("-- [Directory Watcher] RecievedEvent  Path: '{0}' Type '{1}'".format(
               event.src_path, event.event_type))
               
        self.start()

    def start(self):
        self.stop()  # Ensure any existing timer is stopped before starting a new one
        self.__stop_event.clear()
        self.__thread = threading.Thread(target=self._run)
        self.__thread.start()
        # print("DirWatcher Timer started.")
            
    def _run(self):
        if not self.__stop_event.wait(self.__delay):
            self.reset()
            
    def stop(self):
        if self.__thread is not None:
            self.__stop_event.set()
            self.__thread.join()
            self.__thread = None
            # print("DirWatcher Timer stopped.")

    def reset(self):
        if self.__any_evt_callback:
            self.__any_evt_callback()
        self.__thread = None


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
