
class Resource(object):
    def __init__(self, path):
        object.__init__(self)
        self.__path = path
        self.__uid = None

    def path(self):
        return self.__path
