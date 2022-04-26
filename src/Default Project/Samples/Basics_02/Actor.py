import math
import panda3d.core as p3dCore
from editor.core.pModBase import PModBase


class Actor(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        # __init__ should contain anything except for variable declaration...!

        self.should_start = False
        self.walk_amim = "Samples/Basics_02/panda-walk4"

    # on_start method is called once
    def on_start(self):
        if not self.should_start:
            return
        panda = self._render.find("**/panda_walk_character").getPythonTag("PICKABLE")
        anims = {"walk": self.walk_amim}
        panda.load_anims(anims)
        panda.loop("walk")

    # update method is called every frame
    def on_update(self):
        pass
