import editor.utils as EdUtils
from editor.nodes.baseNp import BaseNp
from panda3d.core import LColor


class ModelNp(BaseNp):
    def __init__(self, np, uid=None, *args, **kwargs):
        BaseNp.__init__(self, np, uid, *args, **kwargs)

    def create_properties(self):
        super().create_properties()

        space = EdUtils.EdProperty.EmptySpace(0, 10)
        label = EdUtils.EdProperty.Label(name="Node Settings", is_bold=True)
        color = EdUtils.EdProperty.FuncProperty(name="Colour", value=self.get_ed_colour(), setter=self.set_ed_colour,
                                                getter=self.get_ed_colour)

        self.properties.append(space)
        self.properties.append(label)
        self.properties.append(color)

    def create_save_data(self):
        super(ModelNp, self).create_save_data()
        self._save_data_info["Colour"] = [self.get_ed_colour, self.set_ed_colour]

    def set_ed_colour(self, val):
        r = EdUtils.common_maths.map_to_range(0, 255, 0, 1, val.x)
        g = EdUtils.common_maths.map_to_range(0, 255, 0, 1, val.y)
        b = EdUtils.common_maths.map_to_range(0, 255, 0, 1, val.z)
        a = EdUtils.common_maths.map_to_range(0, 255, 0, 1, val.w)

        color = LColor(r, g, b, a)
        self.setColor(color)

    def get_ed_colour(self):
        val = self.getColor()

        r = EdUtils.common_maths.map_to_range(0, 1, 0, 255, val.x)
        g = EdUtils.common_maths.map_to_range(0, 1, 0, 255, val.y)
        b = EdUtils.common_maths.map_to_range(0, 1, 0, 255, val.z)
        a = EdUtils.common_maths.map_to_range(0, 1, 0, 255, val.w)

        color = LColor(r, g, b, a)
        return color
