import editor.utils as ed_utils
from editor.core.resource import Resource


class UserModule(Resource):
    def __init__(self, path, class_instance, sort_value):
        """ Class representing a Runtime User module or Editor plugin """
        Resource.__init__(self, path)

        self.class_instance = class_instance
        self.sort_value = sort_value
        self.saved_data = None

    def save_data(self):
        obj_data = ed_utils.ObjectData(self.class_instance.name)

        # get all attributes of module and add them to object data
        for name, val in self.class_instance.get_savable_atts():
            prop = ed_utils.EdProperty.Property(name, val)
            obj_data.add_property(prop)

        self.saved_data = obj_data

    def reload_data(self):
        if self.saved_data is not None:

            properties = self.saved_data.properties
            for name, val in properties:
                if hasattr(self.class_instance, name):
                    if not self.class_instance.is_discarded_attr(name):
                        setattr(self.class_instance, name, val)
