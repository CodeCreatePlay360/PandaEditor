import pathlib
import sys
import wx
import wx.lib.colourchooser.pycolourchooser as colorSelector
import editor.edPreferences as edPreferences

from panda3d.core import LVecBase2f, LPoint2f, LVecBase3f, LPoint3f, LColor
from editor.constants import ICONS_PATH
from editor.globals import editor
from editor.utils import common_maths

# IDs
ID_TEXT_CHANGE = wx.NewId()

# constants
Control_Margin_Right = 1
Control_Margin_Left = 3
Label_To_Control_Space = 10
Label_Top_Offset = 3

SYSTEM_KEY_CODES = [8, 32, 45, 43, 46]


def get_rounded_value(value: float, round_off=3):
    value = round(value, round_off)
    return value


def is_valid_int(curr_value):
    try:
        int(curr_value)
        value_valid = True
    except ValueError:
        value_valid = False

    return value_valid


def is_valid_float(curr_value):
    try:
        float(curr_value)
        value_valid = True
    except ValueError:
        value_valid = False

    return value_valid


class WxCustomProperty(wx.Window):
    def __init__(self, parent, prop=None, h_offset=1, *args, **kwargs):
        wx.Window.__init__(self, parent, *args)
        self.SetBackgroundColour(edPreferences.Colors.Panel_Normal)
        self.__parent = parent

        self.__ed_property = prop
        self.__h_offset = h_offset
        self.__font_colour = edPreferences.Colors.Inspector_properties_label
        self.__font_size = 10

        # create fonts
        self.__ed_property_font = wx.Font(self.font_size, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.__control_label_font = wx.Font(self.font_size, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # ------------------------------------------------------------------------------

        self.__ed_property_label = wx.StaticText(self, label=self.ed_property.name.capitalize())
        self.__ed_property_label.SetFont(self.ed_property_font)
        self.__ed_property_label.SetForegroundColour(self.font_colour)

        self.SetSize((-1, 22))
        self.SetMinSize((-1, 22))
        self.SetMaxSize((-1, 22))

        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__sizer.AddSpacer(Control_Margin_Left)
        self.SetSizer(self.__sizer)

        self.Layout()

    def on_kill_focus(self, evt):
        evt.Skip()

    def bind_events(self):
        pass

    def unbind_events(self):
        pass

    def create_control(self):
        size = self.ed_property_label.GetSize()
        self.ed_property_label.SetMinSize((size.x + Label_To_Control_Space, size.y))

    def get_value(self):
        return self.ed_property.get_value()

    def get_type(self):
        return self.ed_property.get_type()

    def set_control_value(self, val):
        pass

    def set_value(self, val):
        # self.value = val
        property_value = self.ed_property.set_value(val)
        editor.observer.trigger("PropertyModified", self)
        return property_value

    def has_focus(self):
        return False

    @property
    def parent(self):
        return self.__parent

    @property
    def ed_property(self):
        return self.__ed_property

    @property
    def h_offset(self):
        return self.__h_offset

    @property
    def font_colour(self):
        return self.__font_colour

    @property
    def font_size(self):
        return self.__font_size

    @property
    def ed_property_font(self):
        return self.__ed_property_font

    @property
    def control_label_font(self):
        return self.__control_label_font

    @property
    def ed_property_label(self):
        return self.__ed_property_label

    @property
    def sizer(self):
        return self.__sizer


class EmptySpace(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.SetSize((-1, self.get_y()))
        self.SetMinSize((-1, self.get_y()))

    def create_control(self):
        pass

    def get_x(self):
        return self.ed_property.x

    def get_y(self):
        return self.ed_property.y


class LabelProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.font = None
        self.ctrl_label = None

    def create_control(self):
        self.ed_property_label.Destroy()

        if self.ed_property.is_bold:
            self.font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.BOLD)
        else:
            self.font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)

        self.ctrl_label = wx.StaticText(self, label=self.ed_property.name)
        self.ctrl_label.SetFont(self.font)
        self.ctrl_label.SetForegroundColour(edPreferences.Colors.Bold_Label)

        self.sizer.Add(self.ctrl_label, 0, wx.TOP, border=Label_Top_Offset)


class IntProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)

        self.__text_ctrl = None
        self.__current_value = None
        self.__old_value = None  # last value of text control before updating

    def on_event_text(self, evt):
        if is_valid_int(self.__text_ctrl.GetValue()):
            self.__current_value = int(self.__text_ctrl.GetValue())
            self.__old_value = int(self.__current_value)
        else:
            self.__current_value = self.__old_value

        evt.Skip()

    def on_kill_focus(self, evt):
        self.set_value(self.__current_value)
        evt.Skip()

    def create_control(self):
        super().create_control()
        self.__text_ctrl = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_SUNKEN, id=ID_TEXT_CHANGE)

        # set initial value
        self.__current_value = self.get_value()
        self.__old_value = self.__current_value
        self.__text_ctrl.SetValue(str(self.__current_value))

        # add to sizer
        self.sizer.Add(self.ed_property_label, 0, wx.EXPAND | wx.TOP, border=3)
        self.sizer.Add(self.__text_ctrl, 1, wx.TOP, border=1)
        self.sizer.AddSpacer(Control_Margin_Right)

        self.bind_events()
        self.Refresh()

    def bind_events(self):
        self.__text_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)
        self.__text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)

    def unbind_events(self):
        self.__text_ctrl.Unbind(wx.EVT_KILL_FOCUS)
        self.__text_ctrl.Unbind(wx.EVT_TEXT)

    def set_control_value(self, val):
        val = get_rounded_value(val)
        self.__text_ctrl.SetValue(str(val))

    def has_focus(self):
        if self.__text_ctrl.HasFocus():
            return True
        return False


class FloatProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.__text_ctrl = None
        self.__current_value = None
        self.__old_value = None  # last value of text control before updating

    def on_event_text(self, evt):
        if is_valid_float(self.__text_ctrl.GetValue()):
            value = float(self.__text_ctrl.GetValue())
            if self.ed_property.value_limit is not None:
                if value < self.ed_property.value_limit:
                    value = self.ed_property.value_limit

            # self.set_value(value)
            self.__current_value = value
            self.__old_value = self.__current_value
        else:
            self.__text_ctrl.SetValue(str(self.__old_value))

        evt.Skip()

    def on_kill_focus(self, evt):
        self.set_value(self.__current_value)
        evt.Skip()

    def create_control(self):
        super().create_control()
        self.__text_ctrl = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_SUNKEN, id=ID_TEXT_CHANGE)

        # set initial value
        property_value = self.get_value()
        self.__text_ctrl.SetValue(str(property_value))

        # add to sizer
        self.sizer.Add(self.ed_property_label, 0, wx.EXPAND | wx.TOP, border=3)
        self.sizer.Add(self.__text_ctrl, 1, wx.TOP, border=1)
        self.sizer.AddSpacer(Control_Margin_Right)

        self.bind_events()
        self.Refresh()

    def bind_events(self):
        self.__text_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)
        self.__text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)

    def unbind_events(self):
        self.__text_ctrl.Unbind(wx.EVT_KILL_FOCUS)
        self.__text_ctrl.Unbind(wx.EVT_TEXT)

    def set_control_value(self, val):
        val = get_rounded_value(val)
        self.__text_ctrl.SetValue(str(val))

    def has_focus(self):
        if self.__text_ctrl.HasFocus():
            return True
        return False


class StringProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.__text_ctrl = None
        self.__current_value = None

    def on_event_text(self, evt):
        self.__current_value = self.__text_ctrl.GetValue()
        evt.Skip()

    def on_kill_focus(self, evt):
        self.set_value(self.__current_value)
        evt.Skip()

    def create_control(self):
        super().create_control()

        self.__text_ctrl = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_SUNKEN, id=ID_TEXT_CHANGE)
        self.__text_ctrl.SetValue(self.get_value())

        # add to sizer
        self.sizer.Add(self.ed_property_label, 0, wx.EXPAND | wx.TOP, border=3)
        self.sizer.Add(self.__text_ctrl, 1, wx.TOP, border=1)
        self.sizer.AddSpacer(Control_Margin_Right)

        self.bind_events()
        self.Refresh()

    def bind_events(self):
        self.__text_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)
        self.__text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)

    def unbind_events(self):
        self.__text_ctrl.Unbind(wx.EVT_KILL_FOCUS)
        self.__text_ctrl.Unbind(wx.EVT_TEXT)

    def set_control_value(self, val):
        self.__text_ctrl.SetValue(str(val))

    def has_focus(self):
        if self.__text_ctrl.HasFocus():
            return True
        return False


class BoolProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.__toggle = None

    def on_event_toggle(self, evt):
        self.set_value(self.__toggle.GetValue())
        evt.Skip()

    def create_control(self):
        # label = wx.StaticText(self, label=self.label)
        super().create_control()
        self.__toggle = wx.CheckBox(self, label="", style=0)

        # initial value
        self.__toggle.SetValue(self.get_value())

        # add to sizer
        if self.ed_property.name == "":
            self.ed_property_label.Destroy()
        else:
            self.sizer.Add(self.ed_property_label, 0, wx.EXPAND | wx.TOP, border=3)

        self.sizer.Add(self.__toggle, 0, wx.TOP, border=0 if sys.platform == "linux" else 3)
        self.sizer.AddSpacer(Control_Margin_Right)

        self.__toggle.Bind(wx.EVT_CHECKBOX, self.on_event_toggle)
        self.Refresh()

    def set_control_value(self, val):
        self.__toggle.SetValue(val)


class ColorProperty(WxCustomProperty):
    class CustomColorSelector(colorSelector.PyColourChooser):
        def __init__(self, color_property, initial_val, *args, **kwargs):
            colorSelector.PyColourChooser.__init__(self, *args, **kwargs)

            self.__color_property = color_property
            self.SetValue(initial_val)

        def onSliderMotion(self, evt):
            super(ColorProperty.CustomColorSelector, self).onSliderMotion(evt)
            self.update()
            evt.Skip()

        def onScroll(self, evt):
            super(ColorProperty.CustomColorSelector, self).onScroll(evt)
            self.update()
            evt.Skip()

        def onPaletteMotion(self, evt):
            super(ColorProperty.CustomColorSelector, self).onPaletteMotion(evt)
            self.update()
            evt.Skip()

        def onBasicClick(self, evt, box):
            super(ColorProperty.CustomColorSelector, self).onBasicClick(evt, box)
            self.update()
            evt.Skip()

        def onCustomClick(self, evt, box):
            super(ColorProperty.CustomColorSelector, self).onBasicClick(evt, box)
            self.update()
            evt.Skip()

        def update(self):
            self.__color_property.set_value(ColorProperty.get_panda3d_color_object(self.GetValue()))
            self.__color_property.Refresh()

    class CustomColorDialog(wx.Dialog):
        def __init__(self, parent, initial_val, title, color_property):
            style = wx.DEFAULT_DIALOG_STYLE | wx.DIALOG_NO_PARENT | wx.STAY_ON_TOP
            super(ColorProperty.CustomColorDialog, self).__init__(parent, title=title, style=style)

            self.SetBackgroundColour(wx.Colour(edPreferences.Colors.Panel_Normal))
            self.SetSize((490, 350))

            self.__panel = wx.Panel(self)  # create a background panel
            self.color_selector = ColorProperty.CustomColorSelector(color_property, initial_val, self.__panel, -1)

            # create a sizer for panel and add color selector to it
            self.__panel_sizer = wx.BoxSizer(wx.VERTICAL)
            self.__panel_sizer.Add(self.color_selector, 1, wx.EXPAND)
            self.__panel.SetSizer(self.__panel_sizer)

            # create a main sizer and add panel to it
            self.__sizer = wx.BoxSizer(wx.VERTICAL)
            self.__sizer.Add(self.__panel, 1, wx.EXPAND)
            self.SetSizer(self.__sizer)

    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.__color_panel = None

    def create_control(self):
        super().create_control()
        self.__color_panel = wx.Panel(self)
        self.__color_panel.SetMaxSize((self.GetSize().x - self.ed_property_label.GetSize().x - 8, 18))
        self.__color_panel.SetWindowStyleFlag(wx.BORDER_SIMPLE)
        self.__color_panel.SetBackgroundColour(ColorProperty.get_wx_color_object(self.get_value()))

        # add to sizer
        self.sizer.Add(self.ed_property_label, 0, wx.EXPAND | wx.TOP, border=3)
        self.sizer.Add(self.__color_panel, 1, wx.EXPAND)
        self.sizer.AddSpacer(Control_Margin_Right)

        self.bind_events()

    def set_control_value(self, val):
        self.__color_panel.SetBackgroundColour(ColorProperty.get_wx_color_object(val))
        self.Refresh()

    def on_evt_clicked(self, evt):
        value = ColorProperty.get_wx_color_object(self.get_value())
        x = ColorProperty.CustomColorDialog(None, value, "ColorSelectDialog", self)
        x.Show()
        evt.Skip()

    def on_evt_size(self, evt):
        self.__color_panel.SetMaxSize((self.GetSize().x - self.ed_property_label.GetSize().x - 8, 18))
        evt.Skip()

    def bind_events(self):
        self.__color_panel.Bind(wx.EVT_LEFT_DOWN, self.on_evt_clicked)
        self.Bind(wx.EVT_SIZE, self.on_evt_size)

    def unbind_events(self):
        self.__color_panel.Unbind(wx.EVT_LEFT_DOWN)
        self.Unbind(wx.EVT_SIZE)

    @staticmethod
    def get_wx_color_object(value):
        """converts to wx colour value range from 0-1 range and return a wx color object"""

        value = LColor(value.x, value.y, value.z, value.w)
        value.x = common_maths.map_to_range(0, 1, 0, 255, value.x)
        value.y = common_maths.map_to_range(0, 1, 0, 255, value.y)
        value.z = common_maths.map_to_range(0, 1, 0, 255, value.z)
        value.w = common_maths.map_to_range(0, 1, 0, 255, value.w)
        return wx.Colour(int(value.x), int(value.y), int(value.z), int(value.w))

    @staticmethod
    def get_panda3d_color_object(value):
        """converts to panda3d color value range from 0-255 range and return a panda3d.core.LColor object"""

        value = wx.Colour(value.red, value.green, value.blue, value.alpha)
        value.x = common_maths.map_to_range(0, 255, 0, 1, value.red)
        value.y = common_maths.map_to_range(0, 255, 0, 1, value.green)
        value.z = common_maths.map_to_range(0, 255, 0, 1, value.blue)
        value.w = common_maths.map_to_range(0, 255, 0, 1, value.alpha)
        return LColor(value.x, value.y, value.z, value.w)


class ColourTemperatureProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)


class Vector2Property(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)

        self.__text_ctrl_x = None
        self.__text_ctrl_y = None

        self.__current_value = None
        self.__old_value = None  # last value of text control before updating

    def on_event_text(self, evt):
        # validate h
        if is_valid_float(self.__text_ctrl_x.GetValue()):
            is_valid_h = True
        else:
            is_valid_h = False

        # validate p
        if is_valid_float(self.__text_ctrl_y.GetValue()):
            is_valid_p = True
        else:
            is_valid_p = False

        if is_valid_h and is_valid_p:
            h = float(self.__text_ctrl_x.GetValue())
            p = float(self.__text_ctrl_y.GetValue())

            # apply value limit
            if self.ed_property.value_limit is not None:
                if h < self.ed_property.value_limit.x:
                    h = self.ed_property.value_limit.x

                if p < self.ed_property.value_limit.x:
                    p = self.ed_property.value_limit.x

            # self.set_value(LVecBase2f(h, p))
            self.__current_value = LVecBase2f(h, p)
            self.__old_value = LVecBase2f(h, p)

        else:
            self.__current_value = self.__old_value
            # self.__text_ctrl_x.SetValue(str(self.__old_value.x))
            # self.__text_ctrl_y.SetValue(str(self.__old_value.y))\

        evt.Skip()

    def on_kill_focus(self, evt):
        self.set_value(self.__current_value)
        evt.Skip()

    def create_control(self):
        super(Vector2Property, self).create_control()

        label_x = wx.StaticText(self, label=" x ")
        label_x.SetFont(self.control_label_font)
        label_x.SetForegroundColour(self.font_colour)
        self.__text_ctrl_x = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        label_y = wx.StaticText(self, label=" y ")
        label_y.SetFont(self.control_label_font)
        label_y.SetForegroundColour(self.font_colour)
        self.__text_ctrl_y = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        # set initial value
        property_value = self.get_value()

        self.__text_ctrl_x.SetValue(str(property_value.x))
        self.__text_ctrl_y.SetValue(str(property_value.y))

        # add to sizer
        self.sizer.Add(self.ed_property_label, 0, wx.EXPAND | wx.TOP, border=3)

        self.sizer.Add(label_x, 0, wx.TOP, 3)
        self.sizer.Add(self.__text_ctrl_x, 1, wx.TOP, border=1)
        self.sizer.Add(label_y, 0, wx.TOP, 3)
        self.sizer.Add(self.__text_ctrl_y, 1, wx.TOP, border=1)

        self.sizer.AddSpacer(Control_Margin_Right)

        self.bind_events()
        self.Refresh()

    def bind_events(self):
        self.__text_ctrl_x.Bind(wx.EVT_TEXT, self.on_event_text)
        self.__text_ctrl_y.Bind(wx.EVT_TEXT, self.on_event_text)

        self.__text_ctrl_x.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)
        self.__text_ctrl_y.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

    def unbind_events(self):
        self.__text_ctrl_x.Unbind(wx.EVT_TEXT)
        self.__text_ctrl_y.Unbind(wx.EVT_TEXT)

        self.__text_ctrl_x.Unbind(wx.EVT_KILL_FOCUS)
        self.__text_ctrl_y.Unbind(wx.EVT_KILL_FOCUS)

    def set_control_value(self, val):
        # apply value limit
        if self.ed_property.value_limit is not None:
            if val.x < self.ed_property.value_limit.x:
                val.x = self.ed_property.value_limit.x

            if val.y < self.ed_property.value_limit.y:
                val.y = self.ed_property.value_limit.y

        x = get_rounded_value(val.x)
        y = get_rounded_value(val.y)

        self.__text_ctrl_x.SetValue(str(x))
        self.__text_ctrl_y.SetValue(str(y))

    def has_focus(self):
        if self.__text_ctrl_x.HasFocus() or self.__text_ctrl_y.HasFocus():
            return True
        return False


