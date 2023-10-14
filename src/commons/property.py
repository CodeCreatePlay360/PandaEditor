from panda3d.core import LVecBase2f, LVecBase3f, LPoint2f, LPoint3f, LColor, PerspectiveLens, OrthographicLens
from commons.logging import Logging as ed_logging
from thirdparty import type_enforced

Supported_Types = [int, float, str, bool, LVecBase2f, LPoint2f, LVecBase3f, LPoint3f, LColor, None]
Value_Limiter_Types = [int, float, LVecBase2f, LVecBase3f, type(None)]


class Property:
    @type_enforced.Enforcer
    def __init__(self,
                 name: str,
                 initial_value: Supported_Types,
                 value_limit: Value_Limiter_Types = None,
                 type_=None,
                 draw_idx: int = 1000,
                 length: int = -1,
                 align: int = 0,
                 *args, **kwargs):

        """
        Base class for editor property objects, should be used through any one of the derived classes.

        :param name: name of this property.
        :param initial_value: initial value.
        :param value_limit: an optional value limit for numerical value types. (see docs TODO ______________)
        :param type_: object type of this property should be any one of supported types. (see docs TODO ______________)
        :param draw_idx: draw index from list of properties, the default value is 1000 and properties will appear
        in inspector in order they are added, lower values are drawn on top.
        :param length: length of label of this property in inspector.
        :param args:
        :param kwargs:
        """

        self.name = name
        self.initial_value = initial_value
        self.type_ = type(self.initial_value) if type_ is None else type_
        self.value_limit = None if not value_limit else value_limit
        self.draw_idx = draw_idx
        self.length = length
        self.align = align
        self.kwargs = kwargs

        self.is_valid = False
        self.error_message = "Failed to varify property: "

    def get_value(self):
        return self.initial_value

    def get_clamped_value(self, val):
        if self.value_limit is None:
            return val

        if type(self.initial_value) is LVecBase2f:
            if val.x < self.value_limit.x:
                val.x = self.value_limit.x
            if val.y < self.value_limit.x:
                val.y = self.value_limit.x

        return val

    def set_value(self, val):
        pass

    def validate(self):
        self.is_valid = True


class ObjProperty(Property):
    @type_enforced.Enforcer
    def __init__(self, name, initial_value, obj, value_limit=None, type_=None, **kwargs):
        """
        Encapsulates, editor UI data for a public attribute
        :param name: name of the attribute.
        :param initial_value: initial value.
        :param obj: object reference in which the attribute is defined.
        :param value_limit: an optional value limit for numerical value types.
        :param type_: object type of this property, should be any one of supported types.
        :param kwargs:
        """

        super().__init__(name=name, initial_value=initial_value, value_limit=value_limit, type_=type_, **kwargs)
        self.obj = obj

    def validate(self):
        if not hasattr(self.obj, self.name):
            self.error_message += "{0} object {1} does not contain the attribute".format(self.name, self.obj)
            self.is_valid = False
            return

        if not isinstance(self.initial_value, type(getattr(self.obj, self.name))):
            self.error_message += "{0} initial value type and value type returned by" \
                                  " get_value method do not match".format(self.name)
            self.is_valid = False
            return

        super().validate()

    def set_value(self, val):
        val = self.get_clamped_value(val)
        setattr(self.obj, self.name, val)

    def get_value(self):
        return getattr(self.obj, self.name)


class FuncProperty(Property):
    @type_enforced.Enforcer
    def __init__(self, name, initial_value, setter, getter, value_limit=None, type_=None, **kwargs):
        """
        Encapsulates editor UI data for a property modifiable and accessible through set value and get value methods.
        :param name: name of property.
        :param initial_value: initial value.
        :param setter: method call when value is changed in inspector.
        :param getter: method call to get value for this property.
        :param value_limit: an optional value limit for numerical types.
        :param type_: object type of this property should be any one of supported types.
        :param kwargs:
        """

        super().__init__(name=name, initial_value=initial_value, type_=type_, value_limit=value_limit, **kwargs)
        self.setter = setter
        self.getter = getter

    def validate(self):
        if not callable(self.set_value) or not callable(self.get_value):
            self.is_valid = False
            self.error_message = "{0} get value and set value methods are not of callable type".format(self.name)
            return
        super().validate()

    def set_value(self, val, *args, **kwargs):
        try:
            val = self.get_clamped_value(val)
            self.setter(val, *args, **kwargs)
        except Exception as exception:
            ed_logging.log_exception(exception)

    def get_value(self, *args, **kwargs):
        val = None

        try:
            val = self.getter()
        except Exception as exception:
            ed_logging.log_exception(exception)

        return val


class EmptySpace(Property):
    @type_enforced.Enforcer
    def __init__(self, x: int = 0, y: int = 0, **kwargs):
        """
        Empty horizontal or vertical spacing.
        :param x: horizontal spacing.
        :param y: vertical spacing.
        :param kwargs:
        """

        super().__init__(name="", initial_value=None, type_="space", **kwargs)

        self.x = x  # horizontal spacing
        self.y = y  # vertical spacing

    def get_value(self):
        return self.x, self.y

    def validate(self):
        super().validate()


