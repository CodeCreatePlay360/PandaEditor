import panda3d.core as p3d_core
from game.scene import Scene
from panda3d.core import WindowProperties


class Game:
    """Game is entry point to what will go into your final build"""

    def __init__(self, *args, **kwargs):
        # global data for whole game
        # TODO game should init its own systems

        self.show_base = kwargs.pop("show_base", None)
        self.win = kwargs.pop("win", None)
        self.display_region = kwargs.pop("dr", None)  # TODO should be created here
        self.display_region_2d = None
        self.mouse_watcher_node = None
        self.mouse_watcher_node_2d = None

        self.render = kwargs.pop("render", None)  # top level game render, individual
                                                  # scene renders should be re-parented to this.

        self.setup_2d_display_region()
        self.set_2d_mouse_watcher()
        self.mouse_watcher_node_2d.set_display_region(self.display_region_2d)

        self.setup_3d_display_region()
        self.setup_3d_mouse_watcher()
        self.mouse_watcher_node.set_display_region(self.display_region)

        self.game_modules = {}  # current loaded user modules
        self.scenes = []        # all scenes in this game
        self.active_scene = None

    def clear_active_3d_display_region(self):
        self.display_region.setActive(False)
        self.display_region.setCamera(p3d_core.NodePath())

    def create_new_scene(self, name: str):
        """creates a new scene, the active should be first cleared by the level editor"""
        scene = Scene(self, name)
        self.active_scene = scene
        self.scenes.append(scene)
        return scene

    def get_module(self, module_name):
        if self.game_modules.__contains__(module_name):
            if not self.game_modules[module_name].class_instance._error:
                return self.game_modules[module_name].class_instance
        return None

    def start(self):
        # classify all modules according to task sort values
        # mod_exec_order[sort_value] = [mod1, mod2,....]
        mod_exec_order = {}
        for key in self.game_modules:
            mod = self.game_modules[key]

            sort_value = mod.class_instance._sort

            if mod_exec_order.__contains__(sort_value):
                mod_exec_order[sort_value].append(mod)
            else:
                mod_exec_order[sort_value] = []
                mod_exec_order[sort_value].append(mod)

        def _start(j, _late_update_sort):
            for _mod in mod_exec_order[j]:
                cls_instance = _mod.class_instance

                if not cls_instance._enabled:
                    return

                _mod.save_data()

                # start module's update
                _res = cls_instance.start(late_update_sort=_late_update_sort)
                if not _res:
                    return False
                # print("[Game] Started", _mod.class_instance._name)

            return True

        # copy modules execution sort orders as an int list
        lst = [*mod_exec_order.keys()]

        if len(lst) == 0:
            return

        # sort modules execution order in ascending order
        lst.sort()

        # late updates are to be executed after all updates have been executed
        # the sort order of all updates should be set in a way, that messenger executes them after updates
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
            module.class_instance.clear_ui()
            module.reload_data()
            self.hide_cursor(False)

    def hide_cursor(self, value: bool):
        if type(value) is bool:
            wp = WindowProperties()
            wp.setCursorHidden(value)
            self.win.requestProperties(wp)

    def set_mouse_mode(self, mode):
        pass

    def setup_2d_display_region(self):
        self.display_region_2d = self.win.makeDisplayRegion()
        self.display_region_2d.setSort(20)
        self.display_region_2d.setActive(True)
        self.display_region_2d.set_dimensions((0, 0.4, 0, 0.4))

    def set_2d_mouse_watcher(self):
        self.mouse_watcher_node_2d = p3d_core.MouseWatcher()
        self.show_base.mouseWatcher.get_parent().attachNewNode(self.mouse_watcher_node_2d)

    def setup_3d_display_region(self):
        pass

    def setup_3d_mouse_watcher(self):
        self.mouse_watcher_node = p3d_core.MouseWatcher()
        self.show_base.mouseWatcher.get_parent().attachNewNode(self.mouse_watcher_node)

    def set_3d_display_region_active(self, cam):
        self.display_region.set_active(True)
        self.display_region.set_camera(cam)