class Vector3Property(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)

        self.__text_ctrl_x = None
        self.__text_ctrl_y = None
        self.__text_ctrl_z = None

        self.__old_value = None
        self.__current_value = None

    def on_event_text(self, evt):
        # validate h
        if is_valid_float(self.__text_ctrl_x.GetValue()):
            is_valid_h = True
        else:
            is_valid_h = False

        # validate p
        if is_valid_float(self.__text_ctrl_y.GetValue()):
            is_valid_p = True
        else:
            is_valid_p = False

        # validate r
        if is_valid_float(self.__text_ctrl_z.GetValue()):
            is_valid_r = True
        else:
            is_valid_r = False

        if is_valid_h and is_valid_p and is_valid_r:
            h = float(self.__text_ctrl_x.GetValue())
            p = float(self.__text_ctrl_y.GetValue())
            r = float(self.__text_ctrl_z.GetValue())

            # apply value limit
            if self.ed_property.value_limit is not None:
                if h < self.ed_property.value_limit.x:
                    h = self.ed_property.value_limit.x

                if p < self.ed_property.value_limit.y:
                    p = self.ed_property.value_limit.y

                if r < self.ed_property.value_limit.z:
                    r = self.ed_property.value_limit.z

            # self.set_value(LVecBase3f(h, p, r))
            self.__current_value = LVecBase3f(h, p, r)
            self.__old_value = LVecBase3f(h, p, r)

        else:
            self.__current_value = self.__old_value

            # self.__text_ctrl_x.SetValue(str(self.__old_value.x))
            # self.__text_ctrl_y.SetValue(str(self.__old_value.y))
            # self.__text_ctrl_z.SetValue(str(self.__old_value.z))

        evt.Skip()

    def on_kill_focus(self, evt):
        self.set_value(self.__current_value)
        evt.Skip()

    def create_control(self):
        # label = wx.StaticText(self, label=self.label)
        super(Vector3Property, self).create_control()

        label_x = wx.StaticText(self, label="x ")
        label_x.SetFont(self.control_label_font)
        label_x.SetForegroundColour(self.font_colour)
        self.__text_ctrl_x = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        label_y = wx.StaticText(self, label=" y ")
        label_y.SetFont(self.control_label_font)
        label_y.SetForegroundColour(self.font_colour)
        self.__text_ctrl_y = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        label_z = wx.StaticText(self, label=" z ")
        label_z.SetFont(self.control_label_font)
        label_z.SetForegroundColour(self.font_colour)
        self.__text_ctrl_z = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        # set initial value
        property_value = self.get_value()
        self.__old_value = property_value

        x = get_rounded_value(property_value.x)
        y = get_rounded_value(property_value.y)
        z = get_rounded_value(property_value.z)

        self.__text_ctrl_x.SetValue(str(x))
        self.__text_ctrl_y.SetValue(str(y))
        self.__text_ctrl_z.SetValue(str(z))

        # add to sizer
        self.sizer.Add(self.ed_property_label, 0, wx.EXPAND | wx.TOP, border=3)

        self.sizer.Add(label_x, 0, wx.TOP, 3)
        self.sizer.Add(self.__text_ctrl_x, 1, wx.TOP, border=1)

        self.sizer.Add(label_y, 0, wx.TOP, 3)
        self.sizer.Add(self.__text_ctrl_y, 1, wx.TOP, border=1)

        self.sizer.Add(label_z, 0, wx.TOP, 3)
        self.sizer.Add(self.__text_ctrl_z, 1, wx.TOP, border=1)

        self.sizer.AddSpacer(Control_Margin_Right)

        self.bind_events()
        self.Refresh()

    def bind_events(self):
        self.__text_ctrl_x.Bind(wx.EVT_TEXT, self.on_event_text)
        self.__text_ctrl_y.Bind(wx.EVT_TEXT, self.on_event_text)
        self.__text_ctrl_z.Bind(wx.EVT_TEXT, self.on_event_text)

        self.__text_ctrl_x.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)
        self.__text_ctrl_y.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)
        self.__text_ctrl_z.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

    def unbind_events(self):
        self.__text_ctrl_x.Unbind(wx.EVT_TEXT)
        self.__text_ctrl_y.Unbind(wx.EVT_TEXT)
        self.__text_ctrl_z.Unbind(wx.EVT_TEXT)

        self.__text_ctrl_x.Unbind(wx.EVT_KILL_FOCUS)
        self.__text_ctrl_y.Unbind(wx.EVT_KILL_FOCUS)
        self.__text_ctrl_z.Unbind(wx.EVT_KILL_FOCUS)

    def set_control_value(self, val):
        x = get_rounded_value(val.x)
        y = get_rounded_value(val.y)
        z = get_rounded_value(val.z)

        if self.ed_property.value_limit is not None:
            if val.x < self.ed_property.value_limit.x:
                val.x = self.ed_property.value_limit.x

            if val.y < self.ed_property.value_limit.y:
                val.y = self.ed_property.value_limit.y

            if val.z < self.ed_property.value_limit.z:
                val.z = self.ed_property.value_limit.z

        self.__text_ctrl_x.SetValue(str(x))
        self.__text_ctrl_y.SetValue(str(y))
        self.__text_ctrl_z.SetValue(str(z))

    def has_focus(self):
        if self.__text_ctrl_x.HasFocus() or self.__text_ctrl_y.HasFocus() or self.__text_ctrl_z.HasFocus():
            return True
        return False


class EnumProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)

        if sys.platform == "linux":
            self.SetMinSize((-1, 38))
            self.SetMaxSize((-1, 38))
            self.SetSize((-1, 38))

        self.__choice_control = None

    def on_event_choice(self, evt):
        value = self.__choice_control.GetSelection()
        self.set_value(value)
        evt.Skip()

    def create_control(self):
        # label = wx.StaticText(self, label=self.label)
        super(EnumProperty, self).create_control()
        val = self.ed_property.get_choices()
        if type(val) is list:
            pass
        else:
            val = []

        self.__choice_control = wx.Choice(self, choices=val)
        self.__choice_control.SetSelection(self.ed_property.get_value())

        # add to sizer
        self.sizer.Add(self.ed_property_label, 0, wx.EXPAND | wx.TOP, border=Label_Top_Offset)
        self.sizer.Add(self.__choice_control, 1, wx.RIGHT, border=6)

        self.bind_events()
        self.Refresh()

    def bind_events(self):
        self.__choice_control.Bind(wx.EVT_CHOICE, self.on_event_choice)

    def unbind_events(self):
        self.__choice_control.Unbind(wx.EVT_CHOICE)
        self.__choice_control.Unbind(wx.EVT_ENTER_WINDOW)
        self.__choice_control.Unbind(wx.EVT_LEAVE_WINDOW)

    def set_control_value(self, val):
        self.__choice_control.SetSelection(val)


class SliderProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)

        if sys.platform == "linux":
            self.SetMinSize((-1, 28))
            self.SetMaxSize((-1, 28))
            self.SetSize((-1, 28))

        self.__slider = None

    def on_event_slider(self, evt):
        self.set_value(self.__slider.GetValue())
        evt.Skip()

    def create_control(self):
        self.__slider = wx.Slider(self,
                                  value=self.get_value(),
                                  minValue=self.ed_property.min_value,
                                  maxValue=self.ed_property.max_value,
                                  style=wx.SL_HORIZONTAL)

        # add to sizer
        self.sizer.Add(self.ed_property_label, 0, wx.EXPAND | wx.TOP, border=Label_Top_Offset)
        self.sizer.Add(self.__slider, 1, wx.TOP, border=-1)

        self.bind_events()

    def bind_events(self):
        self.__slider.Bind(wx.EVT_SLIDER, self.on_event_slider)

    def unbind_events(self):
        self.__slider.Unbind(wx.EVT_SLIDER)

    def set_control_value(self, val):
        self.__slider.SetValue(int(val))


class ButtonProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.__wx_id = None
        self.__btn = None

    def on_evt_btn(self, evt):
        self.ed_property.execute()
        evt.Skip()

    def create_control(self):
        self.ed_property_label.Destroy()

        self.__btn = wx.Button(self, label=self.ed_property.name)
        self.__btn.SetBackgroundColour(edPreferences.Colors.Panel_Light)
        self.__btn.SetMaxSize((-1, self.GetSize().y))
        self.sizer.Add(self.__btn, 1)
        self.bind_events()

    def bind_events(self):
        self.Bind(wx.EVT_BUTTON, self.on_evt_btn)

    def unbind_events(self):
        self.Unbind(wx.EVT_BUTTON)


class HorizontalLayoutGroup(WxCustomProperty):
    def __init__(self, parent, _property, *args, **kwargs):
        super().__init__(parent, _property, *args, **kwargs)
        self.__properties = []
        self.__property_styling_args = self.ed_property.kwargs.pop("styling", None)

    def set_properties(self, properties):
        self.__properties = properties

    def create_control(self):
        self.ed_property_label.Destroy()
        self.sizer.Clear(True)

        for i in range(len(self.__properties)):
            prop = self.__properties[i]

            if not self.__property_styling_args:
                # -----------------------------------------------------
                # default arguments to sizer if no styling is specified
                if type(prop) in [Vector2Property, Vector3Property, IntProperty, FloatProperty, StringProperty]:
                    self.sizer.Add(prop, 1, wx.EXPAND)
                else:
                    self.sizer.Add(prop, 0)
                # -----------------------------------------------------
            else:
                pass


