import wx
import wx.lib.agw.gradientbutton as gbtn
import wx.lib.colourchooser.pycolourchooser as colorSelector

from panda3d.core import Vec3, Vec2, LColor
from editor.constants import obs, object_manager, LevelEditorEventHandler
from editor.colourPalette import ColourPalette as Colours

# IDs
ID_TEXT_CHANGE = wx.NewId()

# constants
CONTROL_MARGIN_RIGHT = 1
LABEL_TO_CNTRL_SPACE = 10

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
        self.SetBackgroundColour(wx.Colour(Colours.NORMAL_GREY))

        self.parent = parent

        self.property = prop
        self.label = self.property.get_name()
        self.value = self.property.get_value()

        self.trigger_property_modify_event = True

        self.h_offset = h_offset

        self.font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.text_colour = wx.Colour(255, 255, 190, 255)

        self.ctrlLabel = wx.StaticText(self, label=self.label)
        self.ctrlLabel.SetFont(self.font)
        self.ctrlLabel.SetForegroundColour(self.text_colour)

        self.SetSize(0, 22)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.AddSpacer(self.h_offset)

        self.SetSizer(self.sizer)
        self.Layout()

    def bind_events(self):
        pass

    def unbind_events(self):
        pass

    def on_control_init(self):
        pass

    def create_control(self):
        self.ctrlLabel.SetMinSize((self.ctrlLabel.GetSize().x + LABEL_TO_CNTRL_SPACE,
                                   self.ctrlLabel.GetSize().y))

    def on_control_created(self):
        pass

    def set_control_value(self, val, **kwargs):
        pass

    def set_value(self, val):
        self.value = val
        property_value = self.property.set_value(val)

        return property_value

    def get_value(self):
        return self.property.get_value()

    def on_event_char(self, evt):
        pass

    def get_type(self):
        return self.property.get_type()

    '''
    def on_event_text(self, evt, val):
        obs.trigger("PropertyModified", self.property, val)
        evt.Skip()
    '''


class EmptySpace(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)

        # self.space_x = self.property.x
        # self.space_y = self.property.y

    def create_control(self):
        pass

    def get_x(self):
        return self.property.x

    def get_y(self):
        return self.property.y


class LabelProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)

        self.ctrlLabel.Destroy()

        if self.property.is_bold:
            self.font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        else:
            self.font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

        self.ctrlLabel = wx.StaticText(self, label=self.label)
        self.ctrlLabel.SetFont(self.font)
        self.ctrlLabel.SetForegroundColour(self.text_colour)

        self.sizer.Add(self.ctrlLabel, 0)

    def create_control(self):
        pass


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

        # add to sizers
        self.sizer.Add(self.ctrlLabel, 0)
        self.sizer.Add(self.text_ctrl, 1)
        self.sizer.AddSpacer(CONTROL_MARGIN_RIGHT)

        # bind events
        self.text_ctrl.Bind(wx.EVT_CHAR, self.on_event_char)
        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)
        self.text_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

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

    def on_event_char(self, evt):
        evt.Skip()

    def on_key_down(self, evt):
        evt.Skip()
        return
        key_code = evt.GetKeyCode()
        # Allow ASCII numerics
        if ord('0') <= key_code <= ord('9'):
            evt.Skip()

        # Allow decimal points
        if key_code == 46:
            evt.Skip()

        else:
            return

        evt.Skip()


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

        # add to sizers
        self.sizer.Add(self.ctrlLabel, 0)
        self.sizer.Add(self.text_ctrl, 1)
        self.sizer.AddSpacer(CONTROL_MARGIN_RIGHT)

        # bind events
        self.text_ctrl.Bind(wx.EVT_CHAR, self.on_event_char)
        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)
        self.text_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        self.Refresh()

    def set_control_value(self, val):
        val = get_rounded_value(val)
        self.text_ctrl.SetValue(str(val))

    def on_event_char(self, evt):
        evt.Skip()

    def on_event_text(self, evt):
        if is_valid_float(self.text_ctrl.GetValue()):
            self.set_value(float(self.text_ctrl.GetValue()))
            self.old_value = self.text_ctrl.GetValue()
        else:
            # self.text_ctrl_x.SetValue will call this method, so
            # temporarily unbind evt_text to prevent stack overflow
            self.text_ctrl.Unbind(wx.EVT_TEXT)

            self.text_ctrl.SetValue(str(self.old_value))

            self.text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)

        evt.Skip()

    def on_key_down(self, evt):
        evt.Skip()
        '''
        key_code = evt.GetKeyCode()
        # Allow ASCII numerics, decimals
        if ord('0') <= key_code <= ord('9') or key_code == 46:
            evt.Skip()
        else:
            return
        '''


class StringProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.text_ctrl = None

    def create_control(self):
        # create fields
        # label = wx.StaticText(self, label=self.label)
        super().create_control()

        self.text_ctrl = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_SUNKEN, id=ID_TEXT_CHANGE)

        # set initial value
        property_value = self.get_value()
        self.text_ctrl.SetValue(property_value)

        # bind events
        self.text_ctrl.Bind(wx.EVT_CHAR, self.on_event_char)
        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_event_text)

        # add to sizers
        self.sizer.Add(self.ctrlLabel, 0, wx.EXPAND)
        self.sizer.Add(self.text_ctrl, 1)
        self.sizer.AddSpacer(CONTROL_MARGIN_RIGHT)

        self.Refresh()

    def set_control_value(self, val):
        self.text_ctrl.SetValue(str(val))

    def on_event_text(self, evt):
        val = self.text_ctrl.GetValue()
        self.set_value(val)

        evt.Skip()

    def on_event_char(self, evt):
        evt.Skip()

    def on_key_down(self, evt):
        evt.Skip()


class BoolProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.toggle = None

    def create_control(self):
        # label = wx.StaticText(self, label=self.label)
        super().create_control()
        self.toggle = wx.CheckBox(self, label="", style=0)
        # initial value
        property_value = self.get_value()
        self.toggle.SetValue(property_value)
        # bind events
        self.toggle.Bind(wx.EVT_CHECKBOX, self.on_event_toggle)
        # add to sizers
        self.sizer.Add(self.ctrlLabel, 0, wx.EXPAND | wx.TOP, border=-1)
        self.sizer.Add(self.toggle, 0)
        self.sizer.AddSpacer(CONTROL_MARGIN_RIGHT)

        self.Refresh()

    def set_control_value(self, val):
        self.toggle.SetValue(val)

    def on_event_toggle(self, evt):
        self.set_value(self.toggle.GetValue())
        evt.Skip()


