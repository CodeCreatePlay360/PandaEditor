from game.resources.resource import Resource


class UserModule(Resource):
    def __init__(self, path, class_instance, sort_value):
        """ Class representing a Runtime User module or Editor plugin """
        Resource.__init__(self, path)

        self.class_instance = class_instance
        self.sort_value = sort_value
        self.saved_data = {}

        self.__pre_game_attrs = set()  # Represent attributes names list before entering game state,
                                       # this is necessary because user might add new attributes in on_start or update
                                       # methods, this list will be used for comparsion after game state is exited, any
                                       # attrs not is this list are removed.

    def save_data(self):
        self.saved_data.clear()
        self.__pre_game_attrs.clear()

        for name, val in self.class_instance.__dict__.items():
            self.__pre_game_attrs.add(name)

            if self.class_instance.is_serializable_attr(name, val):
                self.saved_data[name] = val

    def reload_data(self, remove_differences=False):
        new_attrs_set = set()

        if self.saved_data is not None:
            for name, val in self.class_instance.__dict__.items():
                if name in self.saved_data:  # if exists in save data then reload
                    setattr(self.class_instance, name, self.saved_data[name])
                else:
                    new_attrs_set.add(name)

        if remove_differences:
            diff = new_attrs_set.difference(self.__pre_game_attrs)
            for item in diff:
                delattr(self.class_instance, item)
                print("Removed attr {0} from module {1}".format(self.class_instance.module_name, item))

    def copy_data(self, module_other):
        module_other.save_data()
        self.saved_data = module_other.saved_data
        self.reload_data()
