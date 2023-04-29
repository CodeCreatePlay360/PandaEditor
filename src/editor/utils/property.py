from panda3d.core import LVecBase2f, LVecBase3f, LPoint2f, LPoint3f, LColor, PerspectiveLens, OrthographicLens
from thirdparty import type_enforced
from editor.utils.exceptionHandler import safe_execute

Supported_Types = [int, float, str, bool, LVecBase2f, LPoint2f, LVecBase3f, LPoint3f, LColor, None]
Value_Limiter_Types = [int, float, LVecBase2f, LVecBase3f, type(None)]


class Property:
    Invalid_Initial_Value = -1010
    Invalid_Value_Limiter = -1010

    @type_enforced.Enforcer
    def __init__(self,
                 name: str,
                 value: Supported_Types,
                 value_limit: Value_Limiter_Types = None,
                 type_=None,
                 *args, **kwargs):
        self.name = name
        self.initial_value = value
        self.type_ = type(self.initial_value) if type_ is None else type_
        self.value_limit = None if not value_limit else value_limit
        self.kwargs = kwargs

        self.is_valid = False
        self.error_message = "Failed to varify property: "

    def get_value(self):
        return self.initial_value

    def set_value(self, val):
        pass

    def validate(self):
        self.is_valid = True


class ObjProperty(Property):
    @type_enforced.Enforcer
    def __init__(self, name, value, obj, value_limit=None, type_=None, **kwargs):
        super().__init__(name=name, value=value, value_limit=value_limit, type_=type_, **kwargs)
        self.obj = obj

    def validate(self):
        if not hasattr(self.obj, self.name):
            self.error_message += "{0} object {1} does not contain the attribute".format(self.name, self.obj)
            self.is_valid = False
            return

        if not isinstance(self.initial_value, type(getattr(self.obj, self.name))):
            self.error_message += "{0} initial value and actual value types do not match".format(self.name)
            self.is_valid = False
            return

        super().validate()

    def set_value(self, val):
        setattr(self.obj, self.name, val)

    def get_value(self):
        return getattr(self.obj, self.name)


class FuncProperty(Property):
    @type_enforced.Enforcer
    def __init__(self, name, value, setter, getter, value_limit=None, type_=None, **kwargs):
        super().__init__(name=name, value=value, type_=type_, value_limit=value_limit, **kwargs)
        self.setter = setter
        self.getter = getter

    def validate(self):
        if not callable(self.setter) or not callable(self.getter):
            self.is_valid = False
            self.error_message = "{0} setter and getter must be callable objects".format(self.name)
            return
        super().validate()

    def set_value(self, val, *args, **kwargs):
        safe_execute(self.setter, val, *args, **kwargs)

    def get_value(self, *args, **kwargs):
        getter = self.getter
        return safe_execute(getter, return_func_val=True)


class EmptySpace(Property):
    @type_enforced.Enforcer
    def __init__(self, x: int, y: int, **kwargs):
        super().__init__(name="", value=None, type_="space", **kwargs)

        self.x = x  # horizontal spacing
        self.y = y  # vertical spacing

    def get_value(self):
        return self.x, self.y

    def validate(self):
        super().validate()


class Label(Property):
    @type_enforced.Enforcer
    def __init__(self, name, is_bold: bool = False, **kwargs):
        super().__init__(name=name, value=None, type_="label", **kwargs)
        self.is_bold = is_bold

    def validate(self):
        super().validate()


class ButtonProperty(Property):
    @type_enforced.Enforcer
    def __init__(self, name, func, **kwargs):
        self.func = func
        super().__init__(name=name, value=None, type_="button", **kwargs)

    def validate(self):
        super().validate()

    def execute(self):
        safe_execute(self.func)


class ChoiceProperty(FuncProperty):
    @type_enforced.Enforcer
    def __init__(self, name, choices: list, value: int, setter, getter, **kwargs):
        self.choices = choices
        super().__init__(name=name, value=value, type_="choice", setter=setter, getter=getter, **kwargs)

    def get_choices(self):
        return self.choices

    def validate(self):
        # all choices must be string
        for item in self.choices:
            if not (isinstance(item, str)):
                self.error_message += "{0} input param choices list must only contain objects of type str".format(
                    self.name)
                self.is_valid = False
                return

        super().validate()


