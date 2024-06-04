from .resource import Resource
from utils import SingleTask


class RuntimeScript(Resource, SingleTask):
    def __init__(self, name, path):
        Resource.__init__(self, path)
        SingleTask.__init__(self, name)
        self.set_sort(1)
