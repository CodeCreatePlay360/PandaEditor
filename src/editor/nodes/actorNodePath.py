from direct.actor.Actor import Actor
from editor.nodes.baseNodePath import BaseNodePath


class ActorNodePath(BaseNodePath, Actor):
    def __init__(self, np, uid=None, *args, **kwargs):
        BaseNodePath.__init__(self, np, uid, *args, **kwargs)
        Actor.__init__(self, np, *args, **kwargs)

    def restore_data(self):
        super(ActorNodePath, self).restore_data()
        self.stop()
        self.remove_anim_control_dict()