class FoldoutGroup(WxCustomProperty):

    FOLD_OPEN_ICON = str(pathlib.Path(ICONS_PATH + "/foldOpen_16.png"))
    FOLD_CLOSE_ICON = str(pathlib.Path(ICONS_PATH + "/foldClose_16.png"))

    def __init__(self, parent, property_, *args, **kwargs):
        super().__init__(parent, property_)

        self.__fd_open_icon = None
        self.__fd_close_icon = None
        self.__fd_button = None
        self.__is_open = True
        self.__properties = []
        self.scrolled_panel = kwargs.pop("ScrolledPanel", None)

        self.sizer.Clear()  # delete default sizer
        self.__h_sizer = wx.BoxSizer(wx.HORIZONTAL)  # a sizer for foldout open/close buttons

        # create a vertical sizer to layout wx-properties in this foldout
        self.__v_sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self.__v_sizer, deleteOld=True)

    def on_click(self, evt=None):
        self.__is_open = not self.__is_open

        if self.__is_open:
            self.open()
        else:
            self.close()

        if evt:
            evt.Skip()

    def set_properties(self, properties):
        self.__properties = properties

    def create_control(self):
        super(FoldoutGroup, self).create_control()
        self.create_foldout_buttons()
        self.add_properties()
        self.on_click(None)  # default

    def create_foldout_buttons(self):
        self.__v_sizer.Clear()
        self.__h_sizer.Clear()

        # load foldout open and close icons
        self.__fd_open_icon = wx.Image(FoldoutGroup.FOLD_OPEN_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.__fd_close_icon = wx.Image(FoldoutGroup.FOLD_CLOSE_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        # create the foldout button
        self.__fd_button = wx.StaticBitmap(self, -1, self.__fd_open_icon, (0, 0), size=wx.Size(10, 10))
        self.__fd_button.Bind(wx.EVT_LEFT_DOWN, self.on_click)

        # add them to sizers
        self.__h_sizer.AddSpacer(Control_Margin_Left)
        self.__h_sizer.Add(self.__fd_button, 0, wx.TOP, border=5)
        self.__h_sizer.Add(self.ed_property_label, 0, wx.EXPAND | wx.TOP | wx.LEFT, border=Label_Top_Offset)
        self.__v_sizer.Add(self.__h_sizer, 0, wx.EXPAND)

    def add_properties(self):
        for prop in self.__properties:
            prop.Hide()
            self.__v_sizer.Add(prop, 0, wx.EXPAND | wx.LEFT, border=10)

    def open(self):
        min_size = 22
        for prop in self.__properties:
            min_size += 22
            prop.Show()

        self.SetSize((-1, min_size))
        self.SetMaxSize((-1, min_size))
        self.SetMinSize((-1, min_size))

        self.__fd_button.SetBitmap(self.__fd_open_icon)

        self.__v_sizer.Layout()

        if self.scrolled_panel:
            self.scrolled_panel.PostSizeEvent()
        else:
            self.parent.PostSizeEvent()

    def close(self):
        for prop in self.__properties:
            prop.Hide()

        self.SetSize((-1, 22))
        self.SetMinSize((-1, 22))
        self.SetMaxSize((-1, 22))

        self.__fd_button.SetBitmap(self.__fd_close_icon)

        self.__v_sizer.Layout()

        if self.scrolled_panel:
            self.scrolled_panel.PostSizeEvent()
        else:
            self.parent.PostSizeEvent()

    @property
    def properties(self):
        return self.__properties


class InfoBox(WxCustomProperty):
    def __init__(self, parent, _property, *args, **kwargs):
        super().__init__(parent, _property, *args, **kwargs)

        self.info_text = _property.get_text()
        self.info_panel = None


# maps an editor property object to wx_property object
# see editor.utils.property and editor.wxUI.wxCustomProperties
Property_And_Type = {
    int: IntProperty,
    float: FloatProperty,
    str: StringProperty,
    bool: BoolProperty,

    LVecBase2f: Vector2Property,
    LPoint2f: Vector2Property,

    LVecBase3f: Vector3Property,
    LPoint3f: Vector3Property,

    LColor: ColorProperty,

    "label": LabelProperty,
    "choice": EnumProperty,
    "button": ButtonProperty,
    "slider": SliderProperty,
    "space": EmptySpace,

    "info_box": InfoBox,

    "horizontal_layout_group": HorizontalLayoutGroup,
    "foldout_group": FoldoutGroup,
}
