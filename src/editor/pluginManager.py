
class PluginsManager:
    def __init__(self):
        self.plugins = []
        self.properties = []

    def get_properties(self):
        return self.properties

    def has_ed_property(self, prop_name):
        for prop in self.properties:
            if prop.name == prop_name:
                return True
        return False
