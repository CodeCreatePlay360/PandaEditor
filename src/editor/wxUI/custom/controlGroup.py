import wx
import editor.edPreferences as edPreferences


Selection_btn_color_normal = wx.Colour(127, 127, 127, 255)
Selection_btn_color_pressed = wx.Colour(155, 155, 155, 255)
Selection_btn_color_pressed_dark = wx.Colour(110, 110, 110, 255)
Selection_btn_color_hover = wx.Colour(145, 145, 145, 255)

# button types
__BasicButton__ = 0
__SelectionButton__ = 1
__ToggleButton__ = 2


class ButtonBase(wx.Window):
    def __init__(self,
                 parent,
                 btn_index,
                 label_text,
                 start_offset=0,
                 text_pos=(22, 2), text_flags=None, text_border=None,
                 image_path=None, image_pos=(3, 2), image_scale=14.0, image_flags=None, image_border=None,
                 image_to_text_space=0,
                 select_func=None, deselect_func=None,
                 bg_color=Selection_btn_color_normal,
                 data=None,
                 *args, **kwargs):

        wx.Window.__init__(self, parent)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.sizer.AddSpacer(start_offset)

        self.button_type = -1
        self.parent = parent

        self.button_index = btn_index
        self.image_position = image_pos
        self.image_scale = image_scale
        self.image_path = image_path
        self.has_image = self.image_path is not None

        self.text_pos = text_pos
        self.label_text = label_text
        self.text_flags = text_flags
        self.text_border = text_border

        self.on_select_func_call = select_func
        self.on_deselect_func_call = deselect_func

        self.is_selected = False

        self.text_ctrl = None
        self.imageCtrl = None
        self.image_flags = image_flags
        self.image_border = image_border

        self.background_color = bg_color
        self.data = data

        if self.has_image:
            self.image = wx.Image(self.image_path, type=wx.BITMAP_TYPE_ANY)
            self.image = self.image.Scale(int(self.image_scale), int(self.image_scale))
            self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Image.ConvertToBitmap(self.image))

            if not self.image_flags:
                image_flags = wx.EXPAND
            if not self.image_border:
                image_border = 0

            self.sizer.Add(self.imageCtrl, 0, image_flags, image_border)

            self.imageCtrl.Bind(wx.EVT_LEFT_DOWN, self.on_click)
            self.imageCtrl.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            self.imageCtrl.Bind(wx.EVT_MOTION, self.on_hover)
            self.imageCtrl.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)

        # add image to text space
        self.sizer.AddSpacer(image_to_text_space)

        if self.label_text is not None:
            self.text_ctrl = wx.StaticText(self, label=self.label_text)
            self.text_ctrl_font = wx.Font(8, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            self.text_ctrl.SetFont(self.text_ctrl_font)
            self.text_ctrl.SetForegroundColour(edPreferences.Colors.Bold_Label)\

            if not self.text_flags:
                text_flags = wx.EXPAND
            if not self.text_border:
                text_border = 0

            self.sizer.Add(self.text_ctrl, 0, text_flags, text_border)

            self.text_ctrl.Bind(wx.EVT_LEFT_DOWN, self.on_click)
            self.text_ctrl.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            self.text_ctrl.Bind(wx.EVT_MOTION, self.on_hover)
            self.text_ctrl.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)

        # defaults
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.SetWindowStyle(wx.BORDER_NONE)
        self.SetBackgroundColour(self.background_color)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)

        self.Refresh()

    def on_click(self, evt=None):
        pass

    def on_left_up(self, evt):
        evt.Skip()

    def deselect(self):
        pass

    def on_hover(self, evt):
        if not self.is_selected:
            self.SetBackgroundColour(Selection_btn_color_hover)
            self.Refresh()
        evt.Skip()

    def on_leave_window(self, evt):
        evt.Skip()


class BasicButton(ButtonBase):
    def __init__(self, *args, **kwargs):
        ButtonBase.__init__(self, *args, **kwargs)
        self.button_type = __BasicButton__

    def on_click(self, evt=None):
        self.is_selected = False
        self.parent.select_button_index = self.button_index
        self.SetBackgroundColour(Selection_btn_color_pressed_dark)
        self.Refresh()
        if self.on_select_func_call:
            self.on_select_func_call(self.button_index, self.data)

        if evt:
            evt.Skip()

    def on_left_up(self, evt):
        self.SetBackgroundColour(self.background_color)
        self.Refresh()
        evt.Skip()

    def on_leave_window(self, evt):
        self.SetBackgroundColour(self.background_color)
        self.Refresh()
        evt.Skip()


class SelectionButton(ButtonBase):
    def __init__(self, *args, **kwargs):
        ButtonBase.__init__(self, *args, **kwargs)
        self.button_type = __SelectionButton__

    def on_click(self, evt=None):
        if self.on_select_func_call:
            self.on_select_func_call(self.button_index, self.data)

        self.is_selected = True
        self.SetBackgroundColour(Selection_btn_color_pressed)
        self.Refresh()

        if evt:
            evt.Skip()

    def deselect(self):
        self.is_selected = False
        self.SetBackgroundColour(Selection_btn_color_normal)
        self.Refresh()

    def on_leave_window(self, evt):
        if self.is_selected:
            self.SetBackgroundColour(Selection_btn_color_pressed)
        else:
            self.SetBackgroundColour(Selection_btn_color_normal)
        self.Refresh()
        evt.Skip()


class ToggleButton(ButtonBase):
    def __init__(self, *args, **kwargs):
        ButtonBase.__init__(self, *args, **kwargs)
        self.button_type = __ToggleButton__

        self.selected_color = kwargs.pop("selected_color", Selection_btn_color_pressed)
        self.deselected_color = kwargs.pop("deselected_color", Selection_btn_color_normal)

        self.SetBackgroundColour(self.deselected_color)

    def on_click(self, event=None, **kwargs):
        if self.is_selected:
            self.deselect()
            color = self.deselected_color if self.deselected_color else Selection_btn_color_normal
            self.SetBackgroundColour(color)
        else:
            # select it
            self.is_selected = True
            color = self.selected_color if self.selected_color else Selection_btn_color_pressed
            self.SetBackgroundColour(color)
            #
            if self.on_select_func_call:
                self.on_select_func_call(self.button_index, self.data)

        self.Refresh()
        if event:
            event.Skip()

    def deselect(self):
        self.is_selected = False
        if self.on_deselect_func_call:
            self.on_deselect_func_call(self.button_index)

    def on_hover(self, evt):
        evt.Skip()
