from panda3d.core import PerspectiveLens, OrthographicLens, Vec2
from editor.nodes.baseNp import BaseNp
from editor.utils import EdProperty
from editor.constants import obs


class EdCameraNp(BaseNp):
    def __init__(self, np, uid=None, *args, **kwargs):
        BaseNp.__init__(self, np, uid, *args, **kwargs)

        self.lens_type_map = 0  # [Lens type] 0: Perspective, 1: Ortho
        self.current_lens_type = -1
        self.lens_properties = []  # properties for a particular lens type
        self.set_perspective_lens()

    def create_properties(self):
        super(EdCameraNp, self).create_properties()

        space_prop = EdProperty.EmptySpace(0, 10)
        lens_prop_label = EdProperty.Label(name="Lens", is_bold=True)
        lens_prop = EdProperty.ChoiceProperty("LensType",
                                              choices=["Perspective", "Orthographic"],
                                              value=0,
                                              setter=self.set_lens,
                                              getter=self.get_lens_type)

        self.properties.append(space_prop)
        self.properties.append(lens_prop_label)
        self.properties.append(lens_prop)

    def set_lens(self, lens_type: int):
        if lens_type == 0:
            self.set_perspective_lens()

        if lens_type == 1:
            self.set_ortho_lens()

    def get_lens_type(self):
        return self.current_lens_type

    def get_near_far(self):
        lens = self.node().getLens()
        near_far = Vec2(0, 0)
        near_far.x = lens.get_near()
        near_far.y = lens.get_far()
        return near_far

    def ed_get_fov(self):
        return self.node().getLens().getHfov()

    def set_perspective_lens(self):
        # make sure to not redo same thing
        if self.current_lens_type == 0:
            return

        lens = PerspectiveLens()
        lens.set_fov(60)
        self.node().setLens(lens)
        self.create_perspective_lens_properties()
        self.current_lens_type = 0
        obs.trigger("ResizeEvent")

    def set_ortho_lens(self):
        # make sure to not redo same thing
        if self.current_lens_type == 1:
            return

        lens = OrthographicLens()
        lens.setFilmSize(100)
        self.node().setLens(lens)
        self.create_ortho_lens_properties()
        self.current_lens_type = 1
        obs.trigger("ResizeEvent")

    def set_near_far(self, val):
        self.node().getLens().setNearFar(val.x, val.y)

    def ed_set_fov(self, val):
        self.node().getLens().setFov(val)

    def create_perspective_lens_properties(self):
        # clear existing lens properties
        for prop in self.lens_properties:
            self.properties.remove(prop)
            continue
        self.lens_properties.clear()

        near_far = EdProperty.FuncProperty(name="Near-Far",
                                           value=self.get_near_far(),
                                           setter=self.set_near_far,
                                           getter=self.get_near_far)

        fov = EdProperty.FuncProperty(name="FieldOfView",
                                      value=self.ed_get_fov(),
                                      setter=self.ed_set_fov,
                                      getter=self.ed_get_fov)

        self.lens_properties.append(near_far)
        self.lens_properties.append(fov)

        self.properties.extend(self.lens_properties)

    def create_ortho_lens_properties(self):
        # clear existing lens properties
        for prop in self.lens_properties:
            self.properties.remove(prop)
            continue
        self.lens_properties.clear()

        near_far = EdProperty.FuncProperty(name="Near-Far",
                                           value=self.get_near_far(),
                                           setter=self.set_near_far,
                                           getter=self.get_near_far)

        film_size = EdProperty.FuncProperty(name="FilmSize",
                                            value=self.node().getLens().getFilmSize(),
                                            setter=self.node().getLens().setFilmSize,
                                            getter=self.node().getLens().getFilmSize)

        self.lens_properties.append(near_far)
        self.lens_properties.append(film_size)

        self.properties.extend(self.lens_properties)
