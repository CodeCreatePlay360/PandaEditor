import editor.constants as constants
import editor.utils as ed_utils
from direct.showbase.DirectObject import DirectObject
from panda3d.core import NodePath


def execute(*args, **kwargs):
    foo = args[len(args) - 1]
    args = args[:len(args) - 1]
    ed_utils.try_execute(foo, *args, **kwargs)


def stop_execution(module):
    if module.module_type == "EditorPlugin":
        constants.obs.trigger("PluginFailed", module)
    else:
        constants.obs.trigger("SwitchEdState", 0)


class PModBase(DirectObject):
    def __init__(self, *args, **kwargs):
        DirectObject.__init__(self)

        # these fields are defined here for convenience only,
        # all these fields are defined in project.game as well.
        self._name = kwargs.pop("name", None)
        self.show_base = kwargs.pop("show_base", None)
        self._win = kwargs.pop("win", None)
        self.dr = kwargs.pop("dr", None)
        self.dr2d = kwargs.pop("dr2d", None)
        self._mouse_watcher_node = kwargs.pop("mouse_watcher_node", None)
        self._render = kwargs.pop("render", None)
        self._render2d = kwargs.pop("render2d", None)
        self._aspect2d = kwargs.pop("aspect2d", None)

        self._task = None
        self._late_task = None
        self._sort = 2  # default sort value for user modules
        self._late_update_sort = -1

        self._active = True  # is this module enabled
        self._started = False
        self._initialized = True
        self._error = False  # set this to true if there is an error on initialization

        self._properties = []  # auto generated properties for various attributes
        self._user_properties = []  # properties manually added by user
        self._hidden_attributes = []  #

        self.module_type = None

        # to be discarded variables
        # these variables will not be saved
        self._discarded_attributes = [
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
            if self._active:
                # on start if module is active
                self.on_start()
                self._started = True
            else:
                self._started = False

            # start the object's update loop
            if not self.is_running(0):
                self._task = taskMgr.add(self.update,
                                         "{0} Update".format(self._name),
                                         sort=self._sort,
                                         priority=priority)

            # start the object's late update loop
            if self.module_type == constants.RuntimeModule and not self.is_running(1):
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
        if self._active:

            # check for case if this module was not active when entering game_state,
            # ---------------------------------------------------------------------
            if not self._started:
                if not ed_utils.try_execute(self.on_start):
                    stop_execution(self)
                    return
                else:
                    self._started = True
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
        if self._active:
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
        if self._task in taskMgr.getAllTasks():
            taskMgr.remove(self._task)
            self._task = None

        if self._late_task in taskMgr.getAllTasks():
            taskMgr.remove(self._late_task)
            self._late_task = None

        self._started = False
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

    def get_active_status(self):
        return self._active

    def get_savable_atts(self):
        attrs = []
        for name, val in self.__dict__.items():
            # print("Object {0} Attribute {1} Value {2}".format(self._name, name, val))
            if self._discarded_attributes.__contains__(name) or hasattr(PModBase("", None), name) or type(val) == NodePath:
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

    def set_active(self, val):
        self._active = val

    def is_discarded_attr(self, name):
        if name in self._discarded_attributes:
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
        return self._discarded_attributes

    @discarded_attrs.setter
    def discarded_attrs(self, attr: str):
        if hasattr(self, attr) and not self._discarded_attributes.__contains__(attr):
            self._discarded_attributes.append(attr)

    def has_ed_property(self, name: str):
        for prop in self._properties:
            if prop.name == name:
                return True
        return False

    def on_resize_event(self):
        """this method is called when window is resized"""
        if self._aspect2d is not None and self.show_base is not None:
            self._aspect2d.set_scale(1.0 / self.show_base.getAspectRatio(self._win), 1.0, 1.0)

    def clear_ui(self):
        """clears all direct gui elements, by default this is executed before unloading editor plugin,
         this method can be called manually as well"""
        for np in self._aspect2d.getChildren():
            np.remove_node()
