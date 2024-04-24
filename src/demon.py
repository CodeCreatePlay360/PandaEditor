import math
import panda3d.core as p3d
from eventManager import EventManager
from engine import Engine
from game import Game
from system import Systems


class Demon(object):
    def __init__(self, start_wx=False):
        object.__init__(self)

        self.__is_closed = False

        # set this to true if using wx
        self.__wx = start_wx

        # initialize event handler for python side event handling
        self.__event_manager = EventManager()

        # init the engine
        self.__engine = Engine()
        self.__engine.set_event_hook(self.on_any_event)
        self.__engine.add_update_callback(self.on_update)

        # init game
        self.__game = Game(self.__engine)

        # initialize globals, this provides easy access to all commonly 
        # used systems
        self.__editor = Systems(
            demon=self,
            event_system=self.__event_manager,
            engine=self.__engine,
            resource_manager=self.__engine.resource_manager)

        # event registration
        # self.__event_manager.register("OnExit", self.on_exit)
        # self.__event_manager.trigger("OnExit")

        # other
        self.__is_down = self.engine.mwn.is_button_down
        self.__shift = False
        self.__default_lights = False

    '''
    def on_exit(self, *args, **kwargs):
        print(args)
    '''

    def setup_scene(self):
        scene = self.__engine.resource_manager.load_model("src/resources/environment.egg.pz")
        scene.reparent_to(self.__engine.render)

    def create_default_lights(self):
        # ambient light
        ambientlight = p3d.AmbientLight("AmbientLight")
        ambientlight.setColor((0.35, 0.35, 0.35, 1))

        ambientlight_np = self.engine.render.attachNewNode(ambientlight)
        self.engine.render.setLight(ambientlight_np)

        self.__ambientlight = ambientlight_np

        # --------------------------------------------------------------------
        # sun (directional light)
        sunlight = p3d.DirectionalLight('Sunlight')
        sunlight.setColor((0.6, 0.6, 0.6, 1))
        sunlight.show_frustum()
        # directionalLight.setShadowCaster(True, 512, 512)

        # create new lens for sunlight
        lens = p3d.PerspectiveLens()
        lens.setFov(60)
        lens.setNearFar(0.25, 25)
        sunlight.setLens(lens)

        sunlight_np = self.engine.render.attachNewNode(sunlight)
        self.engine.render.setLight(sunlight_np)

        # update position
        sunlight_np.setPos(0, 0, 25)
        sunlight_np.setHpr(-25, 215, 0)
        self.__sunlight = sunlight_np
        self.orbit_sun()

        self.__default_lights = True

    def exit(self):
        pass

    def on_any_event(self, evt, args=None):
        self.__game.on_any_event(evt, args)

    def on_update(self):
        if self.__default_lights:
            self.__shift = self.__is_down(p3d.KeyboardButton.shift())

            if self.__is_down(p3d.KeyboardButton.asciiKey("a")):
                self.orbit_sun(dx=-1) if self.__shift else self.orbit_sun(dx=1)

            elif self.__is_down(p3d.KeyboardButton.asciiKey("d")):
                self.orbit_sun(dy=-1) if self.__shift else self.orbit_sun(dy=1)

    def run(self):
        while not self.__engine.win.isClosed():
            self.__engine.update()

    def set_ambient_color(self, color):
        self.__ambientlight.setColor(color)

    def orbit_sun(self, dx=0, dy=0):
        # Get new hpr
        hpr = p3d.LVecBase3f(0, 0, 0)
        hpr.setX(self.__sunlight.getH() + dx)
        hpr.setY(self.__sunlight.getP() + dy)
        hpr.setZ(self.__sunlight.getR())

        # Set camera to new hpr
        self.__sunlight.setHpr(hpr)

        # Get the H and P in radians
        rad_x = hpr.getX() * (math.pi / 180.0)
        rad_y = hpr.getY() * (math.pi / 180.0)

        # Get distance from camera to target
        dir_to_target = self.__sunlight.getPos() - p3d.LVecBase3f(0, 0, 0)
        dist_to_target = dir_to_target.length()

        # Get new camera pos
        new_pos = p3d.LVecBase3f(0, 0, 0)
        new_pos.setX(dist_to_target * math.sin(rad_x) * math.cos(rad_y))
        new_pos.setY(-dist_to_target * math.cos(rad_x) * math.cos(rad_y))
        new_pos.setZ(-dist_to_target * math.sin(rad_y))
        # new_pos += self.__target.getPos()

        # Set camera to new pos
        self.__sunlight.setPos(new_pos)

    @property
    def engine(self):
        return self.__engine

    @property
    def event_manager(self):
        return self.__event_manager

    @property
    def is_closed(self):
        return self.__is_closed

    @property
    def resource_manager(self):
        return self.__engine.resource_manager
