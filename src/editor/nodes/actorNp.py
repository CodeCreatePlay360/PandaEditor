from direct.actor.Actor import Actor
from editor.nodes.modelNp import ModelNp


class ActorNp(ModelNp, Actor):
    def __init__(self, np, uid=None, *args, **kwargs):
        ModelNp.__init__(self, np, uid)
        Actor.__init__(self, np, *args, **kwargs)

    def restore_data(self):
        super(ActorNp, self).restore_data()
        self.stop()
        self.remove_anim_control_dict()
