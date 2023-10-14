from pathlib import Path
from game.resources import Component
from panda3d.core import NodePath


class CameraController(Component):
    def __init__(self, *args, **kwargs):
        Component.__init__(self, *args, **kwargs)

        self.__ralph = None
        self.__floater = None
        self.__world = None

    def on_start(self):
        self.__world = self.game.get_module(self.game.path + str(Path("/Samples/RoamingRalph/World.py")))

        # get the ralph character,
        self.__ralph = self.render.find("Ralph")

        # Create a floater object, which floats 2 units above ralph.  We
        # use this as a target for the camera to look at,
        self.__floater = NodePath("CamLookAtTarget")
        self.__floater.reparent_to(self.__ralph)
        self.__floater.setZ(2.0)

        # set an initial pos for the camera
        self.setPos(self.__ralph.getX(), self.__ralph.getY() - 60, 5)

    def on_update(self):
        if self.__world.key_map["cam-left"]:
            self.setX(self, -20 * self.__world.global_clock.getDt())
        if self.__world.key_map["cam-right"]:
            self.setX(self, +20 * self.__world.global_clock.getDt())

        cam_vec = self.__ralph.getPos() - self.getPos()
        cam_vec.setZ(0)
        cam_dist = cam_vec.length()
        cam_vec.normalize()

        # apply min and max distance
        if cam_dist > 20.0:
            self.setPos(self.getPos() + cam_vec * (cam_dist - 20))
            cam_dist = 10.0
        if cam_dist < 5.0:
            self.setPos(self.getPos() - cam_vec * (5.0 - cam_dist))

        # The camera should look in ralph's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above ralph's head.
        self.lookAt(self.__floater)
