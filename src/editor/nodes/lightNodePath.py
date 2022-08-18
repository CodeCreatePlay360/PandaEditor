import editor.utils as ed_utils
from editor.nodes.baseNodePath import BaseNodePath
from panda3d.core import LColor, PerspectiveLens


class LightNp(BaseNodePath):
    def __init__(self, np, uid=None, *args, **kwargs):
        self.intensity = 1.0

        # this attribute is the actual pure color(Hue), as seen, unscaled by intensity
        self.ed_light_colour = LColor(255, 255, 255, 255)
        self.is_active = True

        BaseNodePath.__init__(self, np, uid, *args, **kwargs)

        self.set_color(self.ed_light_colour)
        self.setScale(4)

    def clear_light(self):
        pass

    def create_properties(self):
        super().create_properties()

        space = ed_utils.EdProperty.EmptySpace(0, 10)
        label = ed_utils.EdProperty.Label(name="Light Properties", is_bold=True)

        colour = ed_utils.EdProperty.FuncProperty(name="Light Color", value=self.get_color(),
                                                  setter=self.set_color, getter=self.get_color)

        intensity = ed_utils.EdProperty.FuncProperty(name="Color intensity", value=self.intensity,
                                                     setter=self.set_intensity, getter=self.get_intensity)

        is_active = ed_utils.EdProperty.FuncProperty(name="Is Active", value=self.is_active,
                                                     setter=self.toggle_active, getter=self.get_active_status)

        self.properties.append(space)
        self.properties.append(label)
        self.properties.append(colour)
        self.properties.append(intensity)
        self.properties.append(is_active)

    def create_save_data(self):
        super(LightNp, self).create_save_data()
        self._save_data_info["EdLightColour"] = [self.get_color, self.set_color]
        self._save_data_info["EdLightIntensity"] = [self.get_intensity, self.set_intensity]

    def set_intensity(self, val):
        if not self.is_active:
            self.intensity = 0
        else:
            self.intensity = val

        # update light color according to intensity
        r = ed_utils.common_maths.map_to_range(0, 255, 0, 1, self.ed_light_colour.x)
        g = ed_utils.common_maths.map_to_range(0, 255, 0, 1, self.ed_light_colour.y)
        b = ed_utils.common_maths.map_to_range(0, 255, 0, 1, self.ed_light_colour.z)

        color = LColor(r, g, b, 1)

        r = color.x * self.intensity
        g = color.y * self.intensity
        b = color.z * self.intensity

        color = LColor(r, g, b, 1)
        self.node().setColor(color)

    def set_color(self, val):
        self.ed_light_colour = val

        # convert to panda3d colour range
        r = ed_utils.common_maths.map_to_range(0, 255, 0, 1, self.ed_light_colour.x)
        g = ed_utils.common_maths.map_to_range(0, 255, 0, 1, self.ed_light_colour.y)
        b = ed_utils.common_maths.map_to_range(0, 255, 0, 1, self.ed_light_colour.z)
        self.setColor(LColor(r, g, b, 1))

        r = r * self.intensity
        g = g * self.intensity
        b = b * self.intensity
        self.node().setColor(LColor(r, g, b, 1))

    def toggle_active(self, val):
        self.is_active = val
        if not self.is_active:
            self.set_intensity(0)

    def get_light(self):
        return self.node()

    def get_intensity(self):
        return self.intensity

    def get_color(self):
        return self.ed_light_colour

    def get_active_status(self):
        return self.is_active

    def on_remove(self):
        super().on_remove()


class EdDirectionalLight(LightNp):
    def __init__(self, *args, **kwargs):
        LightNp.__init__(self, *args, **kwargs)
        self.set_scale(8)

    def create_properties(self):
        super(EdDirectionalLight, self).create_properties()


class EdPointLight(LightNp):
    def __init__(self, *args, **kwargs):
        LightNp.__init__(self, *args, **kwargs)
        self.set_scale(15)

        self.attenuation = 0
        self.node().attenuation = (1, 0, 0)
        self.attenuation_map = {
            0: (1, 0, 0),
            1: (0, 1, 0),
            2: (0, 0, 1),
            3: (0, 1, 1)
        }

    def create_properties(self):
        super(EdPointLight, self).create_properties()

        attenuation = ed_utils.EdProperty.ChoiceProperty(name="Attenuation",
                                                         setter=self.set_attenuation,
                                                         getter=self.get_attenuation,
                                                         choices=['constant', 'linear', 'quadratic', 'linear-quadratic'])
        self.properties.append(attenuation)

    def get_attenuation(self):
        return self.attenuation

    def set_attenuation(self, val):
        self.node().setAttenuation(self.attenuation_map[val])
        self.attenuation = val


class EdSpotLight(LightNp):
    def __init__(self, *args, **kwargs):
        # create a lens
        self.lens = PerspectiveLens()
        self.lens.setFov(2)
        self.lens.setNear(0.1)
        self.lens.setFar(2)

        LightNp.__init__(self, *args, **kwargs)

        self.node().setLens(self.lens)
        self.node().setExponent(4)

        self.attenuation = 0
        self.node().attenuation = (1, 0, 0)
        self.attenuation_map = {
            0: (1, 0, 0),
            1: (0, 1, 0),
            2: (0, 0, 1),
            3: (0, 1, 1)
        }

    def create_properties(self):
        super(EdSpotLight, self).create_properties()

        attenuation = ed_utils.EdProperty.ChoiceProperty(name="Attenuation",
                                                         setter=self.set_attenuation,
                                                         getter=self.get_attenuation,
                                                         choices=['constant', 'linear', 'quadratic', 'linear-quadratic'])

        fov = ed_utils.EdProperty.FuncProperty(name="FOV(SpotAngel)",
                                               value=self.lens.getFov(),
                                               setter=self.lens.setFov,
                                               getter=self.lens.getFov)

        self.properties.append(attenuation)
        self.properties.append(fov)

    def get_attenuation(self):
        return self.attenuation

    def set_attenuation(self, val):
        self.node().attenuation = self.attenuation_map[val]
        self.attenuation = val


class EdAmbientLight(LightNp):
    def __init__(self, *args, **kwargs):
        LightNp.__init__(self, *args, **kwargs)

    def create_properties(self):
        super(EdAmbientLight, self).create_properties()
