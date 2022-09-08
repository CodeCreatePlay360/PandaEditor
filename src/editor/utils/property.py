from panda3d.core import Vec3, Vec2, LVecBase2f, PerspectiveLens, OrthographicLens
from editor.utils.exceptionHandler import try_execute, try_execute_1


class Property:
    def __init__(self, name, value, value_limit=None, _type=None, *args, **kwargs):
        self.name = name
        self.val = value
        self._type = _type
        self.value_limit = value_limit
        self.kwargs = kwargs

        self.is_valid = False
        self.error_message = ""

        if _type is None:
            self._type = type(value)
        else:
            self._type = _type

        self.acceptable_value_limit_types = [int, float, Vec2, Vec3]

    def get_name(self):
        return self.name

    def get_value(self):
        return self.val

    def get_type(self):
        return self._type

    def set_value(self, val):
        self.val = val

    def set_name(self, name: str):
        self.name = name

    def validate(self):
        if type(self.name) is not str:
            self.is_valid = False
            return

        if self.value_limit is not None:
            if type(self.value_limit) in self.acceptable_value_limit_types:
                pass
            else:
                print("Property --> failed to varify property {0}, limit_value must be of type"
                      "int, float, Vec2, Vec3".format(self.name))
                self.is_valid = False
                return

        self.is_valid = True


class ObjProperty(Property):
    def __init__(self, name, value, obj, _type=None, value_limit=None, **kwargs):
        super().__init__(name=name, value=value, _type=_type, value_limit=value_limit, **kwargs)

        self.obj = obj

    def validate(self):
        super().validate()

        if hasattr(self.obj, self.name):
            self.is_valid = True
        else:
            self.is_valid = False

    def set_value(self, val):
        setattr(self.obj, self.name, val)

    def get_value(self):
        return getattr(self.obj, self.name)


class FuncProperty(Property):
    def __init__(self, name, value, value_limit=None, _type=None, setter=None, getter=None, **kwargs):
        super().__init__(name=name, value=value, _type=_type, value_limit=value_limit, **kwargs)

        self.setter = setter
        self.getter = getter

    def validate(self):
        super().validate()

        if self.setter is None or self.getter is None:
            self.is_valid = False
        else:
            self.is_valid = True

    def get_value(self, *args, **kwargs):
        getter = self.getter
        return try_execute_1(getter)

    def set_value(self, val, *args, **kwargs):
        try_execute(self.setter, val, *args, **kwargs)


class EmptySpace(Property):
    def __init__(self, x, y, **kwargs):
        super().__init__(name="", value=None, _type="space", **kwargs)

        self.space_x = x  # horizontal spacing
        self.space_y = y  # vertical spacing

    def validate(self):
        super().validate()

        if type(self.space_x) is not int or type(self.space_y) is not int:
            self.is_valid = False
        else:
            self.is_valid = True


class Label(Property):
    def __init__(self, name, is_bold=False, text_color=None, **kwargs):
        super().__init__(name=name, value=None, _type="label", **kwargs)

        self.is_bold = is_bold
        self.text_color = text_color

    def validate(self):
        super().validate()

        if type(self.is_bold) is not bool:
            self.is_valid = False
        else:
            self.is_valid = True


class ButtonProperty(Property):
    def __init__(self, name, func, **kwargs):
        self.func = func

        super().__init__(name=name, value=None, _type="button", **kwargs)

    def validate(self):
        if self.func is None:
            self.is_valid = False
            return

        super().validate()

    def get_func(self):
        return self.func

    def execute(self):
        try_execute(self.func)


class ChoiceProperty(FuncProperty):
    def __init__(self, name, choices, value=None, setter=None, getter=None, **kwargs):
        self.choices = choices
        super().__init__(name=name, value=value, _type="choice", setter=setter, getter=getter, **kwargs)

    def validate(self):
        # choices must be greater than 1
        if len(self.choices) <= 1:
            self.is_valid = False
            print("{0} minimum 2 choices".format(self.name))
            return

        # all choices must be string
        for item in self.choices:
            if type(item) is not str:
                self.is_valid = False
                print("{0} all choices must be of type str".format(self.name))
                return

        if self.setter is None or self.getter is None:
            self.is_valid = False
            print("{0} setter or getter is null".format(self.name))
            return

        if type(self.get_value()) is not int:
            self.is_valid = False
            print("{0} value must be of type int".format(self.name))
            return

        # value must be int
        if self.val and type(self.val) is not int:
            self.is_valid = False
            print("{0} value must be of type int".format(self.name))
            return

        self.is_valid = True

    def get_choices(self):
        return self.choices

    def set_value(self, val: int, *args, **kwargs):
        if not self.is_valid:
            return

        if type(val) is not int:
            print(self.name + " [Utils.ChoiceProperty] set_value arg val must be of type int")
            return

        super().set_value(val, *args, **kwargs)


