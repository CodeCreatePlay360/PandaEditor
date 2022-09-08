import editor.constants as constants
from editor.core.pModBase import PModBase
from editor.commandManager import Command


class EditorPlugin(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        self.__le = kwargs.pop("level_editor", None)
        self.__command_manager = kwargs.pop("command_manager", None)
        self.type = constants.EditorPlugin
        self.discarded_attrs = "_EditorPlugin__le"
        self.discarded_attrs = "_EditorPlugin__commands"
        self.__commands = []

    @property
    def le(self):
        return self.__le

    def add_command(self, command):
        if isinstance(command, Command):
            print("failed to add command")
        else:
            print("failed to add command")

    def clear_commands(self, command):
        pass
