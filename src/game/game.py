import panda3d.core as p3d
from game.scene import Scene

# some static globals constants
DEFAULT_UPDATE_TASK_SORT_VALUE = 2  # default sort value for a UserModule or
                                    # Component regular UpdateTask


class Game:
    """Game is entry point to what will go into your final build"""
 
    def __init__(self, demon):
        self.__demon = demon
        self.__is_editor = False

        self.__render = None    # individual scene renders should be
        self.__render2d = None  # re-parented render and render2d

        self.__dr = None
        self.__dr2d = None  

        self.__mouse_watcher = None

        self.__runtime_scripts = {}  # loaded runtime scripts
        self.__components = {}

        self.__scenes = []           # all scenes in this game
        self.__active_scene = None

    def init(self):        
        # ------------------------------------
        # 3d and 2d rendering setup
        self.__render = p3d.NodePath("GameRender")
        
        self.__render2d = p3d.NodePath("GameRender2d")        
        self.__render2d.setDepthTest(0)
        self.__render2d.setDepthWrite(0)
        self.__render2d.setMaterialOff(1)
        self.__render2d.setTwoSided(1)
        
        # display region
        self.create_dr3d()
        self.create_dr2d()
        
        self.create_mouse_watcher_3d()
        self.__mouse_watcher.node().setDisplayRegion(self.__dr2d)
        
        # -----------------------------------------------------------
        # finally, start the game update task
        # finally, start the level editor update
        task = p3d.PythonTask(self.on_update, "GameUpdate")
        p3d.AsyncTaskManager.getGlobalPtr().add(task)
        
        print("-- Game init successfully")
        
    def on_update(self, task):
        self.__active_scene.update()
        return task.cont
        
    def create_dr2d(self):
        self.__dr2d = self.__demon.engine.win.makeDisplayRegion(0, 0.4, 0, 0.35)
        self.__dr2d.setClearDepthActive(False)
        self.__dr2d.setSort(20)
        self.__dr2d.setActive(True)

    def create_dr3d(self):
        self.__dr = self.__demon.engine.win.makeDisplayRegion(0, 0.4, 0, 0.35)
        self.__dr.setSort(10)
        self.__dr.setClearColorActive(True)
        self.__dr.setClearDepthActive(True)
        self.__dr.setClearColor((0.65, 0.65, 0.65, 1.0))
        
    def create_mouse_watcher_3d(self):
        mk = self.__demon.engine.mw.getParent()
        mouse_watcher = p3d.MouseWatcher()
        mouse_watcher = mk.attachNewNode(mouse_watcher)
        self.__mouse_watcher = mouse_watcher
        
        # see https://docs.panda3d.org/1.10/python/reference/panda3d.core.PGMouseWatcherBackground
        # for explanation on this
        self.__mouse_watcher.node().addRegion(p3d.PGMouseWatcherBackground())

    def clear_active_dr_3d(self):
        self.__dr.setActive(False)
        self.__dr.setCamera(p3d_core.NodePath())
        
    def add_new_scene(self, name: str):
        """creates a new scene, the active should be first cleared by
         the level editor"""
         
        # remove current scene
        if self.__active_scene:
            self.remove_scene(self.__active_scene)
         
        scene = Scene(self, name)
        self.__active_scene = scene
        self.__scenes.append(scene)
        print("-- New scene created successfully")
        return scene
    
    def save_scene(self):
        pass
    
    def remove_scene(self, scene):
        if not isinstance(scene, Scene):
            print("[Game.py] Unbale to remove scene, scene must be instance" +
                  "of Scene!")
            return

        print("Scene removed")

    def set_runtime_scripts(self, scripts):
        pass
        
    def set_components(self, components):
        pass

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

    def print_modules_sort_orders(self):
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
        self.__active_scene.on_resize_event()

    @property
    def demon(self):
        return self.__demon

    @property
    def dr(self):
        return self.__dr

    @property
    def dr2d(self):
        return self.__dr2d

    @property
    def active_scene(self):
        return self.__active_scene
    
    @property
    def mouse_watcher(self):
        return self.__mouse_watcher

    @property
    def render(self):
        return self.__render
    
    @property
    def render2d(self):
        return self.__render2d
