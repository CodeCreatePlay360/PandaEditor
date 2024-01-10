from system import Systems


class Game(object):
    def __init__(self, demon, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        
    def on_any_event(self, evt, *args):
        pass