class Label(Property):
    @type_enforced.Enforcer
    def __init__(self, name, is_bold: bool = False, **kwargs):
        """
        Static text.
        :param name: name of this property.
        :param is_bold: draw bold ?
        :param kwargs:
        """

        super().__init__(name=name, initial_value=None, type_="label", **kwargs)
        self.is_bold = is_bold

    def validate(self):
        super().validate()


class ButtonProperty(Property):
    @type_enforced.Enforcer
    def __init__(self, name, method, **kwargs):
        """
        Generic button.
        :param name: Text to display inside the button.
        :param method: method call when button is pressed.
        :param kwargs:
        """

        self.method = method
        super().__init__(name=name, initial_value=None, type_="button", **kwargs)

    def validate(self):
        super().validate()

    def execute(self):
        try:
            self.method()
        except Exception as exception:
            ed_logging.log_exception(exception)


class ChoiceProperty(FuncProperty):
    @type_enforced.Enforcer
    def __init__(self, name, choices: list, initial_value: int, setter, getter, **kwargs):
        """
        Generic choice widget.
        :param name: name of this property.
        :param choices: list of choices, all list values must be of type string.
        :param initial_value: the initial choice as int.
        :param setter: method call when choice is changed through the widget.
        :param getter: method call to get current choice.
        :param kwargs:
        """

        self.choices = choices
        super().__init__(name=name, initial_value=initial_value, type_="choice", setter=setter, getter=getter, **kwargs)

    def get_choices(self):
        return self.choices

    def validate(self):
        # all choices must be string
        for item in self.choices:
            if not isinstance(item, str):
                self.error_message += "{0} input param choices list must only contain objects of type str".format(
                    self.name)
                self.is_valid = False
                return

        # initial value must be int
        if not isinstance(self.initial_value, int):
            print("initial value must be int")
            self.is_valid = False
            return

        super().validate()


class Slider(FuncProperty):
    @type_enforced.Enforcer
    def __init__(self, name, initial_value: int, min_value: int, max_value: int, setter, getter, **kwargs):
        """
        Generic slider widget.
        :param name: name of this property.
        :param initial_value: the initial value.
        :param min_value: minimum value.
        :param max_value: maximum value.
        :param setter: method call when value is changed through slider.
        :param getter: method call to get value.
        :param kwargs:
        """

        super().__init__(name=name, initial_value=initial_value, type_="slider", setter=setter, getter=getter, **kwargs)

        self._type = "slider"

        self.min_value = min_value
        self.max_value = max_value
        self.initial_value = min(self.min_value, self.max_value)

    def validate(self):
        super().validate()


class ContainerProperty(Property):
    def __init__(self, name, type_, properties: list = None, **kwargs):
        """Base class for a property that contains child properties"""

        super().__init__(name=name, initial_value=None, type_=type_, **kwargs)
        if properties is None:
            properties = []
        self.properties = properties


class HorizontalLayoutGroup(ContainerProperty):
    @type_enforced.Enforcer
    def __init__(self, name="HorizontalLayoutGroup", properties: list = None, **kwargs):
        super().__init__(name=name, type_="horizontal_layout_group", properties=properties, **kwargs)

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


class FoldoutGroup(ContainerProperty):
    @type_enforced.Enforcer
    def __init__(self, name="Foldout", properties: list = None, **kwargs):
        super().__init__(name=name, type_="foldout_group", properties=properties, **kwargs)

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


class StaticBox(ContainerProperty):
    @type_enforced.Enforcer
    def __init__(self, name="LogicalGroup", properties: list = None, **kwargs):
        super().__init__(name=name, type_="static_box", properties=properties, **kwargs)

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
    def get_properties_for_lens(lens):
        if isinstance(lens, PerspectiveLens):
            near_far = FuncProperty(name="Near-Far",
                                    initial_value=LVecBase2f(lens.get_near(), lens.get_far()),
                                    value_limit=LVecBase2f(0.01, 1),
                                    setter=lambda val: lens.setNearFar(val.x, val.y),
                                    getter=lambda: LVecBase2f(lens.get_near(), lens.get_far()))

            fov = FuncProperty(name="Field Of View",
                               initial_value=lens.get_fov().x,
                               value_limit=3,
                               setter=lambda x: lens.set_fov(x),
                               getter=lambda: lens.get_fov().x)

            return [near_far, fov]

        elif isinstance(lens, OrthographicLens):
            near_far = FuncProperty(name="Near-Far",
                                    initial_value=LVecBase2f(lens.get_near(), lens.get_far()),
                                    setter=lambda val: lens.setNearFar(val.x, val.y),
                                    getter=lambda: LVecBase2f(lens.get_near(), lens.get_far()))

            film_size = FuncProperty(name="FilmSize",
                                     initial_value=lens.getFilmSize(),
                                     value_limit=LVecBase2f(0.01, 0.01),
                                     setter=lens.setFilmSize,
                                     getter=lens.getFilmSize)

            return [near_far, film_size]