class Slider(FuncProperty):
    def __init__(self, name, value, min_value, max_value, setter, getter, **kwargs):
        FuncProperty.__init__(self, name=name, value=value, _type="slider", setter=setter, getter=getter, **kwargs)

        self._type = "slider"

        self.min_value = min_value
        self.max_value = max_value

        if self.is_valid:
            if self.val < self.min_value:
                self.val = self.min_value
            if self.val > self.max_value:
                self.val = self.max_value

    def validate(self):
        # value must be int
        if type(self.val) is not int:
            self.is_valid = False
            return

        # min max range should also be int
        if type(self.min_value) is not int or type(self.max_value) is not int:
            self.is_valid = False
            return

        if self.setter is None or self.getter is None:
            self.is_valid = False
            return

        super().validate()


class HorizontalLayoutGroup(Property):
    def __init__(self, properties=None, name="HorizontalLayoutGroup", *args, **kwargs):
        Property.__init__(self, name=name, value=None, _type="horizontal_layout_group", **kwargs)
        if properties is None:
            properties = []
        self.properties = properties

    def validate(self):
        if type(self.properties) != list:
            self.is_valid = False
            return

        for prop in self.properties:
            if isinstance(prop, Property):
                prop.validate()
                if not prop.is_valid:
                    self.is_valid = False
                    return
            else:
                print("HorizontalLayoutGroup: property {0} validation failed "
                      "property must be instance of edUtils.Property object".format(prop))
                self.properties.remove(prop)
                continue

        super().validate()


class FoldoutGroup(Property):
    def __init__(self, properties, name="Foldout", *args, **kwargs):
        Property.__init__(self, name=name, value=None, _type="foldout_group", *args, **kwargs)
        self.properties = properties

    def validate(self):
        for prop in self.properties:
            if isinstance(prop, Property):
                prop.validate()
                if not prop.is_valid:
                    self.is_valid = False
                    return
            else:
                print("FoldoutGroup: property {0} validation failed "
                      "property must be instance of edUtils.Property object".format(prop))
                self.properties.remove(prop)
                continue

        super().validate()


class InfoBox(Property):
    def __init__(self, text, info_type=0):
        Property.__init__(self, name="", value=text, _type="info_box")

        # info type 0=Message, 1=Warning, 2=Error
        # info type value not in range (0-2) is evaluated as 0
        self.info_type = 0 if info_type > 2 else info_type

    def validate(self):
        if type(self.val) != str:
            self.is_valid = False
            return

        super(InfoBox, self).validate()

    def get_text(self):
        return self.val


class Utils:
    @staticmethod
    def get_properties_for_lens(lens):
        if isinstance(lens, PerspectiveLens):
            near_far = FuncProperty(name="Near-Far",
                                    value=LVecBase2f(lens.get_near(), lens.get_far()),
                                    setter=lambda val: lens.setNearFar(val.x, val.y),
                                    getter=lambda: LVecBase2f(lens.get_near(), lens.get_far()))

            fov = FuncProperty(name="Field Of View",
                               value=lens.get_fov(),
                               value_limit=Vec2(0.01, 0.01),
                               setter=lens.set_fov,
                               getter=lens.get_fov)

            return [near_far, fov]

        elif isinstance(lens, OrthographicLens):
            near_far = FuncProperty(name="Near-Far",
                                    value=LVecBase2f(lens.get_near(), lens.get_far()),
                                    setter=lambda val: lens.setNearFar(val.x, val.y),
                                    getter=lambda: LVecBase2f(lens.get_near(), lens.get_far()))

            film_size = FuncProperty(name="FilmSize",
                                     value=lens.getFilmSize(),
                                     value_limit=Vec2(0.01, 0.01),
                                     setter=lens.setFilmSize,
                                     getter=lens.getFilmSize)

            return [near_far, film_size]
