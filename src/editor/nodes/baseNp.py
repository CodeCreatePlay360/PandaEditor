import editor.utils as ed_utils
from panda3d.core import NodePath
from panda3d.core import Vec3


class BaseNp(NodePath):
    def __init__(self, np, uid=None):
        NodePath.__init__(self, np)

        self.uid = uid

        self._task = None

        self.properties = []
        self._save_data_info = {}
        self._save_data = []

        self.create_properties()
        self.create_save_data()

        self.setPythonTag("PICKABLE", self)

    def create_properties(self):
        name = ed_utils.EdProperty.FuncProperty(name="Name      ",
                                                value=self.get_name(),
                                                setter=self.set_name,
                                                getter=self.get_name)

        pos = ed_utils.EdProperty.FuncProperty(name="Position",
                                               value=self.getPos(),
                                               setter=self.setPos,
                                               getter=self.getPos)

        rot = ed_utils.EdProperty.FuncProperty(name="Rotation",
                                               value=self.getHpr(),
                                               setter=self.setHpr,
                                               getter=self.getHpr)

        scale = ed_utils.EdProperty.FuncProperty(name="Scale    ",
                                                 value=self.getScale(),
                                                 value_limit=Vec3(0.01, 0.01, 0.01),
                                                 setter=self.set_scale,
                                                 getter=self.getScale)

        # self.properties.append(name)
        self.properties.append(pos)
        self.properties.append(rot)
        self.properties.append(scale)

    def create_save_data(self):
        # format = save_data["variable"] = [value or getter, setter]
        self._save_data_info["Pos"] = [self.getPos, self.setPos]
        self._save_data_info["Rot"] = [self.getHpr, self.setHpr]
        self._save_data_info["Scale"] = [self.getScale, self.setScale]
        self._save_data_info["Parent"] = [self.get_parent, self.reparent_to]

    def save_data(self):
        self._save_data.clear()

        for key in self._save_data_info.keys():
            prop = ed_utils.EdProperty.FuncProperty(name=key,
                                                    value=self._save_data_info[key][0](),
                                                    setter=self._save_data_info[key][1])
            self._save_data.append(prop)

    def restore_data(self):
        for prop in self._save_data:
            setter = prop.setter
            setter(prop.val)

        self.update_properties()

    def get_properties(self):
        return self.properties

    def update_properties(self):
        for prop in self.properties:
            x = prop.getter
            if x:
                prop.set_value(x())
            else:
                prop.set_value(getattr(self, prop.get_name()))

    def on_property_modified(self, prop, value):
        x = prop.setter
        x(self, value)

    def on_remove(self):
        pass
