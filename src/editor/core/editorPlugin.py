import editor.constants as constants
from editor.core.pModBase import PModBase
from editor.commandManager import Command


class EditorPlugin(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        self.__le = kwargs.pop("level_editor", None)
        self.__command_manager = kwargs.pop("command_manager", None)
        self.__commands = {}

        self.type = constants.EditorPlugin

        self.discarded_attrs = "_EditorPlugin__le"
        self.discarded_attrs = "_EditorPlugin__commands"
        self.discarded_attrs = "_EditorPlugin__commands"

    @property
    def le(self):
        return self.__le

    @property
    def commands(self):
        return self.__commands

    def add_command(self, name, command):
        if isinstance(command, Command) and name not in self.__commands.values():
            self.__commands[name] = command
        else:
            print("[{0}] Failed to add command {1}".format(self.name, name))

    def clear_commands(self, command):
        pass

    def clear_ui(self):
        """"""
        pass
