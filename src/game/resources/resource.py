import uuid


class Resource:
    def __init__(self, path, *args, **kwargs):
        """class representing an editor resource"""
        self.__uuid = uuid.uuid4()
        self.path = path

    @property
    def uuid(self):
        return self.__uuid
