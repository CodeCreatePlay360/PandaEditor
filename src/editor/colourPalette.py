from editor.constants import object_manager


class ColourPalette:
    # some global colours
    NORMAL_GREY = (100, 100, 100, 255)
    LIGHT_GREY = (200, 200, 200, 255)
    DARK_GREY = (80, 80, 80, 255)
    EDITOR_TEXT_COLOR = (255, 255, 190, 255)
    
    def __init__(self, *args):
        object_manager.add_object("ColourPalette", self)
        self.colours = []
        
    def add_colour(self, colour):
        pass

    def remove_colour(self, colour):
        pass
        
    def get_normalize_colour(self, colour):
        pass

    def get_colour(self, c):
        pass

    def get_colours(self):
        pass
