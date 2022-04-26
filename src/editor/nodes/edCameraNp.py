from editor.nodes.baseNp import BaseNp


class EdCameraNp(BaseNp):
    def __init__(self, np, uid=None):
        BaseNp.__init__(self, np, uid)
        self.set_scale(8)
