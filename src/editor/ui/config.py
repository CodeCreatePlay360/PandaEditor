import xml.etree.ElementTree as et
from wx import DEFAULT, SWISS


class UI_Config:
    def __init__(self, config):
        self.__config = et.parse(config)

        win32_elements = self.__config.find("./UI[@platform='any']")
        color_palette = win32_elements.find("ColorPalette")

        self.__ed_font = win32_elements.find("Font")

        self.__map_ = {"Panel_Light": [],
                       "Panel_Normal": [],
                       "Panel_Dark": [],

                       "Text_Primary": [],
                       "Text_Secondary": [],

                       "Resource_Image_Tile_Sel": []}

        self.populate_from_elm(elem=color_palette)

    def populate_from_elm(self, elem):
        last_tag = None
        for elem in elem:
            colors = elem.text.split(",")
            for val in colors:
                try:
                    val_ = int(val)
                    if self.__map_.__contains__(elem.tag):
                        self.__map_[elem.tag].append(val_)
                        if last_tag != elem.tag:
                            if last_tag is not None:
                                self.__map_[last_tag] = tuple(self.__map_[last_tag])
                            last_tag = elem.tag
                except ValueError:
                    continue

    def color_map(self, key):
        if self.__map_.__contains__(key):
            # print("Key {0} Value {1}".format(key, self.__map_[key]))
            return self.__map_[key]
        else:
            print("Key {0} not found in EditorConfig/ColorPalette".format(key))
            return 0, 0, 0, 255

    @property
    def ed_font(self):
        if self.__ed_font.text == "SWISS":
            return SWISS
        print("Font value not found returning platform default font value")
        return DEFAULT

    def reset(self):
        pass
