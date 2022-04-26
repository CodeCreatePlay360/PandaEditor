from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import editor.constants as constants
from direct.showbase.ShowBase import taskMgr


class DirEventProcessor(FileSystemEventHandler):
    def __init__(self):
        self.received_events = []
        self.dir_event_task = None

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

            # make sure to only include .py files and check for duplicates as well
            if any([evt.event_type == "modified", evt.event_type == "created",
                    evt.event_type == "moved", evt.event_type == "deleted"]):
                #  and all([file_name.endswith(".py"), file_name not in interested_events]):
                interested_events.append(file_name)

        if len(interested_events) > 0:
            constants.obs.trigger("DirectoryEvent", interested_events)

        self.received_events = []


class DirWatcher:
    def __init__(self, *args, **kwargs):
        self.observer = Observer()
        self.observer.setDaemon(daemonic=True)
        self.event_handler = DirEventProcessor()
        
        # an observer watch object is returned by self.observer.schedule method,
        # obs-watch_and_paths object maps a path, and it's corresponding observer-watch object
        # obs-watch_and_paths[path] = observer-watch object
        self.obswatch_and_paths = {}
        #
        
        self.run()

    def run(self):
        # self.observer.schedule(self.event_handler, self.project_path, recursive=True)
        self.observer.start()
        # self.observer.join()

    def schedule(self, path, append=True):
        if not append:
            self.observer.unschedule_all()
        obswatch_object = self.observer.schedule(self.event_handler, path, recursive=True)
        
        self.obswatch_and_paths[path] = obswatch_object
        
    def unschedule(self, path):
        obswatch_object = self.obswatch_and_paths[path]
        self.observer.unschedule(obswatch_object)
        del self.obswatch_and_paths[path]