class Slider(FuncProperty):
    @type_enforced.Enforcer
    def __init__(self, name, value: int, min_value: int, max_value: int, setter, getter, **kwargs):
        super().__init__(name=name, value=value, type_="slider", setter=setter, getter=getter, **kwargs)

        self._type = "slider"

        self.min_value = min_value
        self.max_value = max_value
        self.initial_value = min(self.min_value, self.max_value)

    def validate(self):
        super().validate()

# ------------------------------------------------------------------------------------------------
# TODO: HorizontalLayoutGroup, FoldoutGroup, StaticBox should have one base class since code is same for
#  all 3 of them

# TODO rename HorizontalLayoutGroup to HorizontalGroup and rename FoldoutGroup to VerticalGroup & make
#  sure to reflect changes in Property_And_Type in wxCustomProperties


class HorizontalLayoutGroup(Property):
    @type_enforced.Enforcer
    def __init__(self, name="HorizontalLayoutGroup", properties: list = None, **kwargs):
        super().__init__(name=name, value=None, type_="horizontal_layout_group", **kwargs)
        if properties is None:
            properties = []
        self.properties = properties

    def validate(self):
        props = []
        for prop in self.properties:
            if isinstance(prop, Property):
                props.append(prop)

        self.properties.clear()
        for prop in props:
            prop.validate()
            if prop.is_valid:
                self.properties.append(prop)

        super().validate()


class FoldoutGroup(Property):
    @type_enforced.Enforcer
    def __init__(self, name="Foldout", properties: list = None, *args, **kwargs):
        super().__init__(name=name, value=None, type_="foldout_group", *args, **kwargs)
        if properties is None:
            properties = []
        self.properties = properties

    def validate(self):
        props = []
        for prop in self.properties:
            if isinstance(prop, Property):
                props.append(prop)

        self.properties.clear()
        for prop in props:
            prop.validate()
            if prop.is_valid:
                self.properties.append(prop)

        super().validate()


class StaticBox(Property):
    @type_enforced.Enforcer
    def __init__(self, name="LogicalGroup", properties: list = None, *args, **kwargs):
        super().__init__(name=name, value=None, type_="static_box", *args, **kwargs)
        if properties is None:
            properties = []
        self.properties = properties

    def validate(self):
        props = []
        for prop in self.properties:
            if isinstance(prop, Property):
                props.append(prop)

        self.properties.clear()
        for prop in props:
            prop.validate()
            if prop.is_valid:
                self.properties.append(prop)

        super().validate()


class Utils:
    @staticmethod
    def get_lens_properties(lens):
        if isinstance(lens, PerspectiveLens):
            near_far = FuncProperty(name="Near-Far",
                                    value=LVecBase2f(lens.get_near(), lens.get_far()),
                                    setter=lambda val: lens.setNearFar(val.x, val.y),
                                    getter=lambda: LVecBase2f(lens.get_near(), lens.get_far()))

            fov = FuncProperty(name="Field Of View",
                               value=lens.get_fov().x,
                               value_limit=3,
                               setter=lambda x: lens.set_fov(x),
                               getter=lambda: lens.get_fov().x)

            return [near_far, fov]

        elif isinstance(lens, OrthographicLens):
            near_far = FuncProperty(name="Near-Far",
                                    value=LVecBase2f(lens.get_near(), lens.get_far()),
                                    setter=lambda val: lens.setNearFar(val.x, val.y),
                                    getter=lambda: LVecBase2f(lens.get_near(), lens.get_far()))

            film_size = FuncProperty(name="FilmSize",
                                     value=lens.getFilmSize(),
                                     value_limit=LVecBase2f(0.01, 0.01),
                                     setter=lens.setFilmSize,
                                     getter=lens.getFilmSize)

            return [near_far, film_size]
