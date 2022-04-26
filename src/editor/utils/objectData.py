
class ObjectData:
    def __init__(self, obj_name):
        self.obj_name = obj_name
        self.properties = []

    def add_property(self, prop):
        self.properties.append((prop.get_name(), prop.get_value()))
