import math
from panda3d.core import Vec3, Vec2
from editor.core.pModBase import PModBase
from editor.utils import common_maths


class ThirdPersonCam(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        # movement settings
        self.targetPosOffset = Vec3(0, 0, 35)
        self.lookSmooth = 100
        self.distanceToTarget = 150

        self.minZoom = 80
        self.maxZoom = 250
        self.maxRotation_X = 0.0
        self.minRotation_Y = 0.0

        self._xRotation = 0.0
        self._yRotation = 0.0

        self.zoomSmooth = 500
        self.orbitSmooth = 1000.0

        self.__targetPos = Vec3(0, 0, 0)
        self.__zoom_dir = 0
        self.target = None
        self.input_manager = None
        self.cam = None

        self.mouseZoom = False
        self.shouldStart = False

    def on_start(self):
        if not self.shouldStart:
            return

        self.target = self._render.find("**/Ralph")               # find player
        self.input_manager = self._le.get_module("InputManager")  # find input manager
        self.cam = self._game_cam                                 # get main scene cam
        self.reset()

    def on_update(self):
        if not self.shouldStart:
            return

        if self.input_manager.key_map["r-up"] > 0:
            self.reset()

        # keyboard orbit

    def on_late_update(self):
        if not self.shouldStart:
            return

        self.move_to_target()
        self.look_at_target()
        self.orbit()
        self.zoom()
        
    def reset(self):
        self.distanceToTarget = 150
        self._yRotation = 0
        self.move_to_target()
                    
    def move_to_target(self):
        self.__targetPos = self.target.getPos()
        self.__targetPos.y -= self.distanceToTarget
        
        dist = self.target.getPos() - self.__targetPos
        dist = dist.length()

        # orbit rotation on y-axis
        orbit_rot_y = Vec3()
        orbit_rot_y.x = dist * math.cos(self._yRotation * (math.pi / 180)) - dist * math.sin(self._yRotation * (math.pi / 180))
        orbit_rot_y.y = dist * math.sin(self._yRotation * (math.pi / 180)) + dist * math.cos(self._yRotation * (math.pi / 180))
        orbit_rot_y.z = 0

        new_pos = self.target.getPos() + self.targetPosOffset
        new_pos += orbit_rot_y

        self.cam.setPos(new_pos)

    def look_at_target(self):
        self.cam.lookAt(self.target.getPos()+self.targetPosOffset)

    def orbit(self):
        self._xRotation = 0
        self._yRotation += -self.input_manager.mouseInput.x * self.orbitSmooth * globalClock.getDt()
        self._yRotation = common_maths.clamp_angle(self._yRotation, -360, 360)

        '''
        # ------------------------------------------------------------------------ #
        # if use keyboard orbit
        # for rotation on y-axis
        _dir = 0
        if self.input_manager.key_map["d"] > 0:
            _dir = 1
        elif self.input_manager.key_map["a"] > 0:
            _dir = -1

        self._yRotation += _dir * self.orbitSmooth * globalClock.getDt()
        self._yRotation = common_maths.clamp_angle(self._yRotation, -360, 360)
        # ------------------------------------------------------------------------ #
        '''

    def zoom(self):
        if self.mouseZoom:
            self.distanceToTarget += self.input_manager.zoom * self.zoomSmooth * globalClock.getDt()
        else:
            # ------------------------------------------------------------------------ #
            # if use keyboard zoom
            zoom_dir = 0
            if self.input_manager.key_map["q"] > 0:
                zoom_dir = 1
            elif self.input_manager.key_map["e"] > 0:
                zoom_dir = -1

            self.distanceToTarget += zoom_dir * self.zoomSmooth * globalClock.getDt()
            # ------------------------------------------------------------------------ #

        if self.distanceToTarget < self.minZoom:
            self.distanceToTarget = self.minZoom

        elif self.distanceToTarget > self.maxZoom:
            self.distanceToTarget = self.maxZoom
