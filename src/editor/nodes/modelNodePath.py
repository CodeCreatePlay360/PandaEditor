from editor.nodes.baseNodePath import BaseNodePath


class ModelNodePath(BaseNodePath):
    def __init__(self, np, path, uid=None):
        BaseNodePath.__init__(self, np, path, id_="__NodePath__", uid=uid)
        self.create_properties()

    def get_copy(self, np):
        data = None
        if np.hasPythonTag("__GAME_OBJECT__"):
            data = ModelNodePath(np, self.path)
            self.copy_properties(np.getPythonTag("__GAME_OBJECT__"))
            np.setPythonTag("__GAME_OBJECT__", data)
        return data
