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
        self.parent = parent

        self.property = prop
        self.trigger_property_modify_event = True

        self.h_offset = h_offset

        self.font_colour = edPreferences.Colors.Inspector_properties_label
        self.font_size = 10

        # create fonts
        self.ed_property_font = wx.Font(self.font_size, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.control_label_font = wx.Font(self.font_size, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # ------------------------------------------------------------------------------

        self.ed_property_labels = wx.StaticText(self, label=self.property.name.capitalize())
        self.ed_property_labels.SetFont(self.ed_property_font)
        self.ed_property_labels.SetForegroundColour(self.font_colour)

        self.SetSize((-1, 22))
        self.SetMinSize((-1, 22))
        self.SetMaxSize((-1, 22))

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.AddSpacer(Control_Margin_Left)

        self.SetSizer(self.sizer)
        self.Layout()

    def bind_events(self):
        pass

    def unbind_events(self):
        pass

    def on_control_init(self):
        pass

    def create_control(self):
        size = self.ed_property_labels.GetSize()
        self.ed_property_labels.SetMinSize((size.x + Label_To_Control_Space, size.y))

    def on_control_created(self):
        pass

    def set_control_value(self, val):
        pass

    def set_value(self, val):
        # self.value = val
        property_value = self.property.set_value(val)
        editor.observer.trigger("PropertyModified", self)
        return property_value

    def get_value(self):
        return self.property.get_value()

    def on_event_char(self, evt):
        pass

    def get_type(self):
        return self.property.get_type()

    def has_focus(self):
        return False


class EmptySpace(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.SetSize((-1, self.get_y()))
        self.SetMinSize((-1, self.get_y()))

    def create_control(self):
        pass

    def get_x(self):
        return self.property.x

    def get_y(self):
        return self.property.y


class LabelProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.font = None
        self.ctrl_label = None

    def create_control(self):
        self.ed_property_labels.Destroy()

        if self.property.is_bold:
            self.font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.BOLD)
        else:
            self.font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)

        self.ctrl_label = wx.StaticText(self, label=self.property.name)
        self.ctrl_label.SetFont(self.font)
        self.ctrl_label.SetForegroundColour(edPreferences.Colors.Bold_Label)

        self.sizer.Add(self.ctrl_label, 0, wx.TOP, border=Label_Top_Offset)


class IntProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.text_ctrl = None

        # set this to true if control's value is a valid value according to given condition
        self.valid_value = False

        # last value of text control before updating
        self.old_value = None

    def create_control(self):
        super().create_control()
        self.text_ctrl = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_SUNKEN, id=ID_TEXT_CHANGE)

        # set initial value
        property_value = self.get_value()
        self.old_value = property_value
        self.text_ctrl.SetValue(str(property_value))

        # add to sizer
        self.sizer.Add(self.ed_property_labels, 0, wx.EXPAND | wx.TOP, border=3)
        self.sizer.Add(self.text_ctrl, 1, wx.TOP, border=1)
        self.sizer.AddSpacer(Control_Margin_Right)

        self.bind_events()
        self.Refresh()

    def set_control_value(self, val):
        val = get_rounded_value(val)
        self.text_ctrl.SetValue(str(val))

    def on_event_text(self, evt):
        if is_valid_int(self.text_ctrl.GetValue()):
            self.set_value(int(self.text_ctrl.GetValue()))
            self.old_value = self.text_ctrl.GetValue()
        else:
            # self.text_ctrl_x.SetValue will call this method, so
            # temporarily unbind evt_text to prevent stack overflow
            self.text_ctrl.Unbind(wx.EVT_TEXT)
            self.text_ctrl.SetValue(str(self.old_value))
            self.text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)

        evt.Skip()

    def has_focus(self):
        if self.text_ctrl.HasFocus():
            return True
        return False

    def bind_events(self):
        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)

    def unbind_events(self):
        self.text_ctrl.Unbind(wx.EVT_TEXT)


class FloatProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.text_ctrl = None

        # set this to true if control's value is a valid value according to given condition
        self.valid_value = False

        # last value of text control before updating
        self.old_value = None

    def create_control(self):
        super().create_control()
        self.text_ctrl = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_SUNKEN, id=ID_TEXT_CHANGE)

        # set initial value
        property_value = self.get_value()
        self.text_ctrl.SetValue(str(property_value))

        # add to sizer
        self.sizer.Add(self.ed_property_labels, 0, wx.EXPAND | wx.TOP, border=3)
        self.sizer.Add(self.text_ctrl, 1, wx.TOP, border=1)
        self.sizer.AddSpacer(Control_Margin_Right)

        # bind events
        self.bind_events()
        self.Refresh()

    def set_control_value(self, val):
        val = get_rounded_value(val)
        self.text_ctrl.SetValue(str(val))

    def on_event_text(self, evt):
        if is_valid_float(self.text_ctrl.GetValue()):
            value = float(self.text_ctrl.GetValue())
            if self.property.value_limit is not None:
                if value < self.property.value_limit:
                    value = self.property.value_limit

            self.set_value(value)
            self.old_value = self.text_ctrl.GetValue()
        else:
            # self.text_ctrl_x.SetValue will call this method, so
            # temporarily unbind evt_text to prevent stack overflow
            self.text_ctrl.Unbind(wx.EVT_TEXT)
            self.text_ctrl.SetValue(str(self.old_value))
            self.text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)

        evt.Skip()

    def has_focus(self):
        if self.text_ctrl.HasFocus():
            return True
        return False

    def bind_events(self):
        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)

    def unbind_events(self):
        self.text_ctrl.Unbind(wx.EVT_TEXT)


class StringProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.text_ctrl = None

    def create_control(self):
        super().create_control()

        self.text_ctrl = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_SUNKEN, id=ID_TEXT_CHANGE)
        self.text_ctrl.SetValue(self.get_value())

        # add to sizer
        self.sizer.Add(self.ed_property_labels, 0, wx.EXPAND | wx.TOP, border=3)
        self.sizer.Add(self.text_ctrl, 1, wx.TOP, border=1)
        self.sizer.AddSpacer(Control_Margin_Right)

        self.bind_events()
        self.Refresh()

    def set_control_value(self, val):
        self.text_ctrl.SetValue(str(val))

    def on_event_text(self, evt):
        val = self.text_ctrl.GetValue()
        self.set_value(val)

        evt.Skip()

    def has_focus(self):
        if self.text_ctrl.HasFocus():
            return True
        return False

    def bind_events(self):
        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)

    def unbind_events(self):
        self.text_ctrl.Unbind(wx.EVT_TEXT)


class BoolProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.toggle = None

    def create_control(self):
        # label = wx.StaticText(self, label=self.label)
        super().create_control()
        self.toggle = wx.CheckBox(self, label="", style=0)

        # initial value
        self.toggle.SetValue(self.get_value())
        # add to sizer
        if self.property.name == "":
            self.ed_property_labels.Destroy()
        else:
            self.sizer.Add(self.ed_property_labels, 0, wx.EXPAND | wx.TOP, border=3)
        self.sizer.Add(self.toggle, 0, wx.TOP, border=3)
        self.sizer.AddSpacer(Control_Margin_Right)

        self.bind_events()
        self.Refresh()

    def set_control_value(self, val):
        self.toggle.SetValue(val)

    def on_event_toggle(self, evt):
        self.set_value(self.toggle.GetValue())
        evt.Skip()

    def bind_events(self):
        self.toggle.Bind(wx.EVT_CHECKBOX, self.on_event_toggle)

    def unbind_events(self):
        self.toggle.Unbind(wx.EVT_CHECKBOX)


