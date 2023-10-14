from direct.actor.Actor import Actor
from game.nodes.baseNodePath import BaseNodePath


class ActorNodePath(BaseNodePath, Actor):
    def __init__(self, path, uid=None, actor_other=None, **kwargs):
        if actor_other:
            Actor.__init__(self, actor_other)
        else:
            Actor.__init__(self, path)

        tag = kwargs.pop("tag", None)
        if tag:
            self.setPythonTag(tag, self)

        BaseNodePath.__init__(self, self, path, id_="__ActorNodePath__", uid=uid)
        self.create_properties()
