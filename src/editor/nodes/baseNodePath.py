import editor.utils as ed_utils
import uuid
from panda3d.core import NodePath
from panda3d.core import Vec3, LColor


class BaseNodePath(NodePath):
    def __init__(self, np, uid=None, copy=False, *args, **kwargs):
        NodePath.__init__(self, np)

        self._id = "__NodePath__"
        self.__tag = "default"

        self.path = kwargs.pop("path", None)  # path this resource is loaded from
        create_properties = kwargs.pop("create_properties", True)

        self.__uuid = uid if uid is not None else uuid.uuid4().__str__()
        self.properties = []
        self._save_data_info = {}
        self._save_data = []

        if create_properties:
            self.create_properties()

    def create_properties(self):
        label = ed_utils.EdProperty.Label(name="Transform", is_bold=True)

        pos = ed_utils.EdProperty.FuncProperty(name="Position ",
                                               value=self.getPos(),
                                               setter=self.setPos,
                                               getter=self.getPos)

        rot = ed_utils.EdProperty.FuncProperty(name="Rotation ",
                                               value=self.getHpr(),
                                               setter=self.setHpr,
                                               getter=self.getHpr)

        scale = ed_utils.EdProperty.FuncProperty(name="Scale      ",
                                                 value=self.getScale(),
                                                 value_limit=Vec3(0.01, 0.01, 0.01),
                                                 setter=self.set_scale,
                                                 getter=self.getScale)

        self.properties.append(label)
        self.properties.append(pos)
        self.properties.append(rot)
        self.properties.append(scale)

        space = ed_utils.EdProperty.EmptySpace(0, 10)
        label = ed_utils.EdProperty.Label(name="Node Properties", is_bold=True)
        color = ed_utils.EdProperty.FuncProperty(name="Color", value=self.get_ed_colour(), setter=self.set_ed_colour,
                                                 getter=self.get_ed_colour)

        self.properties.append(space)
        self.properties.append(label)
        self.properties.append(color)

    def get_properties(self):
        return self.properties

    def update_properties(self):
        for prop in self.properties:
            if prop._type == "label" or prop._type == "space":
                continue
            x = prop.getter
            if x:
                prop.set_value(x())
            else:
                prop.set_value(getattr(self, prop.get_name()))

    def on_property_modified(self, prop, value):
        x = prop.setter
        x(self, value)

    def set_ed_colour(self, val):
        r = ed_utils.common_maths.map_to_range(0, 255, 0, 1, val.x)
        g = ed_utils.common_maths.map_to_range(0, 255, 0, 1, val.y)
        b = ed_utils.common_maths.map_to_range(0, 255, 0, 1, val.z)
        a = ed_utils.common_maths.map_to_range(0, 255, 0, 1, val.w)

        color = LColor(r, g, b, a)
        self.setColor(color)

    def get_ed_colour(self):
        if self.hasColor():
            val = self.getColor()
        else:
            val = LColor(1, 1, 1, 1)

        r = ed_utils.common_maths.map_to_range(0, 1, 0, 255, val.x)
        g = ed_utils.common_maths.map_to_range(0, 1, 0, 255, val.y)
        b = ed_utils.common_maths.map_to_range(0, 1, 0, 255, val.z)
        a = ed_utils.common_maths.map_to_range(0, 1, 0, 255, val.w)

        color = LColor(r, g, b, a)
        return color

    def has_ed_property(self, name: str):
        for prop in self.properties:
            if prop.name == name:
                return True
        return False

    @property
    def id(self):
        return self._id

    @property
    def tag(self):
        return self.__tag

    @property
    def uid(self):
        return self.__uuid

    @tag.setter
    def tag(self, value):
        self.__tag = value