class ColorProperty(WxCustomProperty):
    class CustomColorSelector(colorSelector.PyColourChooser):
        def __init__(self, color_property, initial_val, *args, **kwargs):
            colorSelector.PyColourChooser.__init__(self, *args, **kwargs)

            self.color_property = color_property
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
            self.color_property.set_value(ColorProperty.get_panda3d_color_object(self.GetValue()))
            self.color_property.Refresh()

    class CustomColorDialog(wx.Dialog):
        def __init__(self, parent, initial_val, title, color_property):
            style = wx.DEFAULT_DIALOG_STYLE | wx.DIALOG_NO_PARENT | wx.STAY_ON_TOP
            super(ColorProperty.CustomColorDialog, self).__init__(parent, title=title, style=style)

            self.SetBackgroundColour(wx.Colour(edPreferences.Colors.Panel_Normal))
            self.SetSize((490, 350))

            self.panel = wx.Panel(self)  # create a background panel
            self.color_selector = ColorProperty.CustomColorSelector(color_property, initial_val, self.panel, -1)

            # create a sizer for panel and add color selector to it
            self.panel_sizer = wx.BoxSizer(wx.VERTICAL)
            self.panel_sizer.Add(self.color_selector, 1, wx.EXPAND)
            self.panel.SetSizer(self.panel_sizer)

            # create a main sizer and add panel to it
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer.Add(self.panel, 1, wx.EXPAND)
            self.SetSizer(self.sizer)

    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.color_panel = None

    def create_control(self):
        super().create_control()
        self.color_panel = wx.Panel(self)
        self.color_panel.SetMaxSize((self.GetSize().x - self.ed_property_labels.GetSize().x - 8, 18))
        self.color_panel.SetWindowStyleFlag(wx.BORDER_SIMPLE)
        self.color_panel.SetBackgroundColour(ColorProperty.get_wx_color_object(self.get_value()))

        # add to sizer
        self.sizer.Add(self.ed_property_labels, 0, wx.EXPAND | wx.TOP, border=3)
        self.sizer.Add(self.color_panel, 1, wx.EXPAND)
        self.sizer.AddSpacer(Control_Margin_Right)

        self.bind_events()

    def set_control_value(self, val):
        self.color_panel.SetBackgroundColour(ColorProperty.get_wx_color_object(val))
        self.Refresh()

    def on_evt_clicked(self, evt):
        value = ColorProperty.get_wx_color_object(self.get_value())
        x = ColorProperty.CustomColorDialog(None, value, "ColorSelectDialog", self)
        x.Show()
        evt.Skip()

    def on_evt_size(self, evt):
        self.color_panel.SetMaxSize((self.GetSize().x - self.ed_property_labels.GetSize().x - 8, 18))
        evt.Skip()

    def bind_events(self):
        self.color_panel.Bind(wx.EVT_LEFT_DOWN, self.on_evt_clicked)
        self.Bind(wx.EVT_SIZE, self.on_evt_size)

    def unbind_events(self):
        self.color_panel.Unbind(wx.EVT_LEFT_DOWN)
        self.Unbind(wx.EVT_SIZE)

    @staticmethod
    def get_wx_color_object(value):
        """converts to wx colour value range from 0-1 range and return a wx color object"""

        value = LColor(value.x, value.y, value.z, value.w)
        value.x = common_maths.map_to_range(0, 1, 0, 255, value.x)
        value.y = common_maths.map_to_range(0, 1, 0, 255, value.y)
        value.z = common_maths.map_to_range(0, 1, 0, 255, value.z)
        value.w = common_maths.map_to_range(0, 1, 0, 255, value.w)
        return wx.Colour(value.x, value.y, value.z, value.w)

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

        self.bold_font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.text_ctrl_x = None
        self.text_ctrl_y = None

        self.old_value = ""

    def create_control(self):
        super(Vector2Property, self).create_control()

        label_x = wx.StaticText(self, label=" x ")
        label_x.SetFont(self.control_label_font)
        label_x.SetForegroundColour(self.font_colour)
        self.text_ctrl_x = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        label_y = wx.StaticText(self, label=" y ")
        label_y.SetFont(self.control_label_font)
        label_y.SetForegroundColour(self.font_colour)
        self.text_ctrl_y = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        # set initial value
        property_value = self.get_value()

        self.text_ctrl_x.SetValue(str(property_value.x))
        self.text_ctrl_y.SetValue(str(property_value.y))

        # self.sizer.Add(self.ed_property_labels, 0, wx.EXPAND | wx.TOP, border=3)
        # self.sizer.Add(self.text_ctrl, 1, wx.TOP, border=1)

        # add to sizer
        self.sizer.Add(self.ed_property_labels, 0, wx.EXPAND | wx.TOP, border=3)

        self.sizer.Add(label_x, 0, wx.TOP, 3)
        self.sizer.Add(self.text_ctrl_x, 1, wx.TOP, border=1)
        self.sizer.Add(label_y, 0, wx.TOP, 3)
        self.sizer.Add(self.text_ctrl_y, 1, wx.TOP, border=1)

        self.sizer.AddSpacer(Control_Margin_Right)

        # bind events
        self.bind_events()
        self.Refresh()

    def set_control_value(self, val):
        # apply value limit
        if self.property.value_limit is not None:
            if val < self.property.value_limit:
                val = self.property.value_limit

        x = get_rounded_value(val.x)
        y = get_rounded_value(val.y)

        self.text_ctrl_x.SetValue(str(x))
        self.text_ctrl_y.SetValue(str(y))

    def on_event_char(self, evt):
        evt.Skip()

    def on_event_text(self, evt):
        # validate h
        if is_valid_float(self.text_ctrl_x.GetValue()):
            is_valid_h = True
        else:
            is_valid_h = False

        # validate p
        if is_valid_float(self.text_ctrl_y.GetValue()):
            is_valid_p = True
        else:
            is_valid_p = False

        if is_valid_h and is_valid_p:
            h = float(self.text_ctrl_x.GetValue())
            p = float(self.text_ctrl_y.GetValue())

            # apply value limit
            if self.property.value_limit is not None:
                if h < self.property.value_limit.x:
                    h = self.property.value_limit.x

                if p < self.property.value_limit.x:
                    p = self.property.value_limit.x

            self.set_value(LVecBase2f(h, p))
            self.old_value = LVecBase2f(h, p)

        else:
            # temporarily unbind events otherwise this will cause a stack overflow,
            # since call to SetValue will call this method again.
            self.bind_events()

            self.text_ctrl_x.SetValue(str(self.old_value.x))
            self.text_ctrl_y.SetValue(str(self.old_value.y))

            # bind events again
            self.unbind_events()

        evt.Skip()

    def has_focus(self):
        if self.text_ctrl_x.HasFocus() or self.text_ctrl_y.HasFocus():
            return True
        return False

    def bind_events(self):
        self.text_ctrl_x.Bind(wx.EVT_TEXT, self.on_event_text)
        self.text_ctrl_y.Bind(wx.EVT_TEXT, self.on_event_text)

    def unbind_events(self):
        self.text_ctrl_x.Unbind(wx.EVT_TEXT)
        self.text_ctrl_y.Unbind(wx.EVT_TEXT)


