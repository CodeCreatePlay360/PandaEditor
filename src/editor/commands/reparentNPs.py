from editor.commandManager import Command


class ReparentNPs(Command):
    def __init__(self, app, src_np, target_np, *args, **kwargs):
        super(ReparentNPs, self).__init__(app)

        self.src_np = src_np
        self.original_src_np_parent = src_np.get_parent()
        self.target_np = target_np

    def do(self, *args, **kwargs):
        self.app.level_editor.reparent_np(self.src_np, self.target_np)

    def undo(self):
        self.app.level_editor.reparent_np(self.src_np, self.original_src_np_parent)
