import game.constants as constants
from game.resources.pModBase import PModBase


class EditorPlugin(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        self.__le = kwargs.pop("level_editor", None)
        self.__command_manager = kwargs.pop("command_manager", None)
        self.__commands = {}

        self.module_type = constants.EditorPlugin

        self.non_serialized_attrs = "_EditorPlugin__le"
        self.non_serialized_attrs = "_EditorPlugin__commands"
        self.non_serialized_attrs = "_EditorPlugin__commands"

    @property
    def le(self):
        return self.__le

    @property
    def commands(self):
        return self.__commands

    def add_command(self, name, command, *args, **kwargs):
        if name not in self.le.user_commands.values():
            self.__commands[name] = (command, args, kwargs)
        else:
            print("[{0}] Failed to add command {1}".format(self.name, name))
