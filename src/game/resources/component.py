from .script import Script


class Component(Script):
    def __init__(self, path, name, np):
        Script.__init__(self, path, name)
        self.__np =  np

    def __getattr__(self, name):
        return getattr(self.__np, name)
