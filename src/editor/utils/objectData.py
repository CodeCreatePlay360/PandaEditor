
class ObjectData:
    def __init__(self, obj_name):
        """Represents an object and a list of its attributes"""

        self.__obj_name = obj_name
        self.__attrs = []

    def add_attr(self, attr_name: str, value):
        self.__attrs.append((attr_name, value))

    @property
    def obj_name(self):
        return self.__obj_name

    @property
    def saved_attrs(self):
        return self.__attrs
