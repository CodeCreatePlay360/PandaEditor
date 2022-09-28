import editor.constants as constants
import editor.utils as ed_utils
from direct.showbase.DirectObject import DirectObject
from panda3d.core import NodePath
from editor.globals import editor


def execute(*args, **kwargs):
    foo = args[len(args) - 1]
    args = args[:len(args) - 1]
    ed_utils.try_execute(foo, *args, **kwargs)


def stop_execution(module):
    if module.type == "EditorPlugin":
        editor.observer.trigger("PluginFailed", module)
    else:
        editor.observer.trigger("SwitchEdState", 0)


class PModBase(DirectObject):
    def __init__(self, *args, **kwargs):
        DirectObject.__init__(self)

        # these fields are defined here for convenience only,
        # also defined in project.game as well.
        self.__name = kwargs.pop("name", None)
        self.__show_base = kwargs.pop("show_base", None)
        self.__win = kwargs.pop("win", None)
        self.__dr = kwargs.pop("dr", None)
        self.__dr2d = kwargs.pop("dr2d", None)
        self.__mouse_watcher_node = kwargs.pop("mouse_watcher_node", None)
        self.__render = kwargs.pop("render", None)
        self.__render2d = kwargs.pop("render2d", None)
        self.__aspect2d = kwargs.pop("aspect2d", None)

        self.__path = kwargs.pop("path", None)

        self.__task = None
        self.__late_task = None
        self.__sort = 2  # default sort value for user modules
        self.__late_update_sort = -1

        self.__active = True  # is this module enabled
        self.__started = False
        self.__initialized = True

        self.__properties = []  # auto generated properties for various attributes
        self.__user_properties = []  # properties manually added by user
        self.__hidden_attributes = []  #

        self.__user_commands = []

        self.__module_type = None

        # to be discarded variables
        # these variables will not be saved
        self.__discarded_attributes = [
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

            "_active",
            "_initialized",
            "_error",

            "_properties",
            "_user_properties",
            "_hidden_attributes",

            "module_type",

            "_discarded_attrs"]

    def accept(self, event, method, extra_args: list = None):
        if extra_args is None:
            extra_args = []
        if type(extra_args) is not list:
            print("unable to accept event {0} from {1} argument extra_args must be of type list".format(
                event, self.__name))
            return

        xx = extra_args.copy()
        xx.append(method)
        super(PModBase, self).accept(event, execute, extraArgs=xx)

    def start(self, sort=None, late_update_sort=None, priority=None):
        if sort:
            self.__sort = sort

        if late_update_sort:
            self.__late_update_sort = late_update_sort

        def _start():
            if self.__active:
                # on start if module is active
                self.on_start()
                self.__started = True
            else:
                self.__started = False

            # start the object's update loop
            if not self.is_running(0):
                self.__task = taskMgr.add(self.update,
                                          "{0} Update".format(self.__name),
                                          sort=self.__sort,
                                          priority=priority)

            # start the object's late update loop
            if self.type == constants.RuntimeModule and not self.is_running(1):
                self.__late_task = taskMgr.add(self.late_update,
                                               "{0} LateUpdate".format(self.__name),
                                               sort=self.__late_update_sort,
                                               priority=None)

        res = ed_utils.try_execute(_start)
        if not res:
            stop_execution(self)
            return False
        return True

    def on_start(self):
        pass

    def update(self, task):
        if self.__active:

            # check for case if this module was not active when entering game_state,
            # ---------------------------------------------------------------------
            if not self.__started:
                if not ed_utils.try_execute(self.on_start):
                    stop_execution(self)
                    return
                else:
                    self.__started = True
            # ---------------------------------------------------------------------

            res = ed_utils.try_execute(self.on_update)
        else:
            res = True

        if res is True:
            return task.cont
        else:
            stop_execution(self)
            return False

    def on_update(self):
        pass

    def late_update(self, task):
        if self.__active:
            res = ed_utils.try_execute(self.on_late_update)
        else:
            res = True

        if res is True:
            return task.cont
        else:
            stop_execution(self)
            return False

    def on_late_update(self):
        pass

    def stop(self):
        # remove the object's task from the task manager
        if self.__task in taskMgr.getAllTasks():
            taskMgr.remove(self.__task)
            self.__task = None

        if self.__late_task in taskMgr.getAllTasks():
            taskMgr.remove(self.__late_task)
            self.__late_task = None

        self.__started = False
        self.on_stop()

    def on_stop(self):
        pass

    def is_running(self, task=0):
        """ Return True if the object's task can be found in the task manager, False otherwise"""

        if task == 0:
            return self.__task in taskMgr.getAllTasks()
        elif task == 1:
            return self.__late_task in taskMgr.getAllTasks()

        return False

    def add_property(self, prop: ed_utils.EdProperty.Property):
        """manually adds a property"""
        if not self.__user_properties.__contains__(prop) and isinstance(prop, ed_utils.EdProperty.Property):
            self.__user_properties.append(prop)

    def get_active_status(self):
        return self.__active

    def get_savable_atts(self):
        attrs = []
        for name, val in self.__dict__.items():
            if self.__discarded_attributes.__contains__(name) or hasattr(PModBase("", None), name):
                # print("discarded attr name: {0}".format(name))
                continue
            # print("[{0}] Saved attribute name: {1} val: {2}".format(self.name, name, val))
            attrs.append((name, val))

        return attrs

    def get_attr(self, attr):
        if attr in self.__dict__.keys():
            return self.__dict__[attr]
        return None

    def get_properties(self):
        self.__properties = []
        for name, value in self.get_savable_atts():

            # hidden variables should be ignored
            if name in self.__hidden_attributes:
                continue

            # private variables should be ignored
            if name[0] == "_":
                continue
            try:
                prop = ed_utils.EdProperty.ObjProperty(name=name, value=value, type_=type(value), obj=self)
                self.__properties.append(prop)
            except Exception as e:
                print("Error: Unable to add property {0}".format(name))
                print(e)

        self.__properties.extend(self.__user_properties)
        return self.__properties

    def set_active(self, val):
        self.__active = val

    def is_discarded_attr(self, name):
        if name in self.__discarded_attributes:
            return True
        return False

    def has_ed_property(self, name: str):
        for prop in self.__properties:
            if prop.name == name:
                return True
        return False

    def on_resize_event(self):
        """this method is called when window is resized"""
        pass

    @property
    def hidden_attrs(self):
        return self.__hidden_attributes

    @property
    def discarded_attrs(self):
        return self.__discarded_attributes

    @property
    def name(self):
        return self.__name

    @property
    def show_base(self):
        return self.__show_base

    @property
    def win(self):
        return self.__win

    @property
    def dr(self):
        return self.__dr

    @property
    def dr2d(self):
        return self.__dr2d

    @property
    def mouse_watcher_node(self):
        return self.__mouse_watcher_node

    @property
    def render(self):
        return self.__render

    @property
    def render2d(self):
        return self.__render2d

    @property
    def aspect2d(self):
        return self.__aspect2d

    @property
    def path(self):
        return self.__path

    @property
    def task(self):
        return self.__task

    @property
    def late_task(self):
        return self.__late_task

    @property
    def sort(self):
        return self.__sort

    @property
    def late_update_sort(self):
        return self.__late_update_sort

    @property
    def active(self):
        return self.__active

    @property
    def started(self):
        return self.__started

    @property
    def initialized(self):
        return self.__initialized

    @property
    def properties(self):
        return self.__properties

    @property
    def user_properties(self):
        return self.__user_properties

    @property
    def hidden_attributes(self):
        return self.__hidden_attributes

    @property
    def type(self):
        return self.__module_type

    @hidden_attrs.setter
    def hidden_attrs(self, attr: str):
        if not isinstance(attr, str):
            print("{0}: Unable to set attribute {1} as hidden, value must be of type string".format(self.name, attr))
            return
        if hasattr(self, attr) and not self.__hidden_attributes.__contains__(attr):
            self.__hidden_attributes.append(attr)

    @discarded_attrs.setter
    def discarded_attrs(self, attr: str):
        if not isinstance(attr, str):
            print("{0}: Unable to set attribute {1} as discarded, value must be of type string".format(self.name, attr))
            return
        if hasattr(self, attr) and not self.__discarded_attributes.__contains__(attr):
            self.__discarded_attributes.append(attr)

    @type.setter
    def type(self, val):
        self.__module_type = val
