import xml.etree.ElementTree as et
from wx import DEFAULT, SWISS


class UI_Config:
    PINK_COLOR = (253, 114, 255, 255)

    def __init__(self, config):
        self.__xml_tree = et.parse(config).getroot()
        self.__font = self.__xml_tree.find("UI").find("Font")

    def color_map(self, key: str):
        """Returns a color identified by arg 'key' from editor UI global color palette, see editor/config.xml"""

        try:
            color_str = self.__xml_tree.find("UI").find("_ColorPalette").find(key)
            colors_list = color_str.text.split(",")
        except AttributeError:
            print(1 / 0)  # replace this with editor logger
            return UI_Config.PINK_COLOR

        return self.make_color(colors_list)

    @property
    def font(self):
        if self.__font.text == "SWISS":
            return SWISS
        print("Font value not found returning platform default font value")
        return DEFAULT

    @staticmethod
    def make_color(colors_list):
        r = int(colors_list[0])
        g = int(colors_list[1])
        b = int(colors_list[2])
        a = int(colors_list[3])
        return r, g, b, a

    def widget_color(self, win: str = None, key: str = None):
        """Returns an editor UI window (identified by arg 'win') specific color (identified by arg 'key') from editor
         UI global color palette, see editor/config.xml"""

        try:
            color_str = self.__xml_tree.find("UI").find("_ColorPalette").find(win).find(key)
            colors_list = color_str.text.split(",")
        except AttributeError:
            print(1 / 0)  # replace this with editor logger
            return UI_Config.PINK_COLOR

        return self.make_color(colors_list)