class Vector3Property(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)

        self.bold_font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.text_ctrl_x = None
        self.text_ctrl_y = None
        self.text_ctrl_z = None

        self.old_value = ""

    def create_control(self):
        # label = wx.StaticText(self, label=self.label)
        super(Vector3Property, self).create_control()

        label_x = wx.StaticText(self, label="x ")
        label_x.SetFont(self.control_label_font)
        label_x.SetForegroundColour(self.font_colour)
        self.text_ctrl_x = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        label_y = wx.StaticText(self, label=" y ")
        label_y.SetFont(self.control_label_font)
        label_y.SetForegroundColour(self.font_colour)
        self.text_ctrl_y = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        label_z = wx.StaticText(self, label=" z ")
        label_z.SetFont(self.control_label_font)
        label_z.SetForegroundColour(self.font_colour)
        self.text_ctrl_z = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        # set initial value
        property_value = self.get_value()
        self.old_value = property_value

        x = get_rounded_value(property_value.x)
        y = get_rounded_value(property_value.y)
        z = get_rounded_value(property_value.z)

        self.text_ctrl_x.SetValue(str(x))
        self.text_ctrl_y.SetValue(str(y))
        self.text_ctrl_z.SetValue(str(z))

        # add to sizer
        self.sizer.Add(self.ed_property_labels, 0, wx.EXPAND | wx.TOP, border=3)

        self.sizer.Add(label_x, 0, wx.TOP, 3)
        self.sizer.Add(self.text_ctrl_x, 1, wx.TOP, border=1)

        self.sizer.Add(label_y, 0, wx.TOP, 3)
        self.sizer.Add(self.text_ctrl_y, 1, wx.TOP, border=1)

        self.sizer.Add(label_z, 0, wx.TOP, 3)
        self.sizer.Add(self.text_ctrl_z, 1, wx.TOP, border=1)

        self.sizer.AddSpacer(Control_Margin_Right)

        self.bind_events()
        self.Refresh()

    def set_control_value(self, val):
        x = get_rounded_value(val.x)
        y = get_rounded_value(val.y)
        z = get_rounded_value(val.z)

        self.text_ctrl_x.SetValue(str(x))
        self.text_ctrl_y.SetValue(str(y))
        self.text_ctrl_z.SetValue(str(z))

    def on_event_char(self, evt):
        evt.Skip()

    def on_event_text(self, evt):
        # validate h
        if is_valid_float(self.text_ctrl_x.GetValue()):
            is_valid_h = True
        else:
            is_valid_h = False

        # validate p
        if is_valid_float(self.text_ctrl_y.GetValue()):
            is_valid_p = True
        else:
            is_valid_p = False

        # validate r
        if is_valid_float(self.text_ctrl_z.GetValue()):
            is_valid_r = True
        else:
            is_valid_r = False

        if is_valid_h and is_valid_p and is_valid_r:
            h = float(self.text_ctrl_x.GetValue())
            p = float(self.text_ctrl_y.GetValue())
            r = float(self.text_ctrl_z.GetValue())

            # apply value limit
            if self.property.value_limit is not None:
                if h < self.property.value_limit.x:
                    h = self.property.value_limit.x

                if p < self.property.value_limit.y:
                    p = self.property.value_limit.y

                if r < self.property.value_limit.z:
                    r = self.property.value_limit.z

            self.set_value(LVecBase3f(h, p, r))
            self.old_value = LVecBase3f(h, p, r)

        else:
            # self.text_ctrl_x.SetValue will call this method, so
            # temporarily unbind evt_text to prevent stack overflow
            self.unbind_events()

            # reset to last known ok value
            self.text_ctrl_x.SetValue(str(self.old_value.x))
            self.text_ctrl_y.SetValue(str(self.old_value.y))
            self.text_ctrl_z.SetValue(str(self.old_value.z))

            # bind again
            self.bind_events()

        evt.Skip()

    def has_focus(self):
        if self.text_ctrl_x.HasFocus() or self.text_ctrl_y.HasFocus() or self.text_ctrl_z.HasFocus():
            return True
        return False

    def bind_events(self):
        self.text_ctrl_x.Bind(wx.EVT_TEXT, self.on_event_text)
        self.text_ctrl_y.Bind(wx.EVT_TEXT, self.on_event_text)
        self.text_ctrl_z.Bind(wx.EVT_TEXT, self.on_event_text)

    def unbind_events(self):
        self.text_ctrl_x.Unbind(wx.EVT_TEXT)
        self.text_ctrl_y.Unbind(wx.EVT_TEXT)
        self.text_ctrl_z.Unbind(wx.EVT_TEXT)


class EnumProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)

        # self.SetSize(0, 28)
        self.choice_control = None

    def create_control(self):
        # label = wx.StaticText(self, label=self.label)
        super(EnumProperty, self).create_control()
        val = self.property.get_choices()
        if type(val) is list:
            pass
        else:
            val = []

        self.choice_control = wx.Choice(self, choices=val)
        self.choice_control.SetSelection(self.property.get_value())

        # add to sizer
        self.sizer.Add(self.ed_property_labels, 0, wx.EXPAND | wx.TOP, border=Label_Top_Offset)
        self.sizer.Add(self.choice_control, 1, wx.RIGHT, border=6)

        self.bind_events()
        self.Refresh()

    def set_control_value(self, val):
        self.choice_control.SetSelection(val)

    def on_event_choice(self, evt):
        value = self.choice_control.GetSelection()
        self.set_value(value)
        evt.Skip()

    def on_evt_size(self, evt):
        evt.Skip()

    def bind_events(self):
        self.Bind(wx.EVT_SIZE, self.on_evt_size)
        self.Bind(wx.EVT_CHOICE, self.on_event_choice)

    def unbind_events(self):
        self.Unbind(wx.EVT_SIZE)
        self.Unbind(wx.EVT_CHOICE)

        self.choice_control.Unbind(wx.EVT_ENTER_WINDOW)
        self.choice_control.Unbind(wx.EVT_LEAVE_WINDOW)


class SliderProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.slider = None

    def create_control(self):
        self.slider = wx.Slider(self,
                                value=self.get_value(),
                                minValue=self.property.min_value,
                                maxValue=self.property.max_value,
                                style=wx.SL_HORIZONTAL)

        # add to sizer
        self.sizer.Add(self.ed_property_labels, 0, wx.EXPAND | wx.TOP, border=Label_Top_Offset)
        self.sizer.Add(self.slider, 1, wx.TOP, border=-1)

        self.bind_events()

    def set_control_value(self, val):
        self.slider.SetValue(int(val))

    def on_event_slider(self, evt):
        self.set_value(self.slider.GetValue())
        evt.Skip()

    def bind_events(self):
        self.Bind(wx.EVT_SLIDER, self.on_event_slider)

    def unbind_events(self):
        self.Unbind(wx.EVT_SLIDER)


class ButtonProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.wx_id = None
        self.btn = None

    def create_control(self):
        self.ed_property_labels.Destroy()
        del self.ed_property_labels

        self.btn = wx.Button(self, label=self.property.name)
        self.btn.SetBackgroundColour(edPreferences.Colors.Panel_Light)
        self.btn.SetMaxSize((-1, self.GetSize().y))
        self.sizer.Add(self.btn, 1)
        self.bind_events()

    def on_evt_btn(self, evt):
        self.property.execute()
        evt.Skip()

    def bind_events(self):
        self.Bind(wx.EVT_BUTTON, self.on_evt_btn)

    def unbind_events(self):
        self.Unbind(wx.EVT_BUTTON)


