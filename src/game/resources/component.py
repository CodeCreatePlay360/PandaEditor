from utils import SingleTask
from .resource import Resource


class Component(Resource, SingleTask):
    def __init__(self, name, path, np):
        Resource.__init__(self, path)
        SingleTask.__init__(self, name)
        self.__np =  np
        self.set_sort(1)

    def __getattr__(self, name):
        return getattr(self.__np, name)

    def is_init(self):
        return self.__is_init
