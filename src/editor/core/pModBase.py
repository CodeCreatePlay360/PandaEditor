import editor.constants as constant
import editor.utils as ed_utils
from direct.showbase.DirectObject import DirectObject
from panda3d.core import NodePath


def execute(*args, **kwargs):
    foo = args[len(args) - 1]
    args = args[:len(args) - 1]
    ed_utils.try_execute(foo, *args, **kwargs)


def stop_execution(module):
    if module._editor_plugin:
        constant.obs.trigger("PluginFailed", module)
    else:
        constant.obs.trigger("ProjectEvent", "SwitchEdState", 0)


class PModBase(DirectObject):
    def __init__(self, *args, **kwargs):
        DirectObject.__init__(self)

        # these fields are defined here for convenience only,
        # all these fields are defined in project.game as well.
        self._name = kwargs.pop("name", None)
        self._win = kwargs.pop("win", None)
        self._render = kwargs.pop("render", None)
        self._aspect2d = kwargs.pop("aspect2d", None)
        self.dr = kwargs.pop("dr", None)
        self.dr2d = kwargs.pop("dr2d", None)
        self._mouse_watcher_node = kwargs.pop("mouse_watcher_node", None)

        self._task = None
        self._late_task = None
        self._sort = 2  # default sort value for user modules
        self._late_update_sort = -1

        self._enabled = True  # is this module enabled
        self._initialized = True
        self._error = False  # set this to true if there is an error on initialization

        self._properties = []         # auto generated properties for various attributes
        self._user_properties = []    # properties manually added by user
        self._hidden_attributes = []  #

        # to be discarded variables
        # these variables will not be saved
        self._discarded_attrs = [
            "_MSGRmessengerId",

            "_name",
            "_render",
            "_mouse_watcher",
            "_win",

            "_editor_plugin",

            "_task",
            "_late_task",
            "_sort",
            "_late_update_sort",

            "_enabled",
            "_initialized",
            "_error",

            "_properties",
            "_user_properties",
            "_hidden_attributes",

            "_discarded_attrs"]

    def accept(self, event, method, extra_args: list = None):
        if extra_args is None:
            extra_args = []
        if type(extra_args) is not list:
            print("unable to accept event {0} from {1} argument extra_args must be of type list".format(
                event, self._name))
            return

        xx = extra_args.copy()
        xx.append(method)
        super(PModBase, self).accept(event, execute, extraArgs=xx)

    def start(self, sort=None, late_update_sort=None, priority=None):
        if sort:
            self._sort = sort

        if late_update_sort:
            self._late_update_sort = late_update_sort

        def _start():
            self.on_start()

            # start the object's update loop
            if not self.is_running(0):
                self._task = taskMgr.add(self.update,
                                         "{0} Update".format(self._name),
                                         sort=self._sort,
                                         priority=priority)

            # start the object's late update loop
            # self._editor_plugin is generated on the fly do not declare it here
            if not self._editor_plugin and not self.is_running(1):
                self._late_task = taskMgr.add(self.late_update,
                                              "{0} LateUpdate".format(self._name),
                                              sort=self._late_update_sort,
                                              priority=None)

        res = ed_utils.try_execute(_start)
        if not res:
            stop_execution(self)
            return False
        return True

    def on_start(self):
        pass

    def update(self, task):
        res = ed_utils.try_execute(self.on_update)
        if res is True:
            return task.cont
        else:
            stop_execution(self)
            return False

    def on_update(self):
        pass

    def late_update(self, task):
        res = ed_utils.try_execute(self.on_late_update)
        if res is True:
            return task.cont
        else:
            stop_execution(self)
            return False

    def on_late_update(self):
        pass

    def stop(self):
        # remove the object's task from the task manager
        if self._task in taskMgr.getAllTasks():
            taskMgr.remove(self._task)
            self._task = None

        if self._late_task in taskMgr.getAllTasks():
            taskMgr.remove(self._late_task)
            self._late_task = None

        self.on_stop()

    def on_stop(self):
        pass

    def is_running(self, task=0):
        """ Return True if the object's task can be found in the task manager, False otherwise"""

        if task == 0:
            return self._task in taskMgr.getAllTasks()
        elif task == 1:
            return self._late_task in taskMgr.getAllTasks()

        return False

    def add_property(self, prop: ed_utils.EdProperty.Property):
        """manually adds a property"""
        if not self._user_properties.__contains__(prop) and isinstance(prop, ed_utils.EdProperty.Property):
            self._user_properties.append(prop)

    def get_savable_atts(self):
        attrs = []
        for name, val in self.__dict__.items():
            if self._discarded_attrs.__contains__(name) or hasattr(PModBase("", None), name) or type(val) == NodePath:
                continue
            attrs.append((name, val))

        return attrs

    def get_attr(self, attr):
        if attr in self.__dict__.keys():
            return self.__dict__[attr]
        return None

    def get_properties(self):
        self._properties = []

        for name, value in self.get_savable_atts():

            # hidden variables should be ignored
            if name in self._hidden_attributes:
                continue

            # private variables should be ignored
            if name[0] == "_":
                continue

            prop = ed_utils.EdProperty.ObjProperty(name=name, value=value, _type=type(value), obj=self)
            self._properties.append(prop)

        self._properties.extend(self._user_properties)

        return self._properties

    def is_discarded_attr(self, name):
        if name in self._discarded_attrs:
            return True
        return False

    @property
    def hidden_attrs(self):
        return self._hidden_attributes

    @hidden_attrs.setter
    def hidden_attrs(self, attr: str):
        if hasattr(self, attr) and not self._hidden_attributes.__contains__(attr):
            self._hidden_attributes.append(attr)

    @property
    def discarded_attrs(self):
        return self._discarded_attrs

    @discarded_attrs.setter
    def discarded_attrs(self, attr: str):
        if hasattr(self, attr) and not self._discarded_attrs.__contains__(attr):
            self._discarded_attrs.append(attr)

    def has_ed_property(self, name: str):
        for prop in self._properties:
            if prop.name == name:
                return True
        return False

    def on_resize_event(self):
        """this method is called when window is resized"""
        pass
