import math
import panda3d.core as p3dCore
from editor.core.pModBase import PModBase
from editor.utils import common_maths


class CubeRotator(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        self.should_start = False

        self.__cube_np = None
        self.__light_1_np = None
        self.__light_2_np = None

        self.__is_ok = False

        self.cube_rotate_speed = 5
        self.lights_rotate_speed = 3
        self.light_to_cube_distance = 80
        self.__y_rotation = 0  # current rotation of lights

    def on_start(self):
        # this method is called only once
        self.__cube_np = self._render.find("**Player")
        self.__light_1_np = self._render.find("**PointLight_01")
        self.__light_2_np = self._render.find("**PointLight_02")

        if self.__cube_np and self.__light_1_np and self.__light_2_np:
            self.__is_ok = True
        else:
            print("[CubeRotator] error unable to find all models...!")
            self.__is_ok = False

    def on_update(self):
        if not self.should_start or not self.__is_ok:
            return

        self.rotate_cube()
        self.rotate_lights()

    def rotate_cube(self):
        h = self.__cube_np.getH()
        h += self.cube_rotate_speed * globalClock.getDt()
        if h > 360:
            h = 0
        self.__cube_np.setH(h)

    def rotate_lights(self):
        dist = self.light_to_cube_distance

        self.__y_rotation += self.lights_rotate_speed * globalClock.getDt()
        self.__y_rotation = common_maths.clamp_angle(self.__y_rotation, -360, 360)

        # ======================================================================================== #
        # rotate light 01
        orbit_rot = p3dCore.Vec3()
        orbit_rot.x = dist * math.cos(self.__y_rotation * (math.pi / 180)) - dist * math.sin(self.__y_rotation * (math.pi / 180))
        orbit_rot.y = dist * math.sin(self.__y_rotation * (math.pi / 180)) + dist * math.cos(self.__y_rotation * (math.pi / 180))
        orbit_rot.z = 0

        new_pos = p3dCore.Vec3(0, 0, 40)
        new_pos += orbit_rot

        self.__light_1_np.setPos(new_pos)

        # ======================================================================================== #
        # rotate light 02
        orbit_rot = p3dCore.Vec3()
        orbit_rot.x = dist * math.cos(-self.__y_rotation * (math.pi / 180)) - dist * math.sin(-self.__y_rotation * (math.pi / 180))
        orbit_rot.y = dist * math.sin(-self.__y_rotation * (math.pi / 180)) + dist * math.cos(-self.__y_rotation * (math.pi / 180))
        orbit_rot.z = 0

        new_pos = p3dCore.Vec3(0, 0, 40)
        new_pos += orbit_rot

        self.__light_2_np.setPos(new_pos)
