import editor.utils as ed_utils
from editor.nodes.baseNodePath import BaseNodePath
from panda3d.core import LColor, LVecBase3f


class LightNp(BaseNodePath):
    def __init__(self, np, path, id_, uid=None):
        BaseNodePath.__init__(self, np, path, id_=id_, uid=uid)

        self.__ed_light_colour = LColor(1, 1, 1, 1)  # actual color(Hue), as seen, unscaled by intensity
        self.__intensity = 1.0
        self.__is_active = True

        # if np_other and np_other.hasPythonTag("PICKABLE"):
        #     np_other = np_other.getPythonTag("PICKABLE")
        #     self.__intensity = np_other.intensity
        #     self.__ed_light_colour = np_other.get_color()
        #     self.toggle_active(self.get_active())

    def create_properties(self):
        super().create_properties()

        space = ed_utils.EdProperty.EmptySpace(0, 10)
        label = ed_utils.EdProperty.Label(name="Light Properties", is_bold=True)

        colour = ed_utils.EdProperty.FuncProperty(name="Light Color",
                                                  value=self.__ed_light_colour,
                                                  setter=self.set_color,
                                                  getter=self.get_color)

        intensity = ed_utils.EdProperty.FuncProperty(name="Color intensity",
                                                     value=self.__intensity,
                                                     setter=self.set_intensity,
                                                     getter=self.get_intensity)

        is_active = ed_utils.EdProperty.FuncProperty(name="Is Active",
                                                     value=self.__is_active,
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
        self.node().setColor(color)

    def set_color(self, val):
        self.setColor(LColor(val.x, val.y, val.z, 1))
        self.__ed_light_colour = LColor(val.x, val.y, val.z, 1)

        r = val.x * self.__intensity
        g = val.y * self.__intensity
        b = val.z * self.__intensity
        self.node().setColor(LColor(r, g, b, 1))

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
        # np = NodePath(DirectionalLight("DirectionalLight"))
        LightNp.__init__(self, np, path, id_="__DirectionalLight__", uid=uid)
        self.set_scale(8)
        self.create_properties()

    def create_properties(self):
        super(EdDirectionalLight, self).create_properties()


class EdPointLight(LightNp):
    def __init__(self, np, path, uid=None):
        # np = NodePath(PointLight("PointLight"))
        LightNp.__init__(self, np, path, id_="__PointLight__", uid=uid)

        self.__attenuation = 0
        self.__attenuation_map = {
            0: LVecBase3f(1, 0, 0),
            1: LVecBase3f(0, 1, 0),
            2: LVecBase3f(0, 0, 1),
            3: LVecBase3f(0, 1, 1)
        }

        # set default value for attenuation
        if self.node().getAttenuation() in self.__attenuation_map.values():
            value = [i for i in self.__attenuation_map if self.__attenuation_map[i] == self.node().getAttenuation()]
            self.__attenuation = value[0]

        # if np_other and np.hasPythonTag("PICKABLE"):
        #     np = np.getPythonTag("PICKABLE")
        #     self.set_attenuation(np.get_attenuation())

        self.set_scale(15)
        self.create_properties()

    def create_properties(self):
        super(EdPointLight, self).create_properties()

        attenuation = ed_utils.EdProperty.ChoiceProperty(name="Attenuation",
                                                         value=self.__attenuation,
                                                         setter=self.set_attenuation,
                                                         getter=self.get_attenuation,
                                                         choices=['constant', 'linear', 'quadratic',
                                                                  'linear-quadratic'])

        self.properties.append(attenuation)

    def set_attenuation(self, val):
        self.node().setAttenuation(self.__attenuation_map[val])

    def get_attenuation(self):
        return self.__attenuation


class EdSpotLight(LightNp):
    def __init__(self, np, path, uid=None):
        # np = NodePath(Spotlight("SpotLight"))
        LightNp.__init__(self, np, path, id_="__SpotLight__", uid=uid)

        self.__attenuation = 0
        self.attenuation_map = {
            0: (1, 0, 0),
            1: (0, 1, 0),
            2: (0, 0, 1),
            3: (0, 1, 1)
        }
        # set default value for attenuation
        if self.node().getAttenuation() in self.attenuation_map.values():
            value = [i for i in self.attenuation_map if self.attenuation_map[i] == self.node().getAttenuation()]
            self.__attenuation = value[0]

        # if np_other and np.hasPythonTag("PICKABLE"):
        #     np = np.getPythonTag("PICKABLE")
        #     self.set_attenuation(np.get_attenuation())

        self.create_properties()

    def create_properties(self):
        super(EdSpotLight, self).create_properties()

        attenuation = ed_utils.EdProperty.ChoiceProperty(name="Attenuation",
                                                         value=self.__attenuation,
                                                         setter=self.set_attenuation,
                                                         getter=self.get_attenuation,
                                                         choices=['constant', 'linear', 'quadratic',
                                                                  'linear-quadratic'])

        space = ed_utils.EdProperty.EmptySpace(0, 10)
        label = ed_utils.EdProperty.Label(name="Lens", is_bold=True)

        lens = self.node().getLens()
        lens.setNearFar(0.5, 5)
        lens_props = ed_utils.EdProperty.Utils.get_properties_for_lens(lens)

        self.properties.append(attenuation)
        self.properties.append(space)
        self.properties.append(label)
        self.properties.extend(lens_props)

    def set_attenuation(self, val):
        self.node().setAttenuation(self.attenuation_map[val])

    def get_attenuation(self):
        return self.__attenuation


class EdAmbientLight(LightNp):
    def __init__(self, np, path, uid=None):
        # np = NodePath(AmbientLight("AmbientLight"))
        LightNp.__init__(self, np, path, id_="__AmbientLight__", uid=uid)
        self.create_properties()

    def create_properties(self):
        super(EdAmbientLight, self).create_properties()
