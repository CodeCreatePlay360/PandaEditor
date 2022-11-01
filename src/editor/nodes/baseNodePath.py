import uuid
from panda3d.core import NodePath
from panda3d.core import LVecBase3f, LColor
from editor.utils import EdProperty, common_maths


class BaseNodePath(NodePath):
    def __init__(self, np, path, id_, uid=None):
        NodePath.__init__(self, np)
        self.setColor(LColor(1, 1, 1, 1))

        self.__np = np
        self.__id = id_
        self.__path = path  # path this resource is loaded from
        self.__uuid = uid if uid is not None else uuid.uuid4().__str__()
        self.__properties = []
        self.__components = {}  # self.components["full_path"] = component object

    def create_properties(self):
        self.__properties.clear()

        label = EdProperty.Label(name="Transform", is_bold=True)

        pos = EdProperty.FuncProperty(name="Position ",
                                      value=self.getPos(),
                                      setter=self.setPos,
                                      getter=self.getPos)

        rot = EdProperty.FuncProperty(name="Rotation ",
                                      value=self.getHpr(),
                                      setter=self.setHpr,
                                      getter=self.getHpr)

        scale = EdProperty.FuncProperty(name="Scale      ",
                                        value=self.getScale(),
                                        value_limit=LVecBase3f(0.01, 0.01, 0.01),
                                        setter=self.set_scale,
                                        getter=self.getScale)

        self.__properties.append(label)
        self.__properties.append(pos)
        self.__properties.append(rot)
        self.__properties.append(scale)

        space = EdProperty.EmptySpace(0, 10)
        label = EdProperty.Label(name="Node Properties", is_bold=True)
        color = EdProperty.FuncProperty(name="Color",
                                        value=self.get_ed_colour(),
                                        setter=lambda val: self.setColor(val),
                                        getter=self.get_ed_colour)

        self.__properties.append(space)
        self.__properties.append(label)
        self.__properties.append(color)

    def copy_properties(self, np_other):
        properties = np_other.get_properties()

        for i in range(len(properties)):
            if i < len(self.__properties):
                self.__properties[i].set_value(properties[i].get_value())

    def get_properties(self):
        return self.__properties

    def get_ed_colour(self):
        if self.hasColor():
            val = self.getColor()
        else:
            val = LColor(1, 1, 1, 1)

        return val

    def attach_component(self, path, component):
        if not self.__components.__contains__(path):
            self.__components[path] = component
            # print("Component: [{0}] attached to [{1}]".format(component, self.name))
        else:
            print("Warning: Attempt to attach multiple Components of same type... "
                  "Component: [{0}] is already attached to [{1}] !".format(path, self.name))

    def detach_component(self, path):
        if self.__components.__contains__(path):
            del self.__components[path]

    def clear_components(self):
        print("Cleared all Components on {0}".format(self.name))
        self.__components.clear()

    @property
    def np(self):
        return self.__np

    @property
    def id(self):
        return self.__id

    @property
    def path(self):
        return self.__path

    @property
    def uid(self):
        return self.__uuid

    @property
    def properties(self):
        return self.__properties

    @property
    def components(self):
        return self.__components
