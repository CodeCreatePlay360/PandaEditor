from editor.nodes.baseNodePath import BaseNodePath


class ModelNodePath(BaseNodePath):
    def __init__(self, np, path, uid=None):
        BaseNodePath.__init__(self, np, path, id_="__NodePath__", uid=uid)
        self.create_properties()