class ColorProperty(WxCustomProperty):
    class CustomColorSelector(colorSelector.PyColourChooser):
        def __init__(self, color_property, initial_val, *args, **kwargs):
            colorSelector.PyColourChooser.__init__(self, *args, **kwargs)

            # the actual wx color property 
            self.color_property = color_property

            # set the inital colour value
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
            val = self.GetValue()

            colour = self.GetValue()

            colour = wx.Colour(colour.red, colour.green, colour.blue, colour.alpha)
            self.color_property.color_panel.SetBackgroundColour(colour)

            # convert to panda3d colour object
            colour = LColor(colour.red, colour.green, colour.blue, colour.alpha)
            self.color_property.set_value(colour)

            self.color_property.Refresh()

    class CustomColorDialog(wx.Dialog):
        def __init__(self, parent, initial_val, title, color_property):
            super(ColorProperty.CustomColorDialog, self).__init__(parent,
                                                                  title=title,
                                                                  style=wx.DEFAULT_DIALOG_STYLE |
                                                                        wx.DIALOG_NO_PARENT |
                                                                        wx.STAY_ON_TOP)

            self.SetBackgroundColour(wx.Colour(Colours.NORMAL_GREY))
            self.SetSize((490, 350))

            # create a backgound panel
            self.panel = wx.Panel(self)

            # create a py color selector
            # self.color_selector = colorSelector.PyColourChooser(self.panel, -1)
            self.color_selector = ColorProperty.CustomColorSelector(
                color_property,
                initial_val,
                self.panel,
                -1)

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

    def create_control(self):
        # label = wx.StaticText(self, label=self.label)
        super().create_control()
        self.color_panel = wx.Panel(self)
        self.color_panel.SetMaxSize((self.GetSize().x - self.ctrlLabel.GetSize().x - 8, 18))
        self.color_panel.SetWindowStyleFlag(wx.BORDER_SIMPLE)

        property_val = self.get_value()
        colour = wx.Colour(property_val.x, property_val.y, property_val.z, property_val.w)
        self.color_panel.SetBackgroundColour(colour)

        # add to sizers
        self.sizer.Add(self.ctrlLabel, 0, wx.EXPAND)
        self.sizer.Add(self.color_panel, 1, wx.EXPAND)
        self.sizer.AddSpacer(CONTROL_MARGIN_RIGHT)

        self.color_panel.Bind(wx.EVT_LEFT_DOWN, self.on_evt_clicked)
        self.Bind(wx.EVT_SIZE, self.on_evt_size)

        # self.Refresh()

    def set_control_value(self, val):
        # convert from panda3d.core.LColor to wx.Colour object
        colour = wx.Colour(val.x, val.y, val.z, val.w)
        self.color_panel.SetBackgroundColour(colour)
        self.Refresh()

    def on_evt_clicked(self, evt):
        initial_val = self.get_value()

        initial_val = wx.Colour(initial_val.x, initial_val.y,
                                initial_val.z, alpha=initial_val.w)

        x = ColorProperty.CustomColorDialog(None,
                                            initial_val,
                                            "ColorSelectDialog",
                                            self)
        x.Show()
        # self.Refresh()

        evt.Skip()

    def on_evt_size(self, evt):
        self.color_panel.SetMaxSize((self.GetSize().x - self.ctrlLabel.GetSize().x - 8, 18))
        evt.Skip()


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
        # label = wx.StaticText(self, label=self.label)
        super(Vector2Property, self).create_control()

        label_x = wx.StaticText(self, label="H")
        label_x.SetFont(self.bold_font)
        label_x.SetForegroundColour(self.text_colour)
        self.text_ctrl_x = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        label_y = wx.StaticText(self, label="P")
        label_y.SetFont(self.bold_font)
        label_y.SetForegroundColour(self.text_colour)
        self.text_ctrl_y = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        # set initial value
        property_value = self.get_value()

        self.text_ctrl_x.SetValue(str(property_value.x))
        self.text_ctrl_y.SetValue(str(property_value.y))

        # add to sizers
        self.sizer.Add(self.ctrlLabel, 0, wx.EXPAND)
        # self.sizer.AddSpacer(LABEL_TO_CONTROL_MARGIN)
        self.sizer.Add(label_x, 0, wx.RIGHT | wx.TOP, 1)
        self.sizer.Add(self.text_ctrl_x, 1, wx.LEFT | wx.RIGHT, 1)
        self.sizer.Add(label_y, 0, wx.RIGHT | wx.TOP, 1)
        self.sizer.Add(self.text_ctrl_y, 1, wx.LEFT | wx.RIGHT, 1)
        self.sizer.AddSpacer(CONTROL_MARGIN_RIGHT)

        # bind events
        self.bind_events()
        self.Refresh()

    def bind_events(self):
        self.text_ctrl_x.Bind(wx.EVT_TEXT, self.on_event_text)
        self.text_ctrl_y.Bind(wx.EVT_TEXT, self.on_event_text)

    def unbind_events(self):
        self.text_ctrl_x.Unbind(wx.EVT_TEXT)
        self.text_ctrl_y.Unbind(wx.EVT_TEXT)

    def set_control_value(self, val):
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

            self.set_value(Vec2(h, p))
            self.old_value = Vec2(h, p)

        else:
            # temporarily unbind events otherwise this will cause a stack overflow,
            # since call to SetValue will call this method again.
            self.bind_events()

            self.text_ctrl_x.SetValue(str(self.old_value.x))
            self.text_ctrl_y.SetValue(str(self.old_value.y))

            # bind events again
            self.unbind_events()

        evt.Skip()

    def on_key_down(self, evt):
        evt.Skip()


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

        label_x = wx.StaticText(self, label="H")
        label_x.SetFont(self.bold_font)
        label_x.SetForegroundColour(self.text_colour)
        self.text_ctrl_x = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        label_y = wx.StaticText(self, label="P")
        label_y.SetFont(self.bold_font)
        label_y.SetForegroundColour(self.text_colour)
        self.text_ctrl_y = wx.TextCtrl(self, size=(0, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)

        label_z = wx.StaticText(self, label="R")
        label_z.SetFont(self.bold_font)
        label_z.SetForegroundColour(self.text_colour)
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

        # add to sizers
        self.sizer.Add(self.ctrlLabel, 0, wx.EXPAND)
        # self.sizer.AddSpacer(LABEL_TO_CONTROL_MARGIN)
        self.sizer.Add(label_x, 0, wx.RIGHT | wx.TOP, 1)
        self.sizer.Add(self.text_ctrl_x, 1, wx.LEFT | wx.RIGHT, 1)

        self.sizer.Add(label_y, 0, wx.RIGHT | wx.TOP, 1)
        self.sizer.Add(self.text_ctrl_y, 1, wx.LEFT | wx.RIGHT, 1)

        self.sizer.Add(label_z, 0, wx.RIGHT | wx.TOP, 1)
        self.sizer.Add(self.text_ctrl_z, 1, wx.LEFT | wx.RIGHT, 1)

        self.sizer.AddSpacer(CONTROL_MARGIN_RIGHT)

        # bind events
        self.bind_events()

        self.Refresh()

    def bind_events(self):
        # self.text_ctrl_x.Bind(wx.EVT_CHAR, self.on_event_char)
        # self.text_ctrl_y.Bind(wx.EVT_CHAR, self.on_event_char)
        # self.text_ctrl_z.Bind(wx.EVT_CHAR, self.on_event_char)

        self.text_ctrl_x.Bind(wx.EVT_TEXT, self.on_event_text)
        self.text_ctrl_y.Bind(wx.EVT_TEXT, self.on_event_text)
        self.text_ctrl_z.Bind(wx.EVT_TEXT, self.on_event_text)

        # self.text_ctrl_x.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        # self.text_ctrl_y.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        # self.text_ctrl_z.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def unbind_events(self):
        # self.text_ctrl_x.Unbind(wx.EVT_CHAR)
        # self.text_ctrl_y.Unbind(wx.EVT_CHAR)
        # self.text_ctrl_z.Unbind(wx.EVT_CHAR)

        self.text_ctrl_x.Unbind(wx.EVT_TEXT)
        self.text_ctrl_y.Unbind(wx.EVT_TEXT)
        self.text_ctrl_z.Unbind(wx.EVT_TEXT)

        # self.text_ctrl_x.Unbind(wx.EVT_KEY_DOWN)
        # self.text_ctrl_y.Unbind(wx.EVT_KEY_DOWN)
        # self.text_ctrl_z.Unbind(wx.EVT_KEY_DOWN)

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

                if p < self.property.value_limit.x:
                    p = self.property.value_limit.x

                if r < self.property.value_limit.x:
                    r = self.property.value_limit.x

            self.set_value(Vec3(h, p, r))
            self.old_value = Vec3(h, p, r)

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

    def on_key_down(self, evt):
        evt.Skip()


class EnumProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)

        self.SetSize(0, 28)
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
        self.choice_control.SetSelection(self.value)

        # add to sizers
        self.sizer.Add(self.ctrlLabel, 0, wx.TOP, border=3)
        self.sizer.Add(self.choice_control, 0)

        self.Bind(wx.EVT_SIZE, self.on_evt_size)
        self.Bind(wx.EVT_CHOICE, self.on_event_choice)

        self.choice_control.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter)
        self.choice_control.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)

        self.Refresh()

    def set_control_value(self, val):
        self.choice_control.SetSelection(val)

    def on_event_choice(self, evt):
        value = self.choice_control.GetSelection()
        self.set_value(value)
        evt.Skip()

    def on_evt_size(self, evt):
        self.choice_control.SetMinSize((self.parent.GetSize().x - 8, 22))
        evt.Skip()

    def on_mouse_enter(self, evt):
        LevelEditorEventHandler.UPDATE_XFORM_TASK = False
        evt.Skip()

    def on_mouse_leave(self, evt):
        LevelEditorEventHandler.UPDATE_XFORM_TASK = True
        evt.Skip()


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

        # add to sizers
        self.sizer.Add(self.ctrlLabel, 0, wx.TOP, border=2)
        self.sizer.Add(self.slider, 1)

        self.Bind(wx.EVT_SLIDER, self.on_event_slider)

    def set_control_value(self, val):
        self.slider.SetValue(int(val))

    def on_event_slider(self, evt):
        self.set_value(self.slider.GetValue())
        evt.Skip()

    def on_evt_size(self, evt):
        evt.Skip()


class ButtonProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.wx_id = None
        self.btn = None

    def create_control(self):
        self.ctrlLabel.Destroy()
        del self.ctrlLabel

        self.btn = gbtn.GradientButton(self, label=self.property.get_name())
        self.sizer.Add(self.btn, 1, wx.LEFT | wx.RIGHT)
        self.sizer.AddSpacer(CONTROL_MARGIN_RIGHT)

        self.Bind(wx.EVT_BUTTON, self.on_evt_btn)

    def on_evt_btn(self, evt):
        self.property.execute()
        evt.Skip()


class ContainerProperty(WxCustomProperty):
    def __init__(self, parent, prop, *args, **kwargs):
        super().__init__(parent, prop, *args, **kwargs)
        self.SetBackgroundColour(wx.Colour(Colours.DARK_GREY))

        self.properties = []
        self.expanded = False

    def create_control(self):
        self.panel = wx.Panel(self)
        self.panel.SetMaxSize((0, 18))
        self.panel.SetWindowStyleFlag(wx.BORDER_SIMPLE)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.on_evt_clicked)

        # add self.panel to sizers
        self.sizer.Add(self.panel, 1, wx.EXPAND)
        self.sizer.AddSpacer(CONTROL_MARGIN_RIGHT)

        # destroy the default property label
        self.ctrlLabel.Destroy()

        # create a panel label
        label = wx.StaticText(self.panel, label=self.label)
        label.SetPosition(wx.Point(0, 1))
        label.SetFont(self.font)
        label.SetForegroundColour(wx.Colour(255, 255, 255, 255))

        self.Bind(wx.EVT_SIZE, self.on_evt_size)

    def set_control_value(self, val):
        self.property.set_value(val)
        for prop in self.properties:
            info = prop.property.get_list_item_info()
            prop.set_control_value(val[info.index])

    def on_evt_clicked(self, evt):
        if self.expanded is True:
            self.parent.excluded_controls = []
            self.expanded = False

        elif self.expanded is False:
            self.parent.excluded_controls = self.properties
            self.expanded = True

        self.parent.update_controls()
        object_manager.get("PropertiesPanel").fold_manager.refresh()
        evt.Skip()

    def on_evt_size(self, evt):
        self.panel.SetMaxSize((self.parent.GetSize().x - 10, 18))
        evt.Skip()


