from panda3d.core import NodePath, LColor, LVecBase3f
from commons import EditorProperty
from game.nodes.baseNodePath import BaseNodePath


class LightNp(BaseNodePath):
    def __init__(self, np, path, id_, uid=None):
        BaseNodePath.__init__(self, np, path, id_=id_, uid=uid)
        self.__ed_light_colour = LColor(1, 1, 1, 1)  # actual color(Hue), as seen, unscaled by intensity
        self.__intensity = 1.0
        self.__is_active = True

    def create_properties(self):
        super().create_properties()

        space = EditorProperty.EmptySpace(0, 10)
        label = EditorProperty.Label(name="Light Properties", is_bold=True)

        colour = EditorProperty.FuncProperty(name="Light Color",
                                                  initial_value=self.__ed_light_colour,
                                                  setter=self.set_light_color,
                                                  getter=self.np.get_color)

        intensity = EditorProperty.FuncProperty(name="Color intensity",
                                                     initial_value=self.__intensity,
                                                     setter=self.set_intensity,
                                                     getter=self.get_intensity)

        is_active = EditorProperty.FuncProperty(name="Is Active",
                                                     initial_value=self.__is_active,
                                                     setter=self.toggle_active,
                                                     getter=self.get_active)

        self.properties.append(space)
        self.properties.append(label)
        self.properties.append(colour)
        self.properties.append(intensity)
        self.properties.append(is_active)

    def set_intensity(self, val):
        if not self.__is_active:
            self.__intensity = 0.0
        else:
            self.__intensity = val

        r = self.__ed_light_colour.x * self.__intensity
        g = self.__ed_light_colour.y * self.__intensity
        b = self.__ed_light_colour.z * self.__intensity
        color = LColor(r, g, b, 1)
        self.np.node().setColor(color)

    def set_light_color(self, val):
        self.np.setColor(LColor(val.x, val.y, val.z, 1))
        self.__ed_light_colour = LColor(val.x, val.y, val.z, 1)
        r = val.x * self.__intensity
        g = val.y * self.__intensity
        b = val.z * self.__intensity
        self.np.node().setColor(LColor(r, g, b, 1))

    def toggle_active(self, val):
        self.__is_active = val
        if not self.__is_active:
            self.set_intensity(0.0)

    def get_active(self):
        return self.__is_active

    def get_intensity(self):
        return self.__intensity

    @property
    def intensity(self):
        return self.__intensity


class EdDirectionalLight(LightNp):
    def __init__(self, np, path, uid=None):
        LightNp.__init__(self, np, path, id_="__DirectionalLight__", uid=uid)
        self.create_properties()

    def create_properties(self):
        super(EdDirectionalLight, self).create_properties()

    def get_copy(self, np):
        data = None
        if np.hasPythonTag("__GAME_OBJECT__"):
            data = EdDirectionalLight(np, self.path)
            self.copy_properties(np.getPythonTag("__GAME_OBJECT__"))
            np.setPythonTag("__GAME_OBJECT__", data)
        return data


class EdPointLight(LightNp):
    def __init__(self, np, path, uid=None):
        LightNp.__init__(self, np, path, id_="__PointLight__", uid=uid)

        self.__attenuation = 0
        self.__attenuation_map = {
            0: LVecBase3f(1, 0, 0),
            1: LVecBase3f(0, 1, 0),
            2: LVecBase3f(0, 0, 1),
            3: LVecBase3f(0, 1, 1)
        }

        # set default value for attenuation
        if self.np.node().getAttenuation() in self.__attenuation_map.values():
            value = [i for i in self.__attenuation_map if self.__attenuation_map[i] == self.np.node().getAttenuation()]
            self.__attenuation = value[0]

        self.create_properties()

    def create_properties(self):
        super(EdPointLight, self).create_properties()

        attenuation = EditorProperty.ChoiceProperty(name="Attenuation",
                                                         initial_value=self.__attenuation,
                                                         setter=self.set_attenuation,
                                                         getter=self.get_attenuation,
                                                         choices=['constant', 'linear', 'quadratic',
                                                                  'linear-quadratic'])

        self.properties.append(attenuation)

    def set_attenuation(self, val):
        self.__attenuation = val
        self.np.node().setAttenuation(self.__attenuation_map[val])

    def get_attenuation(self):
        return self.__attenuation

    def get_copy(self, np):
        data = None
        if np.hasPythonTag("__GAME_OBJECT__"):
            data = EdPointLight(np, self.path)
            self.copy_properties(np.getPythonTag("__GAME_OBJECT__"))
            np.setPythonTag("__GAME_OBJECT__", data)
        return data


class EdSpotLight(LightNp):
    def __init__(self, np, path, uid=None):
        LightNp.__init__(self, np, path, id_="__SpotLight__", uid=uid)

        self.__attenuation = 0
        self.attenuation_map = {
            0: (1, 0, 0),
            1: (0, 1, 0),
            2: (0, 0, 1),
            3: (0, 1, 1)
        }
        # set default value for attenuation
        if self.np.node().getAttenuation() in self.attenuation_map.values():
            value = [i for i in self.attenuation_map if self.attenuation_map[i] == self.np.node().getAttenuation()]
            self.__attenuation = value[0]

        self.create_properties()

    def create_properties(self):
        super(EdSpotLight, self).create_properties()

        attenuation = EditorProperty.ChoiceProperty(name="Attenuation",
                                                         initial_value=self.__attenuation,
                                                         setter=self.set_attenuation,
                                                         getter=self.get_attenuation,
                                                         choices=['constant', 'linear', 'quadratic',
                                                                  'linear-quadratic'])

        space = EditorProperty.EmptySpace(0, 10)
        label = EditorProperty.Label(name="Lens", is_bold=True)

        lens = self.np.node().getLens()
        lens.setNearFar(0.5, 5)
        lens_props = EditorProperty.Utils.get_properties_for_lens(lens)

        self.properties.append(attenuation)
        self.properties.append(space)
        self.properties.append(label)
        self.properties.extend(lens_props)

    def set_attenuation(self, val):
        self.__attenuation = val
        self.np.node().setAttenuation(self.attenuation_map[val])

    def get_attenuation(self):
        return self.__attenuation

    def get_copy(self, np):
        data = None
        if np.hasPythonTag("__GAME_OBJECT__"):
            data = EdSpotLight(np, self.path)
            self.copy_properties(np.getPythonTag("__GAME_OBJECT__"))
            np.setPythonTag("__GAME_OBJECT__", data)
        return data


class EdAmbientLight(LightNp):
    def __init__(self, np, path, uid=None):
        LightNp.__init__(self, np, path, id_="__AmbientLight__", uid=uid)
        self.create_properties()

    def create_properties(self):
        super(EdAmbientLight, self).create_properties()

    def get_copy(self, np):
        data = None
        if np.hasPythonTag("__GAME_OBJECT__"):
            data = EdAmbientLight(np, self.path)
            self.copy_properties(np.getPythonTag("__GAME_OBJECT__"))
            np.setPythonTag("__GAME_OBJECT__", data)
        return data
