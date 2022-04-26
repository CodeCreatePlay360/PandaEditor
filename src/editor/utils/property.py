from panda3d.core import Vec3, Vec2
from editor.utils.exceptionHandler import try_execute, try_execute_1


class Property:
    def __init__(self, name, value, value_limit=None, _type=None):
        self.name = name
        self.val = value
        self._type = _type

        self.is_valid = False
        self.value_limit = value_limit
        self.acceptable_value_limit_types = [int, float, Vec2, Vec3]

        if _type is None:
            self._type = type(value)
        else:
            self._type = _type

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
    def __init__(self, name, value, obj, _type=None, value_limit=None):
        super().__init__(name=name, value=value, _type=_type, value_limit=value_limit)

        self.obj = obj

    def validate(self):
        if hasattr(self.obj, self.name):
            self.is_valid = True
            return

        super().validate()

    def set_value(self, val):
        setattr(self.obj, self.name, val)

    def get_value(self):
        return getattr(self.obj, self.name)


class FuncProperty(Property):
    def __init__(self, name, value, value_limit=None, _type=None, setter=None, getter=None):
        super().__init__(name=name, value=value, _type=_type, value_limit=value_limit)

        self.setter = setter
        self.getter = getter

    def validate(self):
        if self.setter is None or self.getter is None:
            self.is_valid = False

        super().validate()

    def get_value(self, *args, **kwargs):
        getter = self.getter
        return try_execute_1(getter)

    def set_value(self, val, *args, **kwargs):
        try_execute(self.setter, val, *args, **kwargs)


class EmptySpace(Property):
    def __init__(self, x, y):
        super().__init__(name="", value=None, _type="space")

        self.x = x  # horizontal spacing
        self.y = y  # vertical spacing

    def validate(self):
        if type(self.x) is not int or type(self.y) is not int:
            self.is_valid = False
            return

        super().validate()


class Label(Property):
    def __init__(self, name, is_bold=False, text_color=None):
        super().__init__(name=name, value=None, _type="label")

        self.is_bold = is_bold
        self.text_color = text_color

    def validate(self):
        if type(self.is_bold) is not bool:
            self.is_valid = False
            return
        super().validate()


class ButtonProperty(Property):
    def __init__(self, name, func):
        self.func = func

        super().__init__(name=name, value=None, _type="button")

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
    def __init__(self, name, choices, value=0, setter=None, getter=None):
        self.choices = choices

        super().__init__(name=name, value=value, _type="choice", setter=setter, getter=getter)

    def validate(self):
        # choices must be greater than 1
        if len(self.choices) <= 1:
            self.is_valid = False
            return

        # all choices must be string
        for item in self.choices:
            if type(item) is not str:
                self.is_valid = False
                return

        # value must be int
        if type(self.val) is not int:
            self.is_valid = False
            return

        if self.setter is None or self.getter is None:
            self.is_valid = False
            return

        self.is_valid = True

    def get_choices(self):
        return self.choices

    def set_value(self, val: int, *args, **kwargs):
        if type(val) is not int:
            print("error in edUI.ChoiceProperty.set_value arg val must be of type int")
            return

        super().set_value(val, *args, **kwargs)


class Slider(FuncProperty):
    def __init__(self, name, value, min_value, max_value, setter, getter):
        FuncProperty.__init__(self, name=name, value=value, _type="slider", setter=setter, getter=getter)

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


class StaticBox(Property):
    def __init__(self, name, controls=None):
        Property.__init__(self, name, value=None, _type="static_box")

        self.controls = controls