class ListProperty(ContainerProperty):
    def __init__(self, *args, **kwargs):
        ContainerProperty.__init__(self, *args, **kwargs)


class StaticBox(WxCustomProperty):
    def __init__(self, parent, property, *args, **kwargs):
        super().__init__(parent, property, *args, **kwargs)
        self.static_box = None
        self.static_box_sizer = None

    def create_control(self):
        # destroy the default property label
        self.ctrlLabel.Destroy()

        self.static_box = wx.StaticBox(self, label=self.label)
        self.static_box.SetForegroundColour(self.text_colour)
        self.static_box.SetFont(self.font)

        self.text_ctrl_x = wx.TextCtrl(self.static_box, size=(55, 18), style=wx.BORDER_DOUBLE, id=ID_TEXT_CHANGE)
        self.text_ctrl_x.SetPosition(wx.Point(2, 22))

        self.Bind(wx.EVT_SIZE, self.on_evt_size)

    def on_evt_size(self, evt):
        self.SetSize((self.parent.GetSize().x - 16, 55))

        self.static_box.SetSize((self.GetSize().x - 6, self.GetSize().y))
        self.static_box.SetPosition(wx.Point(3, 0))

        evt.Skip()


class ObjectControl(WxCustomProperty):
    def __init__(self, parent, property, *args, **kwargs):
        super().__init__(parent, property, *args, **kwargs)
        self.obj_control = None

    def create_control(self):
        super().create_control()

        self.obj_control = wx.Panel(self)
        self.obj_control.SetMaxSize((self.GetSize().x - self.ctrlLabel.GetSize().x - 8, 18))
        self.obj_control.SetWindowStyleFlag(wx.BORDER_SIMPLE)

        self.color_panel.SetBackgroundColour(colour)

        # add to sizers
        self.sizer.Add(self.ctrlLabel, 0, wx.EXPAND)
        self.sizer.Add(self.obj_control, 1, wx.EXPAND)
        self.sizer.AddSpacer(CONTROL_MARGIN_RIGHT)

        self.obj_control.Bind(wx.EVT_LEFT_DOWN, self.on_evt_clicked)
        # self.Bind(wx.EVT_SIZE, self.on_evt_size)

    def on_event_clicked(self, evt):
        evt.Skip()
        pass
