import game.constants as constants

from panda3d.core import NodePath
from game.resources.runtimeModule import RuntimeModule


class Component(RuntimeModule, NodePath):
    def __init__(self, np, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)
        NodePath.__init__(self, np)

        self.module_type = constants.Component
        self.__status = constants.SCRIPT_STATUS_OK
        self.non_serialized_attrs = "_Component__status"

    def set_status(self, status: int):
        if status not in [constants.SCRIPT_STATUS_OK, constants.SCRIPT_STATUS_ERROR]:
            print("Unknown script status value {0}".format(status))
            return
        self.__status = status

    def get_status(self):
        return self.__status