import panda3d.core as p3d

from panda3d.core import WindowProperties
from game.scene import Scene

# some static globals constants
DEFAULT_UPDATE_TASK_SORT_VALUE = 2  # default sort value for a UserModule or
                                    # Component regular UpdateTask


class Game:
    """Game is entry point to what will go into your final build"""

    def __init__(self, proj_path, demon):
        self.__demon = demon
        self.__path = proj_path
        self.__is_editor = False

        # top level game render, individual scene renders should be
        # re-parented to this.
        self.__render = self.__demon.engine.render  

        self.__dr = None
        self.__dr_2D = None

        # create a new main camera for game world and a lens for it
        self.__main_cam = p3d.NodePath(p3d.Camera("MainCamera"))
        self.__main_cam.reparent_to(self.__render)

        lens = p3d.PerspectiveLens()
        lens.set_fov(60)
        lens.setAspectRatio(800 / 600)
        self.__main_cam.node().setLens(lens)
        
        self.setup_dr_2D()
        self.setup_dr_3D()
        
        self.set_active_cam(self.__main_cam)

        self.__runtime_modules = {}  # loaded runtime modules
        self.__all_modules = {}      # runtime modules + components
        self.__scenes = []           # all scenes in this game
        self.__active_scene = None
        
        # finally, start the game update task
        # finally, start the level editor update
        task = p3d.PythonTask(self.on_update, "GameUpdate")
        p3d.AsyncTaskManager.getGlobalPtr().add(task)
        
    def on_update(self, task):
        self.__active_scene.update()
        return task.cont
        
    def add_new_scene(self, name: str):
        """creates a new scene, the active should be first cleared by
         the level editor"""
         
        # remove current scene
        if self.__active_scene:
            self.remove_scene(self.__active_scene)
         
        scene = Scene(self, name)
        self.__active_scene = scene
        self.__scenes.append(scene)
        return scene
    
    def save_scene(self):
        pass
    
    def remove_scene(self, scene):
        if not isinstance(scene, Scene):
            print("[Game.py] Unbale to remove scene, scene must be instance" +
                  "of Scene!")
            return

        print("Scene removed")

    def clear_active_dr_3d(self):
        self.__dr.setActive(False)
        self.__dr.setCamera(p3d_core.NodePath())

    def start(self):
        self.__all_modules = {}
        # get all runtime modules
        for key, value in self.__runtime_modules.items():
            self.__all_modules[key] = value

        # get all components
        components = self.components
        for np in components.keys():
            for component in components[np]:
                self.__all_modules[component.path+component.class_instance.getPythonTag("__GAME_OBJECT__").uid] =\
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
            module.reload_data(remove_differences=True)

            self.hide_cursor(False)

        for np in self.__active_scene.render_2D.getChildren():
            if np.get_name() == "__aspect_2D__" or np.get_name() == "__camera2D__":
                pass
            else:
                np.remove_node()

        for np in self.__active_scene.aspect_2D.getChildren():
            np.remove_node()

        self.__all_modules.clear()

    def setup_dr_2D(self):
        self.__dr_2D = self.__demon.engine.win.makeDisplayRegion()
        self.__dr_2D.setSort(2)
        self.__dr_2D.setActive(True)
        self.__dr_2D.set_dimensions((0, 0.4, 0, 0.35))

    def setup_dr_3D(self):
        self.__dr = self.__demon.engine.win.makeDisplayRegion(0, 0.4, 0, 0.35)
        self.__dr.setSort(1)
        self.__dr.setClearColorActive(True)
        self.__dr.setClearDepthActive(True)
        self.__dr.setClearColor((0.65, 0.65, 0.65, 1.0))

    def set_active_cam(self, cam):
        self.__dr.set_active(True)
        self.__dr.set_camera(cam)
        cam.node().getLens().setAspectRatio(self.__demon.engine.aspect_ratio)
        self.__main_cam = cam

    def set_runtime_modules(self, modules: dict):
        self.__runtime_modules = modules

    def get_module(self, module_path: str):
        for key in self.__runtime_modules.keys():
            if key == module_path:
                return self.__runtime_modules[key].class_instance
        return None

    def get_all_modules(self):
        """returns all runtime user modules including NodePaths as list"""

        modules = []

        # append all runtime modules
        for path in self.__runtime_modules:
            modules.append(self.__runtime_modules[path].class_instance)

        # append all np-components
        for np in self.components:
            for comp in self.components[np]:
                modules.append(comp.class_instance)

        return modules

    def user_modules_sort_orders(self):
        all_modules = self.get_all_modules()
        for mod in all_modules:
            if isinstance(mod, Component):
                print("[Module] {0} -- [Sort] {1}".format(mod.get_name(), mod.sort))
            else:
                print("[Module] {0} -- [Sort] {1}".format(mod.name, mod.sort))

    def is_runtime_module(self, path):
        if self.__runtime_modules.__contains__(path):
            return True
        return False

    def on_resize_event(self):
        """should be called after a window has been resized"""
        
        ar = self.__demon.engine.aspect_ratio
        
        if self.__main_camera:
            self.__main_camera.node().getLens().setAspectRatio(ar)

        self.__aspect_2D.set_scale(1.0 / ar, 1.0, 1.0)

    @property
    def cam(self):
        return self.__main_cam

    @property
    def path(self):
        return self.__path

    @property
    def win(self):
        return self.__demon.engine.win

    @property
    def dr(self):
        return self.__dr

    @property
    def dr_2d(self):
        return self.__dr_2D

    @property
    def demon(self):
        return self.__demon

    @property
    def render(self):
        return self.__render

    @property
    def active_scene(self):
        return self.__active_scene
