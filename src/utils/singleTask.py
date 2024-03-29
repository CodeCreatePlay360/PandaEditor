from panda3d.core import AsyncTaskManager, PythonTask


class SingleTask(object):
    def __init__(self, name, *args, **kwargs):
        object.__init__(self)

        self.__name = name
        self.__task = None
        self.__late_task = None
        self.__sort = 0

    def start(self, sort=None, late_update_sort=None, *args, **kwargs):
        self.on_start()

        # print("task {0} started sort {1}".format(self._name, self.__sort))
        if sort is None:
            sort = self.__sort

        # Start the object's task if it hasn't been already
        if not self.is_running(0):
            self.__task = PythonTask(self.update,
                                     name="%s-Update" % self.__name)
                                     
            self.__task.set_sort(sort)
            
            AsyncTaskManager.getGlobalPtr().add(self.__task)

        if not self.is_running(1):
            self.__late_task = PythonTask(self.late_update,
                                          name="%s-LateUpdate" % self.__name)
            
            if late_update_sort:
                self.__late_task.set_sort(late_update_sort)
            
            AsyncTaskManager.getGlobalPtr().add(self.__late_task)

    def update(self, task):
        
        """Run on_update method - return task.cont if there was no return value"""
        self.on_update()
        return task.DS_cont

    def late_update(self, task):
        self.on_late_update()
        return task.DS_cont

    def stop(self):
        """Remove the object's task from the task manager."""
        
        if self.__task in AsyncTaskManager.getGlobalPtr().getActiveTasks():
            AsyncTaskManager.getGlobalPtr().remove(self.__task)
            self.__task = None
        
        if self.__late_task in AsyncTaskManager.getGlobalPtr().getActiveTasks():
            AsyncTaskManager.getGlobalPtr().remove(self.__late_task)
            self.__late_task = None
        
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

    def is_running(self, task=0):
        """
        Return True if the object's task can be found in the task manager,
        False otherwise.
        """
        
        if task == 0:
            return self.__task in AsyncTaskManager.getGlobalPtr().getActiveTasks()
        elif task == 1:
            return self.__late_task in AsyncTaskManager.getGlobalPtr().getActiveTasks()

        return False
    
    @property
    def name(self):
        return self.__name
