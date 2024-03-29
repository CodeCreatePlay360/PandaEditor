from .selection import Selection


class LevelEditor(object):
    def __init__(self, demon, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        self.demon = demon
        
        self.__selection = Selection(render=demon.engine.render,
                                     render2D=demon.engine.render2D,
                                     mwn=demon.engine.mwn,
                                     cam=demon.engine.cam)
        
        self.demon.accept("mouse1", self.on_mouse1)
        self.demon.accept("mouse1-up", self.on_mouse1_up)
        
    def on_mouse1(self):
        self.__selection.start_drag_select()
        
    def on_mouse1_up(self):
        self.__selection.stop_drag_select()
        
    def on_mouse_1_drag(self):
        pass
