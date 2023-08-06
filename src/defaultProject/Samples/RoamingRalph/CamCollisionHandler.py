from pathlib import Path
from panda3d.core import CollisionNode, CollisionHandlerQueue, CollisionRay, CollideMask
from editor.core import Component


class CamCollisionHandler(Component):
    def __init__(self, *args, **kwargs):
        Component.__init__(self, *args, **kwargs)

        self.__ralph = None
        #
        # collision solid-ray
        self.__cam_ground_ray = None
        self.__cam_ground_ray = None
        self.__cam_ground_ray = None
        #
        # collision node to hold collision solid
        self.__cam_ground_col = None
        self.__cam_ground_col = None
        self.__cam_ground_col = None
        self.__cam_ground_col = None
        #
        self.__cam_ground_col_np = None
        #
        # collision handler
        self.__cam_ground_handler = None

    def on_start(self):
        # this method is called only once
        # get the ralph character
        self.__ralph = self.render.find("Ralph")
        #
        world = self.game.get_module(self.game.path + str(Path("/Samples/RoamingRalph/World.py")))
        #
        # collision solid-ray
        self.__cam_ground_ray = CollisionRay()
        self.__cam_ground_ray.setOrigin(0, 0, 9)
        self.__cam_ground_ray.setDirection(0, 0, -1)
        #
        # collision node to hold collision solid
        self.__cam_ground_col = CollisionNode('CamRay')
        self.__cam_ground_col.addSolid(self.__cam_ground_ray)
        self.__cam_ground_col.setFromCollideMask(CollideMask.bit(0))
        self.__cam_ground_col.setIntoCollideMask(CollideMask.allOff())
        #
        self.__cam_ground_col_np = self.attachNewNode(self.__cam_ground_col)
        #
        # collision handler
        self.__cam_ground_handler = CollisionHandlerQueue()
        #
        world.c_trav.addCollider(self.__cam_ground_col_np, self.__cam_ground_handler)

    def on_update(self):
        # this method is called every frame
        pass

    def on_late_update(self):
        # Keep the camera at one foot above the terrain,
        # or two feet above ralph, whichever is greater.

        entries = list(self.__cam_ground_handler.entries)
        entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().name == "terrain":
            self.setZ(entries[0].getSurfacePoint(self.render).getZ() + 1.0)

        if self.getZ() < self.__ralph.getZ() + 8.0:
            self.setZ(self.__ralph.getZ() + 8.0)
