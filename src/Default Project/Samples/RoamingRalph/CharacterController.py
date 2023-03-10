import math
from editor.core import Component


class CharacterController(Component):
    def __init__(self, *args, **kwargs):
        Component.__init__(self, *args, **kwargs)

        self.__ralph = None
        self.__is_moving = False
        self.__world = None

    def on_start(self):
        self.__world = self.game.get_module(self.game.path+"/Samples/RoamingRalph/World.py")

        # get the actor, actual Actor node is saved as python tag,
        self.__ralph = self.getPythonTag("__GAME_OBJECT__")

        # load animations for ralph characters,
        walk_anim = self.game.path + "/Samples/RoamingRalph/Art/ralph-walk.egg.pz"
        run_anim = self.game.path + "/Samples/RoamingRalph/Art/ralph-run.egg.pz"
        anims = {"walk": walk_anim,
                 "run": run_anim}

        self.__ralph.loadAnims(anims)

    def on_update(self):
        # if a move-key is pressed, move ralph in the specified direction,
        key_map = self.__world.key_map

        if key_map["left"]:
            self.setH(self.getH() + 300 * self.__world.dt)
        if key_map["right"]:
            self.setH(self.getH() - 300 * self.__world.dt)
        if key_map["forward"]:
            self.setY(self, -25 * self.__world.dt)

        if key_map["forward"] or key_map["left"] or key_map["right"]:
            if self.__is_moving is False:
                self.__ralph.loop("run")
                self.__is_moving = True
        else:
            if self.__is_moving:
                self.__ralph.stop()
                self.__ralph.pose("walk", 5)
                self.__is_moving = False
