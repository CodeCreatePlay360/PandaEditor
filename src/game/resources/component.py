from utils import SingleTask


class Component(SingleTask):
    def __init__(self, *args, **kwargs):
        SingleTask.__init__(self, *args, **kwargs)
