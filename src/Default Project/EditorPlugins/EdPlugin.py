import math
import panda3d.core as p3d_core
import direct.gui.DirectGui as gui
import wx

from editor.core.editorPlugin import EditorPlugin
from editor.utils import EdProperty


class EdPlugin(EditorPlugin):
    def __init__(self, *args, **kwargs):
        EditorPlugin.__init__(self, *args, **kwargs)

        return

        # __init__ should not contain anything except for variable declaration...!
        self.curr_game_viewport_style = 0
        self.hidden_attrs = "curr_game_viewport_style"
        self.add_property(EdProperty.ChoiceProperty("GameViewPortStyle",
                                                    choices=["Minimized", "Maximized"],
                                                    value=self.curr_game_viewport_style,  # initial value
                                                    setter=self.set_game_viewport_style,
                                                    getter=self.get_game_viewport_style))

        self.grid_size = 200
        self.gridStep = 40
        self.sub_divisions = 5

        self.hidden_attrs = "grid_size"
        self.hidden_attrs = "gridStep"
        self.hidden_attrs = "sub_divisions"

        self.add_property(EdProperty.EmptySpace(0, 10))  # add some empty space
        self.add_property(EdProperty.Label(name="GridSettings", is_bold=True))
        self.add_property(EdProperty.ObjProperty(name="grid_size", value=self.grid_size, _type=float, obj=self))
        self.add_property(EdProperty.ObjProperty(name="gridStep", value=self.gridStep, _type=float, obj=self))
        self.add_property(EdProperty.ObjProperty(name="sub_divisions", value=self.sub_divisions, _type=float, obj=self))
        self.add_property(EdProperty.ButtonProperty("SetGrid", self.set_grid))  # button property

        self.gameCamNp = ""
        self.hidden_attrs = "gameCamNp"

        self.add_property(EdProperty.EmptySpace(0, 10))  # add some empty space
        self.add_property(EdProperty.Label(name="ViewPortSettings", is_bold=True))
        self.add_property(EdProperty.ObjProperty(name="gameCamNp", value="None", _type=str, obj=self))
        self.add_property(EdProperty.ButtonProperty("SetAsActiveCam", self.set_active_cam_as_game_cam))

    # on_start method is called once
    def on_start(self):
        return
        # self.create_ui()         # direct gui
        le = self._le              # level editor
        wx_panel = self._panel     # the top most parent "Panel" of wxPython, if request to unique panel is
                                   # successful, otherwise return value of self._panel is None.
                                   # All wx UI elements should be child of this.

    # update method is called every frame
    def on_update(self):
        pass

    def create_ui(self):
        b = gui.DirectButton(text=("OK", "click!", "rolling over", "disabled"), scale=.5, command=self.set_text)
        b.reparent_to(self._aspect2d)

    def set_text(self):
        print("Set text called")

    def set_game_viewport_style(self, val: int):
        self.curr_game_viewport_style = val
        self._le.set_game_viewport_style(1 == val)

    def get_game_viewport_style(self):
        return self.curr_game_viewport_style

    def set_grid(self):
        self._le.create_grid(self.grid_size, self.gridStep, self.sub_divisions)

    def set_active_cam_as_game_cam(self):
        camera = self._render.find("**/"+self.gameCamNp)
        if camera:
            self._le.set_player_camera(camera)