class HorizontalLayoutGroup(WxCustomProperty):
    def __init__(self, parent, _property, *args, **kwargs):
        super().__init__(parent, _property, *args, **kwargs)
        self.properties = []

        self.property_styling_args = self.property.kwargs.pop("styling", None)  # input arguments for individual
        # properties, when adding them to sizer in self.create_control

        # first verify them
        # arguments must be in form
        # { property_index: (proportion, border, FLAGS) } see wx.BoxSizer documentation
        # format_valid = True
        # if self.property_styling_args:
        #     if isinstance(self.property_styling_args, dict):
        #         for key in self.property_styling_args.keys():
        #             if not isinstance(key, int):
        #                 format_valid = False

        # if not format_valid:
        #     print("Incorrect Property styling structure for {0},"
        #           "must be {1}".format(self.property.label, "{property_index: (proportion, border, FLAGS)}"))

    def create_control(self):
        self.ed_property_labels.Destroy()
        del self.ed_property_labels
        self.sizer.Clear(True)

        for i in range(len(self.properties)):
            prop = self.properties[i]

            if not self.property_styling_args:
                # -----------------------------------------------------
                # default arguments to sizer if no styling is specified
                if type(prop) in [Vector2Property, Vector3Property, IntProperty, FloatProperty, StringProperty]:
                    self.sizer.Add(prop, 1, wx.EXPAND)
                else:
                    self.sizer.Add(prop, 0)
                # -----------------------------------------------------
            else:
                pass


FOLD_OPEN_ICON = ICONS_PATH + "\\" + "foldOpen_16.png"
FOLD_CLOSE_ICON = ICONS_PATH + "\\" + "foldClose_16.png"


class FoldoutGroup(WxCustomProperty):
    def __init__(self, parent, property_, *args, **kwargs):
        super().__init__(parent, property_)

        self.fd_open_icon = None
        self.fd_close_icon = None
        self.fd_button = None
        self.is_open = True
        self.properties = []
        self.scrolled_panel = kwargs.pop("ScrolledPanel", None)

        del self.sizer

        # delete default sizer
        self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # create a vertical sizer to layout wx-properties in this foldout
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.v_sizer)

    def create_control(self):
        super(FoldoutGroup, self).create_control()
        self.create_foldout_buttons()
        self.add_properties()
        # default
        self.on_click(None)

    def create_foldout_buttons(self):
        self.v_sizer.Clear()
        self.h_sizer.Clear()

        # load foldout open and close icons
        self.fd_open_icon = wx.Image(FOLD_OPEN_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.fd_close_icon = wx.Image(FOLD_CLOSE_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        # create the foldout button
        self.fd_button = wx.StaticBitmap(self, -1, self.fd_open_icon, (0, 0), size=wx.Size(10, 10))
        self.fd_button.Bind(wx.EVT_LEFT_DOWN, self.on_click)

        # add them to sizers
        self.h_sizer.AddSpacer(Control_Margin_Left)
        self.h_sizer.Add(self.fd_button, 0, wx.TOP, border=5)
        self.h_sizer.Add(self.ed_property_labels, 0, wx.EXPAND | wx.TOP | wx.LEFT, border=Label_Top_Offset)
        self.v_sizer.Add(self.h_sizer, 0, wx.EXPAND)

    def add_properties(self):
        for prop in self.properties:
            prop.Hide()
            self.v_sizer.Add(prop, 0, wx.EXPAND | wx.LEFT, border=10)

    def on_click(self, evt=None):
        self.is_open = not self.is_open

        if self.is_open:
            self.open()
        else:
            self.close()

        if evt:
            evt.Skip()

    def open(self):
        min_size = 22
        for prop in self.properties:
            min_size += 22
            prop.Show()

        self.SetSize((-1, min_size))
        self.SetMaxSize((-1, min_size))
        self.SetMinSize((-1, min_size))

        self.fd_button.SetBitmap(self.fd_open_icon)

        self.v_sizer.Layout()

        if self.scrolled_panel:
            self.scrolled_panel.PostSizeEvent()
        else:
            self.parent.PostSizeEvent()

    def close(self):
        for prop in self.properties:
            prop.Hide()

        self.SetSize((-1, 22))
        self.SetMinSize((-1, 22))
        self.SetMaxSize((-1, 22))

        self.fd_button.SetBitmap(self.fd_close_icon)

        self.v_sizer.Layout()

        if self.scrolled_panel:
            self.scrolled_panel.PostSizeEvent()
        else:
            self.parent.PostSizeEvent()


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
