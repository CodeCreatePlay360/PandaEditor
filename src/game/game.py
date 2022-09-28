import panda3d.core as p3d_core
from game.scene import Scene
from panda3d.core import WindowProperties

# some static globals constants
TAG_GAME_OBJECT = "GameObject"  # global tag for all nodepaths in scenegraph
DEFAULT_UPDATE_TASK_SORT_VALUE = 2  # default sort value for a UserModule or Component regular UpdateTask


class Game:
    """Game is entry point to what will go into your final build"""

    def __init__(self, *args, **kwargs):
        # global data for whole game
        # TODO game should init its own systems

        self.show_base = kwargs.pop("show_base", None)
        self.win = kwargs.pop("win", None)
        self.display_region = None
        self.display_region_2d = None
        self.mouse_watcher_node = None
        self.mouse_watcher_node_2d = None

        self.render = kwargs.pop("render", None)  # top level game render, individual
                                                  # scene renders should be re-parented to this.

        self.setup_dr_2d()
        self.setup_mouse_watcher_2d()

        self.setup_dr_3d()
        self.setup_mouse_watcher_3d()

        self.game_modules = {}  # current loaded user modules
        self.scenes = []        # all scenes in this game
        self.active_scene = None

    def create_new_scene(self, name: str):
        """creates a new scene, the active should be first cleared by the level editor"""
        scene = Scene(self, name)
        self.active_scene = scene
        self.scenes.append(scene)
        return scene

    def clear_active_dr_3d(self):
        self.display_region.setActive(False)
        self.display_region.setCamera(p3d_core.NodePath())

    def get_module(self, module_name):
        if self.game_modules.__contains__(module_name):
            return self.game_modules[module_name].class_instance
        return None

    def start(self):
        # classify all modules according to task sort values
        # mod_exec_order[sort_value] = [mod1, mod2,....]
        mod_exec_order = {}
        for key in self.game_modules:
            mod = self.game_modules[key]

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
        for key in self.game_modules:
            module = self.game_modules[key]

            module.class_instance.ignore_all()
            module.class_instance.stop()
            # module.class_instance.clear_ui()
            module.reload_data()
            self.hide_cursor(False)

        for np in self.active_scene.render_2d.getChildren():
            if np.get_name() == "__aspect_2d__" or np.get_name() == "Camera2d":
                pass
            else:
                np.remove_node()

        for np in self.active_scene.aspect_2d.getChildren():
            np.remove_node()

    def hide_cursor(self, value: bool):
        if type(value) is bool:
            wp = WindowProperties()
            wp.setCursorHidden(value)
            self.win.requestProperties(wp)

    def set_mouse_mode(self, mode):
        pass

    def setup_dr_2d(self):
        self.display_region_2d = self.win.makeDisplayRegion()
        self.display_region_2d.setSort(20)
        self.display_region_2d.setActive(True)
        self.display_region_2d.set_dimensions((0, 0.4, 0, 0.4))

    def setup_mouse_watcher_2d(self):
        self.mouse_watcher_node_2d = p3d_core.MouseWatcher()
        self.show_base.mouseWatcher.get_parent().attachNewNode(self.mouse_watcher_node_2d)
        self.mouse_watcher_node_2d.set_display_region(self.display_region_2d)

    def setup_dr_3d(self):
        self.display_region = self.win.makeDisplayRegion(0, 0.4, 0, 0.4)
        self.display_region.setClearColorActive(True)
        self.display_region.setClearColor((0.8, 0.8, 0.8, 1.0))

    def setup_mouse_watcher_3d(self):
        self.mouse_watcher_node = p3d_core.MouseWatcher()
        self.show_base.mouseWatcher.get_parent().attachNewNode(self.mouse_watcher_node)
        self.mouse_watcher_node.set_display_region(self.display_region)

    def set_active_cam(self, cam):
        self.display_region.set_active(True)
        self.display_region.set_camera(cam)
        cam.node().getLens().setAspectRatio(self.show_base.getAspectRatio(self.win))

    def resize_event(self):
        """should be called after a window has been resized"""
        if self.active_scene.main_camera:
            self.active_scene.main_camera.node().getLens().setAspectRatio(self.show_base.getAspectRatio(self.win))

        self.active_scene.aspect_2d.set_scale(1.0 / self.show_base.getAspectRatio(self.win), 1.0, 1.0)
