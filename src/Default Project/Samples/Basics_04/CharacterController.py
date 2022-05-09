import math
import panda3d.core as p3d_core
from editor.core.pModBase import PModBase


class CharacterController(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)
        # __init__ should not contain anything except for variable declaration...!

        self.input_manager = None
        self.ralph = None
        self.walkAnim = "Samples/Basics_04/models/ralph-walk"
        self.walkSpeed = -3
        self.turnSpeed = 80
        self.__isMoving = False
        self.should_start = False

    def on_start(self):
        # this method is called only once
        if not self.should_start:
            return

        self.input_manager = self._le.get_module("InputManager")
        self.ralph = self._render.find("**/Ralph").getPythonTag("PICKABLE")
        self.ralph.set_scale(6)
        anims = {"walk": self.walkAnim}
        self.ralph.load_anims(anims)

    def on_update(self):
        # this method is called evert frame
        if not self.should_start:
            return

        dt = globalClock.getDt()

        # if a move-key is pressed, move ralph in the specified direction.
        if self.input_manager.key_map["d"]:
            self.ralph.setH(self.ralph.getH() - self.turnSpeed * dt)

        if self.input_manager.key_map["a"]:
            self.ralph.setH(self.ralph.getH() + self.turnSpeed * dt)

        if self.input_manager.key_map["w"]:
            self.ralph.setY(self.ralph, self.walkSpeed * dt)

        # if ralph is moving, loop the run animation.
        # if standing still, stop the animation.

        if self.input_manager.key_map["w"] or self.input_manager.key_map["d"] or self.input_manager.key_map["a"]:
            if not self.__isMoving:
                self.ralph.loop("walk")
                self.__isMoving = True
        else:
            if self.__isMoving:
                self.ralph.stop()
                self.ralph.pose("walk", 5)
                self.__isMoving = False
