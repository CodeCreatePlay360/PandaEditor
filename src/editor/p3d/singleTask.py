from editor.p3d.object import Object
from direct.showbase.ShowBase import taskMgr


class SingleTask(Object):
    def __init__(self, name, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)

        self._name = name
        self._task = None
        self._late_task = None
        self._sort = 0

    def Start(self, sort=None, last_update_sort=None, priority=None):
        self.on_start()

        # print("task {0} started sort {1}".format(self._name, self._sort))
        if sort is None:
            sort = self._sort

        # Start the object's task if it hasn't been already
        if not self.IsRunning(0):
            self._task = taskMgr.add(self.Update, "%sUpdate" % self._name, sort=sort,
                                     priority=priority)

        if not self.IsRunning(1):
            self._late_task = taskMgr.add(self.LateUpdate, "%sLateUpdate" % self._name,
                                          sort=last_update_sort, priority=None)

    def Update(self, task):
        """Run on_update method - return task.cont if there was no return value"""
        self.on_update()
        return task.cont

    def LateUpdate(self, task):
        self.on_late_update()
        return task.cont

    def Stop(self):
        """Remove the object's task from the task manager."""
        if self._task in taskMgr.getAllTasks():
            taskMgr.remove(self._task)
            self._task = None

        if self._late_task in taskMgr.getAllTasks():
            taskMgr.remove(self._late_task)
            self._late_task = None

        self.on_stop()

    def on_start(self):
        """
        Override this function with code to be executed when the object is
        started.
        """
        pass

    def on_update(self):
        """Override this function with code to be executed each frame."""
        pass

    def on_late_update(self):
        pass

    def on_stop(self):
        """
        Override this function with code to be executed when the object is
        stopped.
        """
        pass

    def IsRunning(self, task=0):
        """
        Return True if the object's task can be found in the task manager,
        False otherwise.
        """
        if task == 0:
            return self._task in taskMgr.getAllTasks()

        elif task == 1:
            return self._late_task in taskMgr.getAllTasks()

        return False

    def get_name(self):
        return self._name

    def set_sort(self, val: int):
        self._sort = val

    def get_sort(self):
        return self._sort
