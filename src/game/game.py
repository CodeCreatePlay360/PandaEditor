import panda3d.core as p3d
from os import path as ospath
from game.scene import Scene


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
        self.__components = {}       # path: component
        self.__attached_comps = {}   # comp: list component instances

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
        """creates a new scene"""
         
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
        
    def attach_component(self, np, comp_path):        
        if self.__attached_comps.__contains__(np):
            # check if component already attached
            for comp in self.__attached_comps[np]:
                if comp.path() == comp_path:
                    print("Component already exists")
                    return
        else:
            self.__attached_comps[np] = []
            
        # init the component and 
        # get name from path
        head, tail = ospath.split(comp_path)
        comp_name = tail.split(".")[0]  # name
        
        comp = self.__components[comp_path]
        instance = comp(comp_path, comp_name, np)
        self.__attached_comps[np].append(instance)
        
    def set_runtime_scripts(self, scripts):
        self.__runtime_scripts.clear()
        self.__runtime_scripts = {**scripts}
    
    def set_components(self, comps):
        self.__components.clear()
        self.__components = {**comps}

    def start(self):
        __all_modules = {**self.__runtime_scripts, **self.__attached_comps}
        
        # classify all scripts according to their respective task sort values
        # so that they are started in right order.
        scripts_exec_order = {}  # [sort_value] = [script1, ....]
        
        # sort runtime scripts
        for key, value in self.__runtime_scripts.items():
            if not scripts_exec_order.__contains__(value.sort()):
                scripts_exec_order[value.sort()] = []
                
            scripts_exec_order[value.sort()].append(value)
            
        # sort np components
        for key, value in self.__attached_comps.items():
            for item in value:
                if not scripts_exec_order.__contains__(item.sort()):
                    scripts_exec_order[item.sort()] = []
                scripts_exec_order[item.sort()].append(item)

        # finally start
        for scripts in scripts_exec_order.values():
            for script in scripts: 
                try:
                    _res = script.start()
                except Exception as execption:
                    print(execption)
                    success = False
                    break

        if not success:
            self.stop()

    def stop(self):
        for value in self.__runtime_scripts.values():
            if value.is_running():
                value.stop()

        for key, value in self.__attached_comps.items():
            for item in value:
                if item.is_running():
                    item.stop()

    def on_resize_event(self):
        """should be called after a window has been resized"""
        self.__active_scene.on_resize_event()
        
    listen = lambda self, evt, callback, *args: self.__demon.accept(evt,
                                                                    callback,
                                                                    *args)

    @property
    def engine(self):
        return self.__demon.engine

    @property
    def dr(self):
        return self.__dr

    @property
    def dr2d(self):
        return self.__dr2d
    
    @property
    def mouse_watcher(self):
        return self.__mouse_watcher

    @property
    def render(self):
        return self.__render
    
    @property
    def render2d(self):
        return self.__render2d
    
    @property
    def active_scene(self):
        return self.__active_scene
