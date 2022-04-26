from panda3d.core import Vec4, Vec2, Vec3, TextProperties, TextPropertiesManager
from direct.gui.DirectGui import DirectFrame, DirectButton
from editor.p3d.object import Object
from editor.utilities import convert_to_range
from editor.constants import *


class OnSceneUI(Object):
    def __init__(self, level_editor, *args, **kwargs):
        Object.__init__(self, args, **kwargs)
        
        object_manager.add_object("SceneUI", self)

        self.level_editor = level_editor
        self.btn_maps_geo = None
        self.create_buttons()

    def create_buttons(self):
        self.btn_maps_geo = object_manager.get("LevelEditor").load_model("button_maps.egg",
                                                                         GEO_NO_PARENT)
        self.play_btn = DirectButton(geom=self.btn_maps_geo.find("**/control_play_blue"),
                                     scale=32,
                                     pressEffect=1,
                                     command=self.start_button,
                                     borderWidth=(0.025, 0.025),
                                     frameColor=(0.55, 0.55, 0.55, 1),
                                     relief=2,
                                     extraArgs=[])
        self.play_btn.reparent_to(self.rootP2d)

        self.stop_btn = DirectButton(geom=self.btn_maps_geo.find("**/control_stop_blue"),
                                     scale=32,
                                     pressEffect=1,
                                     command=self.stop_button,
                                     borderWidth=(0.025, 0.025),
                                     frameColor=(0.55, 0.55, 0.55, 1),
                                     relief=2,
                                     extraArgs=[])
        self.stop_btn.reparent_to(self.rootP2d)
        
    def start_button(self, *args):
        obs.trigger("PlayUserModules")
    
    def stop_button(self, *args):
        obs.trigger("StopUserModules")
        
    def change_graphics(self, btn_id):
        if btn_id == PLAY_BTN_ID:
            self.play_btn["relief"] = 5
            self.play_btn["geom"] = self.btn_maps_geo.find("**/control_play_grey")
            self.stop_btn["geom"] = self.btn_maps_geo.find("**/control_stop_red")
        elif btn_id == STOP_BTN_ID:
            self.play_btn["relief"] = 2
            self.play_btn["geom"] = self.btn_maps_geo.find("**/control_play_blue")
            self.stop_btn["geom"] = self.btn_maps_geo.find("**/control_stop_blue")

    def on_resize(self, sizeX, sizeY):
        self.play_btn.setPos(sizeX - 24, 0, -22)
        self.stop_btn.setPos(sizeX - 24 - 34, 0, -22)
