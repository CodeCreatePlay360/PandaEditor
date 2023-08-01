import os.path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from direct.showbase.ShowBase import taskMgr
from editor.globals import editor
from editor.constants import GAME_STATE


class DirEventProcessor(FileSystemEventHandler):
    def __init__(self, observer):
        self.received_events = []
        self.__dir_event_task = None
        self.__last_event = None
        self.__progress_dialog = None
        self.__watcher = observer

    def on_any_event(self, event):
        # ignore modified event for a directory, we only care about created event for a directory
        if os.path.isdir(event.src_path) and event.event_type == "modified":
            return

        # sometimes during game state, dir event is triggered even when there are no actual modifications,
        # at least on WIN_32 platforms
        # on disk (I am not sure as to why this is happening, this should be further tested)
        # should be tested with other platforms macOS, linux etc.
        if editor.level_editor.ed_state == GAME_STATE and os.path.isdir(event.src_path):
            return

        # ignore junk files as well
        if "pyc" in event.src_path.split("."):
            return

        if event.event_type == "opened":
            return

        # watch_paths = [*self.__watcher.observer_paths.keys()]
        # self.__watcher.unschedule_all()

        if self.__dir_event_task is None:
            self.__dir_event_task = taskMgr.add(self.dir_evt_timer, "DirEventTimer", sort=0, priority=None, delay=0.1)

        # for path in watch_paths:
        #     self.__watcher.schedule(path)

    def dir_evt_timer(self, task):
        editor.observer.trigger("EditorReload")
        taskMgr.remove("DirEventTimer")
        self.__dir_event_task = None
        return task.cont


class DirWatcher:
    def __init__(self, *args, **kwargs):
        self.__observer = Observer()
        self.__observer.setDaemon(daemonic=True)
        self.__event_handler = DirEventProcessor(self)

        self.__observer_paths = {}
        self.run()

    def run(self):
        self.__observer.start()
        # self.observer.join()

    def schedule(self, path, append=True):
        if not append:
            self.__observer.unschedule_all()

        observer_object = self.__observer.schedule(self.__event_handler, path, recursive=True)
        self.__observer_paths[path] = observer_object

    def unschedule(self, path):
        observer_object = self.__observer_paths[path]
        self.__observer.unschedule(observer_object)
        del self.__observer_paths[path]

    def unschedule_all(self):
        self.observer.unschedule_all()
        self.observer_paths.clear()

    @property
    def observer(self):
        return self.__observer

    @property
    def observer_paths(self):
        return self.__observer_paths
