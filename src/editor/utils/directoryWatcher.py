from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from direct.showbase.ShowBase import taskMgr
from editor.globals import editor


class DirEventProcessor(FileSystemEventHandler):
    def __init__(self, observer):
        self.received_events = []
        self.__dir_event_task = None
        self.__last_event = None
        self.__progress_dialog = None
        self.__watcher = observer

    def on_any_event(self, event):
        if event.event_type == "opened":
            return

        watch_paths = [*self.__watcher.observer_paths.keys()]
        self.__watcher.unschedule_all()

        if self.__dir_event_task is None:
            self.__dir_event_task = taskMgr.add(self.dir_evt_timer, "DirEventTimer", sort=0, priority=None)

        for path in watch_paths:
            self.__watcher.schedule(path)

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
