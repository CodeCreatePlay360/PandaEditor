from panda3d.core import PerspectiveLens, OrthographicLens
from commons import EditorProperty
from editor.globals import editor
from game.nodes.baseNodePath import BaseNodePath


class CameraNodePath(BaseNodePath):
    def __init__(self, np, path, uid=None):
        BaseNodePath.__init__(self, np, path, id_="__CameraNodePath__", uid=uid)

        self.current_lens_type = 0  # 0: Perspective, 1: Ortho

        self.set_lens(0)
        self.create_properties()

    def create_properties(self):
        super(CameraNodePath, self).create_properties()

        space_prop = EditorProperty.EmptySpace(0, 10)
        lens_prop_label = EditorProperty.Label(name="Lens", is_bold=True)
        lens_type = EditorProperty.ChoiceProperty("Lens Type",
                                                  choices=["Perspective", "Orthographic"],
                                                  initial_value=0,
                                                  setter=self.set_lens,
                                                  getter=lambda: self.current_lens_type)

        # remove color property for camera
        for prop in self.properties:
            if prop.name == "Color":
                self.properties.remove(prop)

        self.properties.append(space_prop)
        self.properties.append(lens_prop_label)
        self.properties.append(lens_type)

        lens = self.np.node().getLens()
        properties = EditorProperty.Utils.get_properties_for_lens(lens)
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

        self.np.node().setLens(lens)
        self.current_lens_type = 0
        editor.observer.trigger("ResizeEvent")
        return lens

    def set_ortho_lens(self, lens=None):
        # make sure to not redo same thing
        if self.current_lens_type == 1:
            return

        if lens is None:
            lens = OrthographicLens()

        self.np.node().setLens(lens)
        self.current_lens_type = 1
        editor.observer.trigger("ResizeEvent")
        return lens

    def get_copy(self, np):
        data = None
        if np.hasPythonTag("__GAME_OBJECT__"):
            data = CameraNodePath(np, self.path)
            self.copy_properties(np.getPythonTag("__GAME_OBJECT__"))
            np.setPythonTag("__GAME_OBJECT__", data)
        return data
