import math
import panda3d.core as p3d


class Scene:
    """Scene class represents a game scene"""
    def __init__(self, game, name, *args, **kwargs):
        self.__game = game
        self.__name = name

        # create a 3d rendering setup
        self.__render = None
        self.__main_cam = None
        
        # create a 2d rendering setup
        self.__render2d = None
        self.__aspect2d = None
        self.__camera2d = None
        
        # create 2D and 3D rendering
        self.setup_render3d()
        self.create_render2d()
        
        #
        self.__default_sunlight = None
        
        # other
        self.__shift = False
        self.__is_btn_down = self.__game.engine.mw.node().is_button_down
        
    def update(self):
        if self.__default_sunlight:
            self.__shift = self.__is_btn_down(p3d.KeyboardButton.shift())

            if self.__is_btn_down(p3d.KeyboardButton.asciiKey("a")):
                self.orbit_default_sun(dx=-1) if self.__shift else\
                self.orbit_default_sun(dx=1)

            elif self.__is_btn_down(p3d.KeyboardButton.asciiKey("d")):
                self.orbit_default_sun(dy=-1) if self.__shift else\
                self.orbit_default_sun(dy=1)
        
    def on_resize_event(self):
        props = self.__game.engine.win.getProperties()
        aspect = (props.getXSize() * 0.4) / (props.getYSize() * 0.35)
        
        if self.__main_cam:
            self.__main_cam.node().getLens().setAspectRatio(aspect)
            
        if self.render:
            self.render.setScale(1.0 / aspect, 1.0, 1.0 / aspect)
            
        if self.__aspect2d:
            self.__aspect2d.set_scale(1.0 / aspect, 1.0, 1.0)
        
    def setup_render3d(self):
        name_ = "%s%s" % (self.__name, "Render")
        self.__render = p3d.NodePath(self.__name)
        self.__render.reparent_to(self.__game.render)
        
        # create a new main camera for game world and a lens for it
        self.__main_cam = p3d.NodePath(p3d.Camera("MainCamera"))
        self.__main_cam.reparent_to(self.__render)

        lens = p3d.PerspectiveLens()
        lens.set_fov(60)
        lens.setAspectRatio(800 / 600)
        self.__main_cam.node().setLens(lens)
        
        self.__game.dr.set_camera(self.__main_cam)
        
    def create_render2d(self):
        """setup a 2d rendering"""

        # create a 2d scene graph
        name_ = "%s%s" % (self.__name, "Render2d")
        self.__render2d = self.__game.render2d.attachNewNode(name_)
        self.__aspect2d = self.__render2d.attachNewNode(p3d.PGTop("Aspect2d"))
        
        mw = self.__game.mouse_watcher
        self.__aspect2d.node().set_mouse_watcher(mw.node())

        # create a 2d-camera
        self.__camera2d = p3d.NodePath(p3d.Camera("__camera2D__"))
        lens = p3d.OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        self.__camera2d.node().setLens(lens)
        self.__camera2d.reparent_to(self.__render2d)
        
        self.__game.mouse_watcher.node().addRegion(p3d.PGMouseWatcherBackground())
        self.__game.dr2d.setCamera(self.__camera2d)
        
    def create_default_sun(self):
        # --------------------------------------------------------------------
        # sun (directional light)
        sunlight = p3d.DirectionalLight('Sunlight')
        sunlight.setColor((0.6, 0.6, 0.6, 1))
        sunlight.show_frustum()

        # create new lens for sunlight
        lens = p3d.PerspectiveLens()
        lens.setFov(60)
        lens.setNearFar(0.25, 25)
        sunlight.setLens(lens)

        sunlight_np = self.__render.attachNewNode(sunlight)
        self.__render.setLight(sunlight_np)

        # update position
        sunlight_np.setPos(0, 0, 25)
        sunlight_np.setHpr(-25, 215, 0)
        self.__default_sunlight = sunlight_np
        self.orbit_default_sun()

    def orbit_default_sun(self, dx=0, dy=0):
        # Get new hpr
        hpr = p3d.LVecBase3f(0, 0, 0)
        hpr.setX(self.__default_sunlight.getH() + dx)
        hpr.setY(self.__default_sunlight.getP() + dy)
        hpr.setZ(self.__default_sunlight.getR())

        # Set camera to new hpr
        self.__default_sunlight.setHpr(hpr)

        # Get the H and P in radians
        rad_x = hpr.getX() * (math.pi / 180.0)
        rad_y = hpr.getY() * (math.pi / 180.0)

        # Get distance from camera to target
        dir_to_target = self.__default_sunlight.getPos() - p3d.LVecBase3f(0, 0, 0)
        dist_to_target = dir_to_target.length()

        # Get new camera pos
        new_pos = p3d.LVecBase3f(0, 0, 0)
        new_pos.setX(dist_to_target  * math.sin(rad_x) * math.cos(rad_y))
        new_pos.setY(-dist_to_target * math.cos(rad_x) * math.cos(rad_y))
        new_pos.setZ(-dist_to_target * math.sin(rad_y))
        # new_pos += self.__target.getPos()

        # Set camera to new pos
        self.__default_sunlight.setPos(new_pos)
        
    def add_light(self, light):
        if light.Point:
            light_node = p3d.PointLight("PointLight")
        elif light.Directional:
            light_node = p3d.DirectionalLight("DirectionalLight")
        elif light.Spot:
            light_node = p3d.Spotlight("Spotlight")
        elif light.Ambient:
            light_node = p3d.AmbientLight("AmbientLight")
        
        np = p3d.NodePath(light_node)
        np.reparent_to(self.__render)
        
        return np
    
    def add_camera(self):
        pass
        
    @property
    def camera2d(self):
        return self.__camera2d

    @property
    def render(self):
        return self.__render

    @property
    def render2d(self):
        return self.__render2d

    @property
    def aspect2d(self):
        return self.__aspect2d
