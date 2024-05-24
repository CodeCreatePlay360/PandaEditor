import math
import panda3d.core as p3d


class Scene:
    """Scene class represents a game scene"""
    def __init__(self, game, name, *args, **kwargs):
        self.__game = game
        self.__name = name

        # create a 3d rendering setup
        self.__render = None

        # create a 2d rendering setup
        self.__render_2D = None
        self.__aspect_2d = None
        self.__camera_2D = None
        
        # create 2D and 3D rendering
        self.setup_render_3D()
        self.setup_render_2D()
        
        #
        self.__default_sunlight = None
        
        # other
        self.__shift = False
        self.__is_btn_down = self.__game.demon.engine.mwn.is_button_down
        
    def update(self):
        if self.__default_sunlight:
            self.__shift = self.__is_btn_down(p3d.KeyboardButton.shift())

            if self.__is_btn_down(p3d.KeyboardButton.asciiKey("a")):
                self.orbit_default_sun(dx=-1) if self.__shift else\
                self.orbit_default_sun(dx=1)

            elif self.__is_btn_down(p3d.KeyboardButton.asciiKey("d")):
                self.orbit_default_sun(dy=-1) if self.__shift else\
                self.orbit_default_sun(dy=1)
        
    def setup_render_3D(self):
        self.__render = p3d.NodePath(self.__name)
        self.__render.reparent_to(self.__game.render)

    def setup_render_2D(self):
        """setup a 2d rendering"""

        # create a 2d scene graph
        self.__render_2D = p3d.NodePath("Render2d")
        self.__render_2D.setDepthTest(False)
        self.__render_2D.setDepthWrite(False)

        self.__aspect_2d = self.__render_2D.attachNewNode(p3d.PGTop("__aspect2D__"))
        aspect_ratio = self.__game.demon.engine.aspect_ratio
        self.__aspect_2d.set_scale(1.0 / aspect_ratio, 1.0, 1.0)
        
        mwn = self.__game.demon.engine.mwn
        self.__aspect_2d.node().set_mouse_watcher(mwn)

        # create a 2d-camera
        self.__camera_2D = p3d.NodePath(p3d.Camera("__camera2D__"))
        lens = p3d.OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        self.__camera_2D.node().setLens(lens)
        self.__camera_2D.reparent_to(self.__render_2D)

        self.__game.dr_2d.setCamera(self.__camera_2D)
        
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
    def camera_2D(self):
        return self.__camera_2D

    @property
    def render(self):
        return self.__render

    @property
    def render_2D(self):
        return self.__render_2D

    @property
    def aspect_2D(self):
        return self.__aspect_2d
