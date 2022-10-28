from panda3d.core import PerspectiveLens, OrthographicLens, Camera, NodePath, LColor
from editor.nodes.baseNodePath import BaseNodePath
from editor.utils import EdProperty
from editor.globals import editor


class CameraNodePath(BaseNodePath):
    def __init__(self, np, path, uid=None):
        BaseNodePath.__init__(self, np, path, id_="__CameraNodePath__", uid=uid)
        self.setColor(LColor(0.2, 0.2, 0.2, 1))
        self.current_lens_type = -1  # 0: Perspective, 1: Ortho
        self.set_lens(0)
        self.create_properties()

    def create_properties(self):
        super(CameraNodePath, self).create_properties()

        space_prop = EdProperty.EmptySpace(0, 10)
        lens_prop_label = EdProperty.Label(name="Lens", is_bold=True)
        lens_type = EdProperty.ChoiceProperty("Lens Type",
                                              choices=["Perspective", "Orthographic"],
                                              value=0,
                                              setter=self.set_lens,
                                              getter=lambda: self.current_lens_type)

        # remove color property for camera
        for prop in self.properties:
            if prop.name == "Color":
                self.properties.remove(prop)

        self.properties.append(space_prop)
        self.properties.append(lens_prop_label)
        self.properties.append(lens_type)

        lens = self.node().getLens()
        properties = EdProperty.Utils.get_properties_for_lens(lens)
        self.properties.extend(properties)

    def set_lens(self, lens_type: int):
        if lens_type == 0:
            self.set_perspective_lens()
        if lens_type == 1:
            self.set_ortho_lens()

    def set_perspective_lens(self, lens=None):
        # make sure to not redo same thing
        if self.current_lens_type == 0:
            return

        if lens is None:
            lens = PerspectiveLens()

        self.node().setLens(lens)
        self.current_lens_type = 0
        editor.observer.trigger("ResizeEvent")
        return lens

    def set_ortho_lens(self, lens=None):
        # make sure to not redo same thing
        if self.current_lens_type == 1:
            return

        if lens is None:
            lens = OrthographicLens()

        self.node().setLens(lens)
        self.current_lens_type = 1
        editor.observer.trigger("ResizeEvent")
        return lens
