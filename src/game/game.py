import panda3d.core as p3d_core
from game.scene import Scene
from panda3d.core import WindowProperties

# some static globals constants
DEFAULT_UPDATE_TASK_SORT_VALUE = 2  # default sort value for a UserModule or Component regular UpdateTask


class Game:
    """Game is entry point to what will go into your final build"""

    def __init__(self, *args, **kwargs):
        # global data for whole game
        # TODO game should init its own systems

        self.show_base = kwargs.pop("show_base", None)
        self.win = kwargs.pop("win", None)
        self.__dr = None
        self.__dr_2D = None
        self.mouse_watcher_node = None
        self.mouse_watcher_node_2d = None

        self.render = kwargs.pop("render", None)  # top level game render, individual
        # scene renders should be re-parented to this.

        self.setup_dr_2d()
        self.setup_mouse_watcher_2d()

        self.setup_dr_3d()
        self.setup_mouse_watcher_3d()

        self.runtime_modules = {}  # loaded runtime modules
        self.__all_modules = {}  # runtime modules + components
        self.scenes = []  # all scenes in this game
        self.active_scene = None

    def create_new_scene(self, name: str):
        """creates a new scene, the active should be first cleared by the level editor"""
        scene = Scene(self, name)
        self.active_scene = scene
        self.scenes.append(scene)
        return scene

    def clear_active_dr_3d(self):
        self.__dr.setActive(False)
        self.__dr.setCamera(p3d_core.NodePath())

    def start(self):
        self.__all_modules = {}
        for key, value in self.runtime_modules.items():
            self.__all_modules[key] = value

        components = self.components
        for np in components.keys():
            for component in components[np]:
                self.__all_modules[component.path+component.class_instance.getPythonTag("__TAG_GAME_OBJECT__").uid] =\
                    component

        # classify all modules according to task sort values
        mod_exec_order = {}  # mod_exec_order[sort_value] = [mod1, mod2,....]

        for key in self.__all_modules:
            mod = self.__all_modules[key]

            sort_value = mod.class_instance.sort

            if mod_exec_order.__contains__(sort_value):
                mod_exec_order[sort_value].append(mod)
            else:
                mod_exec_order[sort_value] = []
                mod_exec_order[sort_value].append(mod)

        def _start(j, _late_update_sort):
            for _mod in mod_exec_order[j]:
                cls_instance = _mod.class_instance
                _mod.save_data()

                # start module's update
                _res = cls_instance.start(late_update_sort=_late_update_sort)
                if not _res:
                    return False
            return True

        # copy modules execution sort orders as an int list
        lst = [*mod_exec_order.keys()]

        if len(lst) == 0:
            return

        # sort modules execution order in ascending order
        lst.sort()

        # late updates are to be executed after all updates have been executed
        # the sort order of all updates should be set in a way, that messenger executes them after all updates
        # TODO proper explanation
        start = lst[0]
        stop = lst[len(lst) - 1]

        late_update_sort = stop + 1

        for i in range(start, stop + 1):
            res = _start(i, late_update_sort)
            if not res:
                break
            late_update_sort += 1

    def stop(self):
        for key in self.__all_modules:
            module = self.__all_modules[key]
            module.class_instance.ignore_all()
            module.class_instance.stop()
            module.reload_data()

            self.hide_cursor(False)

        for np in self.active_scene.render_2d.getChildren():
            if np.get_name() == "__aspect_2d__" or np.get_name() == "Camera2d":
                pass
            else:
                np.remove_node()

        for np in self.active_scene.aspect_2d.getChildren():
            np.remove_node()

        self.__all_modules.clear()

    def hide_cursor(self, value: bool):
        if type(value) is bool:
            wp = WindowProperties()
            wp.setCursorHidden(value)
            self.win.requestProperties(wp)

    def set_mouse_mode(self, mode):
        pass

    def setup_dr_2d(self):
        self.__dr_2D = self.win.makeDisplayRegion()
        self.__dr_2D.setSort(20)
        self.__dr_2D.setActive(True)
        self.__dr_2D.set_dimensions((0, 0.4, 0, 0.4))

    def setup_mouse_watcher_2d(self):
        self.mouse_watcher_node_2d = p3d_core.MouseWatcher()
        self.show_base.mouseWatcher.get_parent().attachNewNode(self.mouse_watcher_node_2d)
        self.mouse_watcher_node_2d.set_display_region(self.__dr_2D)

    def setup_dr_3d(self):
        self.__dr = self.win.makeDisplayRegion(0, 0.4, 0, 0.4)
        self.__dr.setClearColorActive(True)
        self.__dr.setClearColor((0.8, 0.8, 0.8, 1.0))

    def setup_mouse_watcher_3d(self):
        self.mouse_watcher_node = p3d_core.MouseWatcher()
        self.show_base.mouseWatcher.get_parent().attachNewNode(self.mouse_watcher_node)
        self.mouse_watcher_node.set_display_region(self.__dr)

    def set_active_cam(self, cam):
        self.__dr.set_active(True)
        self.__dr.set_camera(cam)
        cam.node().getLens().setAspectRatio(self.show_base.getAspectRatio(self.win))

    def get_module(self, module_name):
        if self.runtime_modules.__contains__(module_name):
            return self.runtime_modules[module_name].class_instance
        return None

    def is_runtime_module(self, path):
        if self.runtime_modules.__contains__(path):
            return True
        return False

    def resize_event(self):
        """should be called after a window has been resized"""
        if self.active_scene.main_camera:
            self.active_scene.main_camera.node().getLens().setAspectRatio(self.show_base.getAspectRatio(self.win))

        self.active_scene.aspect_2d.set_scale(1.0 / self.show_base.getAspectRatio(self.win), 1.0, 1.0)

    @property
    def dr(self):
        return self.__dr

    @property
    def dr_2D(self):
        return self.__dr_2D

    @property
    def components(self):
        components = {}  # np: components

        def traverse(np_):
            np = np_.getPythonTag("__TAG_GAME_OBJECT__")
            if np:
                for path in np.components.keys():
                    if not components.__contains__(np):
                        components[np] = []
                    components[np].append(np.components[path])

            for child in np_.getChildren():
                traverse(child)

        traverse(self.active_scene.render)
        return components
