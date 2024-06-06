import math
import panda3d.core as p3d
from eventManager import EventManager
from engine import Engine
from game import Game
from project import Project
from system import Systems
from levelEditor import LevelEditor


class Demon(object):
    def __init__(self, proj_path=False, **kwargs):
        object.__init__(self)
        self.__is_closed = False
                
        # initialize event handler for python side event handling
        self.__event_manager = EventManager()
        self.__evt_map = {}  # evt_map[evt_name] = (call, list_args)
        
        # init the engine
        self.__engine = Engine()
        self.__engine.set_event_hook(self.on_any_event)
        # self.__engine.add_update_callback(self.on_update)
        
        # project
        self.__game = Game(self)
        self.__game.init()
        self.__project = Project(self)
        
        # initialize project and game related systems
        self.set_project(proj_path)
        self.create_default_scene()
        
        # some other defaults
        self.__coll_trav = p3d.CollisionTraverser()
        
        # initialize globals, this provides easy access to all commonly 
        # used systems
        self.__editor = Systems(
                                demon=self,
                                win=self.__engine.win,
                                mw=self.__engine.mw,
                                
                                dr=self.__engine.dr3d,
                                render=self.__engine.render,
                                cam=self.__engine.cam,
                                
                                dr2d=self.__engine.dr2d,
                                render2d=self.__engine.render2D,
                                aspect2d=self.__engine.aspect2d,
                                cam2d=self.__engine.cam,
                                
                                evt_mgr=self.__event_manager,
                                resources=self.__engine.resource_handler,
                                
                                coll_trav=self.__coll_trav,
                                
                                game=self.__game)
                                
        # instance of level editor
        self.__le = None
                                
        # accept events
        self.accept("space", self.__game.start)
                                
        # other
        self.__default_sun = False
        self.__shift = False
        
    def run(self):
        while not self.__engine.win.isClosed():
            self.__engine.update()
            self.on_update()

    def on_update(self):
        pass

    def exit(self):
        pass

    def on_dir_event(self):
        paths = self.__project.get_all_scripts()
        runtimescripts, comps = self.engine.resource_handler.load_scripts(paths)
        self.__game.set_runtime_scripts(runtimescripts)
        self.__game.set_components(comps)

    def set_project(self, proj_path):
        self.__project.set_project(proj_path)
        # self.__project.game.active_scene.create_default_sun()

    def create_default_scene(self):
        scene = self.__game.add_new_scene("DefaultScene")
        # self.add_light(LightType.Point)
        
    def start_level_editor(self):
        self.__le = LevelEditor(self)
        self.__le.init()
        
    def accept(self, evt, callback, *args):
        if not isinstance(evt, str) or not callable(callback):
           print("Incorret arguments to demon.accept")
           return
            
        if not self.__evt_map.__contains__(evt):
            self.__evt_map[evt] = []

        self.__evt_map[evt].append((callback, args))
        
        return len(self.__evt_map[evt]) - 1
        
    def ignore(self, evt, id):
        if self.__evt_map.__contains__(evt) and id < len(self.__evt_map[evt]): 
           self.__evt_map[evt].pop(id)

    def on_any_event(self, evt, *args):
        """event sent from c++ side can be handled here"""
        
        '''
        if evt.name == "TaskManager-addTask":
           print("%s%s" % ("added", args))
        elif evt.name == "TaskManager-removeTask":
           print("%s%s" % ("removed", args))
        '''
                
        if evt.name == "window-event":
           self.__game.on_resize_event()
        
        if evt.name in self.__evt_map.keys():
            res = self.__evt_map[evt.name]

            has_callable_arguments = False

            for i in range(len(res)):
                callback = res[i][0]
                args = res[i][1]

                for j in range(len(args)):
                    if callable(args[j]):
                        has_callable_arguments = True
                        break

                # if we have callables arguments replace them with the result from callable
                if has_callable_arguments:
                    args = tuple(val() if callable(val) else val for val in args)

                if args is not None and len(args) > 0:
                    callback(*args)
                else:
                    callback()

    @property
    def event_manager(self):
        return self.__event_manager

    @property
    def engine(self):
        return self.__engine

    @property
    def game(self):
        return self.__game

    @property
    def project(self):
        return self.__project

    @property
    def le(self):
        return self.__le

    @property
    def is_closed(self):
        return self.__is_closed
