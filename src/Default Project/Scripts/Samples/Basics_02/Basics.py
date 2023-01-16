import math
import panda3d.core as p3d_core
from editor.core.component import Component

 
class Basics(Component):
    def __init__(self, *args, **kwargs):
        Component.__init__(self, *args, **kwargs)
        # __init__ should not contain anything except for variable declaration...!

        self.direction = 1
        self.distance_from_target = 10

        self.__smiley = None
        self.__curr_rotation = None
        self.__is_ok = True

        self.discarded_attrs = "_Basics_is_ok"

    def on_start(self):
        # this method is called only once

        # find smiley model in scene graph
        self.__smiley = self.render.find("**/smiley.egg.pz")

        if not self.__smiley:
            print("smiley model not found in scene...!")

        self.__curr_rotation = 0

        if not self.is_ok():
            print("direction must be 1 or -1...!")

    def is_ok(self):
        return self.direction != 1 or self.direction != -1
            
    def on_update(self):
        # this method is called every frame
        if self.is_ok():
            self.__curr_rotation = self.orbit(self.__curr_rotation, self.direction)

    def orbit(self, rotation, direction=-1):
        rotation += 50 * globalClock.getDt()
        if rotation > 360:
            rotation = 0

        target_pos = p3d_core.LVecBase3f(0, 0, self.distance_from_target)

        dist = target_pos.length()

        axis = p3d_core.LVecBase3f(0, 0, 0)

        pi_over_180 = math.pi / 180

        axis.x = (dist * math.cos(rotation * pi_over_180) - dist * math.sin(rotation * pi_over_180))
        axis.y = dist * math.cos(rotation * pi_over_180) - dist * math.sin(rotation * pi_over_180)
        axis.z = dist * math.sin(rotation * pi_over_180) + dist * math.cos(rotation * pi_over_180)

        axis.x *= direction
        axis.z *= direction

        new_pos = axis

        if self.__smiley:
            new_pos += self.__smiley.get_pos()

        self.setPos(new_pos)

        return rotation

