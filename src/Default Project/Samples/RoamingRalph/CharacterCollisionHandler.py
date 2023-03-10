import math
from panda3d.core import CollisionNode, CollisionHandlerQueue, CollisionRay, CollideMask
from editor.core import Component


class CharacterCollisionHandler(Component):
    def __init__(self, *args, **kwargs):
        Component.__init__(self, *args, **kwargs)

        self.__world = None

        # for character
        self.__ralph_ground_ray = None  #
        self.__ralph_ground_ray_node = None  #
        self.__ralph_ground_col_np = None  #
        self.__ralph_ground_handler = None  #

    def on_start(self):
        self.__world = self.game.get_module(self.game.path+"/Samples/RoamingRalph/World.py")

        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above ralph's head, and the other will start above the camera.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.
        #
        # collision solid-ray
        self.__ralph_ground_ray = CollisionRay()
        self.__ralph_ground_ray.setOrigin(0, 0, 9)
        self.__ralph_ground_ray.setDirection(0, 0, -1)
        #
        # create a collision node to hold collision solids
        self.__ralph_ground_ray_node = CollisionNode('RalphRay')
        self.__ralph_ground_ray_node.addSolid(self.__ralph_ground_ray)
        self.__ralph_ground_ray_node.setFromCollideMask(CollideMask.bit(0))
        self.__ralph_ground_ray_node.setIntoCollideMask(CollideMask.allOff())
        #
        self.__ralph_ground_col_np = self.attachNewNode(self.__ralph_ground_ray_node)
        #
        # collision handler
        self.__ralph_ground_handler = CollisionHandlerQueue()
        #
        self.__world.c_trav.addCollider(self.__ralph_ground_col_np, self.__ralph_ground_handler)

    def on_update(self):
        # this method is called every frame
        self.keep_ralph_on_terrain()

    def keep_ralph_on_terrain(self):
        # Adjust ralph's Z coordinate.  If ralph's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        start_pos = self.getPos()

        entries = list(self.__ralph_ground_handler.entries)
        entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().name == "terrain":
            self.setZ(entries[0].getSurfacePoint(self.render).getZ())
        else:
            self.setPos(start_pos)
