from editor.commandManager import Command


class LoadModel(Command):
    def __init__(self, app, path, is_actor, *args, **kwargs):
        super(LoadModel, self).__init__(app)

        self.path = path[len(self.app.level_editor.project.project_path) + 1:]
        self.model = None
        self.is_actor = is_actor

    def do(self, *args, **kwargs):
        if self.is_actor:
            self.model = self.app.level_editor.add_actor(self.path, select=kwargs.pop("select", True))
        else:
            self.model = self.app.level_editor.load_model(self.path, select=kwargs.pop("select", True))

    def undo(self):
        self.app.level_editor.remove_nps([self.model])
