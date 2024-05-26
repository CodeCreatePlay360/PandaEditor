import math
import panda3d.core as p3d
from eventManager import EventManager
from engine import Engine
from directoryWatcher import DirWatcher
from project import Project
from system import Systems
from level_editor import LevelEditor


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
        self.__dir_watcher = DirWatcher(any_evt_callback=self.on_dir_event)
        self.__project = Project(self)
        
        # initialize project and game related systems
        self.set_project(proj_path)
        self.create_default_scene()
        
        # some other defaults
        self.__coll_trav = p3d.CollisionTraverser()
        self.__coll_handler = p3d.CollisionHandlerQueue()
        
        # initialize globals, this provides easy access to all commonly 
        # used systems
        self.__editor = Systems(
                                demon=self,
                                win=self.__engine.win,
                                mwn=self.__engine.mwn,
                                
                                dr=self.__engine.dr3d,
                                render=self.__engine.render,
                                cam=self.__engine.cam,
                                
                                dr2d=self.__engine.dr2d,
                                render2d=self.__engine.render2D,
                                aspect2d=self.__engine.aspect2d,
                                cam2d=self.__engine.cam,
                                
                                evt_mgr=self.__event_manager,
                                resources=self.__engine.resource_manager,
                                
                                coll_trav=self.__coll_trav,
                                coll_handler=self.__coll_handler)
                                
        # instance of level editor
        self.__le = None
                                
        # other
        self.__is_btn_down = self.engine.mwn.is_button_down
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
        print("on_any_dir_event")

    def set_project(self, proj_path):
        self.__project.set_project(proj_path)
        self.__dir_watcher.schedule(self.__project.path)
        # self.__project.game.active_scene.create_default_sun()

    def create_default_scene(self):
        scene = self.__project.game.add_new_scene("DefaultScene")
        # self.add_light(LightType.Point)
        
    def start_level_editor(self):
        self.__le = LevelEditor(self)
        self.__le.init()
        
    def accept(self, evt, callback, *args):
        if not self.__evt_map.__contains__(evt):
            self.__evt_map[evt] = []  # TODO -- replace this with tuple

        self.__evt_map[evt].append((callback, args))

    def on_any_event(self, evt, *args):
        """event sent from c++ side can be handled here"""

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
    def project(self):
        return self.__project

    @property
    def le(self):
        return self.__le

    @property
    def is_closed(self):
        return self.__is_closed
