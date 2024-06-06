from panda3d.core import AsyncTaskManager, PythonTask
from system import Systems


class SingleTask(object):
    def __init__(self, name):
        object.__init__(self)

        self.__name = name
        self.__task = None
        self.__sort = 0

    def start(self, sort=None):
        self.on_start()

        if sort is None:
            sort = self.__sort

        # start the object's task if it hasn't been already
        if not self.is_running():
            task_label = name="%s-Update" % self.__name
            
            self.__task = PythonTask(self.update, task_label)
            self.__task.set_sort(sort)
            AsyncTaskManager.getGlobalPtr().add(self.__task)

    def update(self, task):
        """Run on_update method - return task.cont if there was no return value"""
        try:
            self.on_update()
        except Exception as exception:
            print(exception)
            Systems.game.stop()

        return task.DS_cont

    def stop(self):
        """Remove the object's task from the task manager."""
        
        if self.__task in AsyncTaskManager.getGlobalPtr().getActiveTasks():
            AsyncTaskManager.getGlobalPtr().remove(self.__task)
            self.__task = None
                
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

    def on_stop(self):
        """
        Override this function with code to be executed when the object is
        stopped.
        """
        pass

    def is_running(self):
        """
        Return True if the object's task can be found in the task manager,
        False otherwise.
        """
        
        task_mgr = AsyncTaskManager.getGlobalPtr()
        return self.__task in task_mgr.getActiveTasks()
    
    def set_sort(self, val):
        self.__sort = val
    
    def sort(self):
        return self.__sort
    
    @property
    def name(self):
        return self.__name
