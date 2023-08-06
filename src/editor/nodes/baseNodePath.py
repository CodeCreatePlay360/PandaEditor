import uuid
from panda3d.core import LVecBase3f
from editor.utils import EdProperty, common_maths


class BaseNodePath:
    def __init__(self, np, path, id_, uid=None):
        self.__np = np
        self.__path = path  # path this resource is loaded from
        self.__id = id_
        self.__uuid = uid if uid is not None else uuid.uuid4().__str__()
        self.__properties = []
        self.__components = {}  # self.components["full_path"] = component object, this works because path is
                                # guaranteed to be unique

    def create_properties(self):
        self.__properties.clear()

        label = EdProperty.Label(name="Transform", is_bold=True)

        pos = EdProperty.FuncProperty(name="Position ",
                                      value=self.np.getPos(),
                                      setter=self.np.setPos,
                                      getter=self.np.getPos)

        rot = EdProperty.FuncProperty(name="Rotation ",
                                      value=self.np.getHpr(),
                                      setter=self.np.setHpr,
                                      getter=self.np.getHpr)

        scale = EdProperty.FuncProperty(name="Scale      ",
                                        value=self.np.getScale(),
                                        value_limit=LVecBase3f(0.01, 0.01, 0.01),
                                        setter=self.np.set_scale,
                                        getter=self.np.getScale)

        self.__properties.append(label)
        self.__properties.append(pos)
        self.__properties.append(rot)
        self.__properties.append(scale)

        space = EdProperty.EmptySpace(0, 10)
        label = EdProperty.Label(name="Node Properties", is_bold=True)
        color = EdProperty.FuncProperty(name="Color",
                                        value=self.np.get_color(),
                                        setter=lambda val: self.np.setColor(val, 1),
                                        getter=self.np.getColor)

        self.__properties.append(space)
        self.__properties.append(label)
        self.__properties.append(color)

    def copy_properties(self, np_other):
        properties = np_other.get_properties()

        for i in range(len(properties)):
            if i < len(self.__properties):
                self.__properties[i].set_value(properties[i].get_value())

    def clear_components(self):
        # print("Cleared all Components on {0}".format(self.name))
        self.__components.clear()

    def attach_component(self, path, component):
        if not self.__components.__contains__(path):
            self.__components[path] = component
            # print("Component: [{0}] attached to [{1}]".format(component, self.name))
        else:
            print("Warning: Attempt to attach multiple Components of same type... "
                  "Component: [{0}] is already attached to [{1}] !".format(path, self.np.name))

    def detach_component(self, path):
        if self.__components.__contains__(path):
            del self.__components[path]

    def get_component(self, path):
        return self.__components.get(path)

    def get_properties(self):
        return self.__properties

    def get_copy(self, np):
        pass

    @property
    def np(self):
        return self.__np

    @property
    def ed_id(self):
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
