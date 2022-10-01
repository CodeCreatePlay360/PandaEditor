from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from direct.showbase.ShowBase import taskMgr
from editor.globals import editor


class DirEventProcessor(FileSystemEventHandler):
    def __init__(self):
        self.received_events = []
        self.dir_event_task = None
        self.__last_event = None

    def on_any_event(self, event):
        if self.dir_event_task is None:
            taskMgr.add(self.dir_evt_timer, "DirEventTimer", sort=0, priority=None)
        self.received_events.append(event)

    def dir_evt_timer(self, task):
        if task.time > 1:
            taskMgr.remove("DirEventTimer")
            self.dir_event_task = None
            self.create_dir_event()
            return
        return task.cont

    def create_dir_event(self):
        interested_events = []
        for evt in self.received_events:
            path = evt.src_path
            file_name = path.split("\\")[-1]

            # new directory sends "created" and "modified" events consecutively,
            # this will cause editor to reload twice whenever a new dir is created,
            # this check will ensure "created" and "modified" are not sent consecutively by
            # keeping track of last event.
            if evt.event_type == "modified" and self.__last_event == "created":
                continue
            self.__last_event = evt.event_type
            #
            # -------------------------------------------------------------------------------

            if any([evt.event_type == "modified", evt.event_type == "created",
                    evt.event_type == "moved", evt.event_type == "deleted"]):
                interested_events.append(file_name)

        if len(interested_events) > 0:
            editor.observer.trigger("EditorReload", interested_events)

        self.received_events = []


class DirWatcher:
    def __init__(self, *args, **kwargs):
        self.__observer = Observer()
        self.__observer.setDaemon(daemonic=True)
        self.event_handler = DirEventProcessor()
        
        # an observer watch object is returned by self.observer.schedule method,
        # obs-watch_and_paths object maps a path, and it's corresponding observer-watch object
        # obs-watch_and_paths[path] = observer-watch object
        self.observer_paths = {}
        self.run()

    def run(self):
        # print("Directory watcher initialized")
        self.__observer.start()
        # self.observer.join()

    def schedule(self, path, append=True):
        if not append:
            self.__observer.unschedule_all()

        observer_object = self.__observer.schedule(self.event_handler, path, recursive=True)
        self.observer_paths[path] = observer_object
        
    def unschedule(self, path):
        observer_object = self.observer_paths[path]
        self.__observer.unschedule(observer_object)
        del self.observer_paths[path]
