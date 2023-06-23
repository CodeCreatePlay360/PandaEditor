from panda3d.core import CollisionTraverser, ClockObject
from editor.core import RuntimeModule


class World(RuntimeModule):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)

        self.__key_map = {}
        self.__c_trav = None  # main collision traverser
        self.global_clock = None  #

    def on_start(self):
        self.global_clock = ClockObject().getGlobalClock()
        self.__c_trav = CollisionTraverser()
        self.register_keys()

    def on_update(self):
        # this method is called every frame
        pass

    def on_late_update(self):
        self.__c_trav.traverse(self.render)

    def register_keys(self):
        self.__key_map = {
            "left": False,
            "right": False,
            "forward": False,
            "cam-left": False,
            "cam-right": False,
        }

        self.accept("a", self.set_key, ["left", True])
        self.accept("d", self.set_key, ["right", True])
        self.accept("w", self.set_key, ["forward", True])
        self.accept("e", self.set_key, ["cam-left", True])
        self.accept("q", self.set_key, ["cam-right", True])

        self.accept("a-up", self.set_key, ["left", False])
        self.accept("d-up", self.set_key, ["right", False])
        self.accept("w-up", self.set_key, ["forward", False])
        self.accept("e-up", self.set_key, ["cam-left", False])
        self.accept("q-up", self.set_key, ["cam-right", False])

    def set_key(self, key, value):
        self.__key_map[key] = value

    @property
    def key_map(self):
        return self.__key_map

    @property
    def c_trav(self):
        return self.__c_trav

    @property
    def dt(self):
        return self.global_clock.getDt()
