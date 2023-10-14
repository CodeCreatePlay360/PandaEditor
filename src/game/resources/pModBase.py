import game.constants as constants

from direct.showbase.DirectObject import DirectObject
from panda3d.core import LVecBase2f, LPoint2f, LVecBase3f, LPoint3f
from commons import EditorProperty
from commons import ed_logging
from editor.globals import editor


def execute(*args, **kwargs):
    foo = args[len(args) - 1]
    args = args[:len(args) - 1]

    try:
        foo(*args, **kwargs)
    except Exception as exception:
        ed_logging.log_exception(exception)


def stop_execution(module):
    if module.module_type == constants.EditorPlugin:
        editor.observer.trigger("PluginFailed", module)
    else:
        editor.observer.trigger("SwitchEdState", 0)


class PModBase(DirectObject):
    def __init__(self, *args, **kwargs):
        DirectObject.__init__(self)

        # these fields are defined here for convenience only,
        # also defined in project.game as well.
        self.__module_name = kwargs.pop("name", None)
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
        self.__non_serialized_attrs = []

    def accept(self, event, method, extra_args: list = None):
        if extra_args is None:
            extra_args = []
        if type(extra_args) is not list:
            print("unable to accept event {0} from {1} argument extra_args must be of type list".format(
                event, self.__module_name))
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
                self.on_start()
                self.__started = True
            else:
                self.__started = False

            # start the object's update loop
            if not self.is_running(0):
                self.__task = taskMgr.add(self.update,
                                          "{0} Update".format(self.__module_name),
                                          sort=self.__sort,
                                          priority=priority)

            # start the object's late update loop
            if (self.module_type == constants.RuntimeModule or self.module_type == constants.Component) and\
                    not self.is_running(1):
                self.__late_task = taskMgr.add(self.late_update,
                                               "{0} LateUpdate".format(self.__module_name),
                                               sort=self.__late_update_sort,
                                               priority=None)

        try:
            _start()
            return True
        except Exception as exception:
            ed_logging.log_exception(exception)
            stop_execution(self)
            return False

    def on_start(self):
        pass

    def update(self, task):
        if self.__active:
            # check for case when module is active but not yet started,
            # this can happen if module was inactive during editor state but later activated in game state
            if not self.__started:
                try:
                    self.on_start()
                    self.__started = True
                except Exception as exception:
                    ed_logging.log_exception(exception)
                    stop_execution(self)

            if self.__started:
                try:
                    self.on_update()
                    return task.cont
                except Exception as exception:
                    stop_execution(self)
                    ed_logging.log_exception(exception)

        else:
            return task.cont

    def on_update(self):
        pass

    def late_update(self, task):
        if self.__active:
            try:
                self.on_late_update()
                return task.cont
            except Exception as exception:
                stop_execution(self)
                ed_logging.log_exception(exception)

        else:
            return task.cont

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

    def add_property(self, prop: EditorProperty.Property):
        """manually adds a property"""
        if not self.__user_properties.__contains__(prop) and isinstance(prop, EditorProperty.Property):
            self.__user_properties.append(prop)

    def get_active_status(self):
        return self.__active

    def get_serializable_attrs(self):
        attrs = []
        for name, val in self.__dict__.items():
            if self.is_serializable_attr(name, val):
                attrs.append((name, val))

        return attrs

    def get_properties(self):
        self.__properties = []
        for name, value in self.get_serializable_attrs():
            try:
                prop = EditorProperty.ObjProperty(name=name, initial_value=value, type_=type(value), obj=self)
                self.__properties.append(prop)
            except Exception as e:
                print("Error: Unable to add property {0}".format(name))
                print(e)

        properties_pre = []
        properties_post = []
        for property_ in self.__user_properties:
            if property_.draw_idx == -1:
                properties_pre.append(property_)
            else:
                properties_post.append(property_)

        # self.__properties.extend(self.__user_properties)
        self.__properties = properties_pre + self.__properties + properties_post
        return self.__properties

    def set_active(self, val):
        self.__active = val

    def is_serializable_attr(self, name, val):
        if name == "_PModBase__active":
            # this attribute should be saved otherwise active status would have to be manually set after
            # every editor reload
            pass

        if name[0] == "_" or hasattr(PModBase("", None), name):
            return False

        if not isinstance(val, (int, float, str, bool, LVecBase2f, LPoint2f, LVecBase3f, LPoint3f)):
            return False

        return True

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
    def non_serialized_attrs(self):
        return self.__non_serialized_attrs

    @property
    def module_name(self):
        return self.__module_name

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
    def module_type(self):
        return self.__module_type

    @hidden_attrs.setter
    def hidden_attrs(self, attr: str):
        if not isinstance(attr, str):
            print("{0}: Unable to set attribute {1} as hidden, value must be of type string".
                  format(self.__module_name, attr))
            return
        if hasattr(self, attr) and not self.__hidden_attributes.__contains__(attr):
            self.__hidden_attributes.append(attr)

    @non_serialized_attrs.setter
    def non_serialized_attrs(self, attr: str):
        if not isinstance(attr, str):
            print("{0}: Unable to set attribute {1} as discarded, value must be of type string".
                  format(self.__module_name, attr))
            return
        if hasattr(self, attr) and not self.__non_serialized_attrs.__contains__(attr):
            self.__non_serialized_attrs.append(attr)

    @module_type.setter
    def module_type(self, val):
        self.__module_type = val
