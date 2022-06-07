import editor.constants as constants
from editor.commandManager import Command


class RenameNPs(Command):
    def __init__(self, app, np, old_name, new_name, *args, **kwargs):
        super(RenameNPs, self).__init__(app)

        self.np = np
        self.old_name = old_name
        self.new_name = new_name

    def do(self, *args, **kwargs):
        self.np.set_name(self.new_name)
        constants.obs.trigger("OnRenameNPs", self.np, self.new_name)

    def undo(self):
        self.np.set_name(self.old_name)
        constants.obs.trigger("OnRenameNPs", self.np, self.old_name)
