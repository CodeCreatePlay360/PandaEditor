import math
import panda3d.core as p3dCore
from editor.core.pModBase import PModBase
from editor.utils import EdProperty


class EdPlugin(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)
        self.is_ed_plugin(True)

        # __init__ should contain anything except for variable declaration...!
        self.curr_game_viewport_style = 0
        self.add_hidden_variable("curr_game_viewport_style")
        self.add_property(EdProperty.ChoiceProperty("GameViewPortStyle",
                                                    choices=["Minimized", "Maximized"],
                                                    value=self.curr_game_viewport_style,  # initial value
                                                    setter=self.set_game_viewport_style,
                                                    getter=self.get_game_viewport_style))

    # on_start method is called once
    def on_start(self):
        pass

    # update method is called every frame
    def on_update(self):
        pass

    def set_game_viewport_style(self, val: int):
        self.curr_game_viewport_style = val

        if val == 0:
            self._le._game_view_minimized = True
        elif val == 1:
            self._le._game_view_minimized = False

    def get_game_viewport_style(self):
        return self.curr_game_viewport_style
