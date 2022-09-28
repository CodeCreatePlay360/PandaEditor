class ObjectRepository:
    def __init__(self):
        self.__object_dictionary = {}

    def add_object(self, name: str, obj):
        if not self.__object_dictionary.__contains__(name):
            self.__object_dictionary[name] = obj

    def remove_object(self, name):
        if self.__object_dictionary.__contains__(name):
            self.__object_dictionary.pop(name)

    def get(self, name):
        if self.__object_dictionary.__contains__(name):
            return self.__object_dictionary[name]
        return None

    def clear(self):
        self.__object_dictionary.clear()
