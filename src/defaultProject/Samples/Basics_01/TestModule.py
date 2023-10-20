from pathlib import Path
from panda3d.core import PNMImage, GeoMipTerrain
from game.resources import RuntimeModule


class TestModule(RuntimeModule):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)

    def on_start(self):
        self.__heightmap = PNMImage("src/defaultProject" + "/Samples/Basics_01/FuckingHeightmap.png")
                 
        terrain = GeoMipTerrain("mySimpleTerrain")
        terrain.setHeightfield(self.__heightmap)
        terrain.setBruteforce(False)
        terrain.getRoot().reparentTo(self.render)
        terrain.getRoot().setScale(1, 1, 0.667*400)  # source; trust me bro
        terrain.generate()

    def on_update(self):
        # this method is called after update
        pass

    def foo(self):
        print("TestModule: Foo")
