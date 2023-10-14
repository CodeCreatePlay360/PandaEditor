import wx
from editor.globals import editor

Selection_btn_color_normal = wx.Colour(110, 110, 110, 255)
Selection_btn_color_pressed = wx.Colour(125, 125, 125, 255)
Selection_btn_color_pressed_dark = wx.Colour(100, 100, 100, 255)
Selection_btn_color_hover = wx.Colour(130, 130, 130, 255)

# button types
__BasicButton__ = 0
__SelectionButton__ = 1
__ToggleButton__ = 2


class ButtonBase(wx.Window):
    def __init__(self, parent, btn_idx, 
                 label_text, 
                 image_path=None, image_scale: tuple = None,
                 select_func=None, deselect_func=None, 
                 data=None, *args, **kwargs):
        wx.Window.__init__(self, parent)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.sizer.AddSpacer(2)

        self.__button_idx = btn_idx
        self.__label_text = label_text
        self.__image_path = image_path
        self.__on_select_func = select_func
        self.__on_deselect_func = deselect_func
        self.__data = data

        self.__text_ctrl = None
        self.__imageCtrl = None

        if self.has_image:
            image = wx.Image(self.__image_path, type=wx.BITMAP_TYPE_ANY)
            if image_scale:
                image = image.Scale(width=image_scale[0], height=image_scale[1])

            self.__imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Image.ConvertToBitmap(image))
            self.sizer.Add(self.__imageCtrl, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 1)

            self.__imageCtrl.Bind(wx.EVT_LEFT_DOWN, self.on_click)
            self.__imageCtrl.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            self.__imageCtrl.Bind(wx.EVT_MOTION, self.on_hover)
            self.__imageCtrl.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)

        self.sizer.AddSpacer(3)

        if self.__label_text is not None:
            self.__text_ctrl = wx.StaticText(self, label=self.__label_text)
            text_ctrl_font = wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.BOLD)
            self.__text_ctrl.SetFont(text_ctrl_font)
            self.__text_ctrl.SetForegroundColour(editor.ui_config.color_map("Text_Primary"))

            self.__text_ctrl.Bind(wx.EVT_LEFT_DOWN, self.on_click)
            self.__text_ctrl.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            self.__text_ctrl.Bind(wx.EVT_MOTION, self.on_hover)
            self.__text_ctrl.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)

            self.sizer.Add(self.__text_ctrl, 0, wx.ALIGN_CENTRE_VERTICAL)

        # defaults
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.SetWindowStyle(wx.BORDER_NONE)
        self.SetBackgroundColour(Selection_btn_color_normal)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)

        self.Refresh()

    @property
    def btn_idx(self):
        return self.__button_idx

    @property
    def image(self):
        return self.__imageCtrl

    @property
    def on_select_func(self):
        return self.__on_select_func

    @property
    def on_deselect_func(self):
        return self.__on_deselect_func

    @property
    def data(self):
        return self.__data

    @property
    def has_image(self):
        return self.__image_path is not None

    def on_hover(self, evt):
        evt.Skip()

    def on_click(self, evt=None):
        if evt:
            evt.Skip()

    def on_left_up(self, evt):
        evt.Skip()

    def on_leave_window(self, evt):
        evt.Skip()


class BasicButton(ButtonBase):
    def __init__(self, *args, **kwargs):
        ButtonBase.__init__(self, *args, **kwargs)
        self.__clear_bg = kwargs.pop("clear_bg", False)
        color = self.GetParent().GetBackgroundColour() if self.__clear_bg else Selection_btn_color_normal
        self.SetBackgroundColour(color)

    @property
    def button_type(self):
        return __BasicButton__

    def on_hover(self, evt):
        self.SetBackgroundColour(Selection_btn_color_hover)
        self.Refresh()
        evt.Skip()

    def on_click(self, evt=None):
        if self.on_select_func:
            self.on_select_func(self.btn_idx, self.data)

        self.SetBackgroundColour(Selection_btn_color_pressed)
        self.Refresh()
        super(BasicButton, self).on_click(evt)

    def on_left_up(self, evt):
        self.SetBackgroundColour(Selection_btn_color_normal)
        self.Refresh()
        evt.Skip()

    def on_leave_window(self, evt):
        color = self.GetParent().GetBackgroundColour() if self.__clear_bg else Selection_btn_color_normal
        self.SetBackgroundColour(color)
        self.Refresh()
        evt.Skip()


class SelectionButton(ButtonBase):
    def __init__(self, *args, **kwargs):
        ButtonBase.__init__(self, *args, **kwargs)
        self.__is_selected = False

    @property
    def button_type(self):
        return __SelectionButton__

    def on_click(self, evt=None):
        if self.on_select_func:
            self.on_select_func(self.btn_idx, self.data)

        self.__is_selected = True
        self.SetBackgroundColour(Selection_btn_color_pressed)
        self.Refresh()
        super(SelectionButton, self).on_click(evt)

    def deselect(self):
        self.__is_selected = False
        self.SetBackgroundColour(Selection_btn_color_normal)
        self.Refresh()

    def on_leave_window(self, evt):
        if self.__is_selected:
            self.SetBackgroundColour(Selection_btn_color_pressed)
        else:
            self.SetBackgroundColour(Selection_btn_color_normal)
        self.Refresh()
        evt.Skip()


class ToggleButton(ButtonBase):
    def __init__(self, *args, **kwargs):
        ButtonBase.__init__(self, *args, **kwargs)
        self.__is_selected = False
        self.__clear_bg = kwargs.pop("clear_bg", False)

        color = self.GetParent().GetBackgroundColour() if self.__clear_bg else Selection_btn_color_normal
        self.SetBackgroundColour(color)

    @property
    def button_type(self):
        return __ToggleButton__

    def on_click(self, evt=None):
        if self.__is_selected:
            self.deselect()
            color = self.GetParent().GetBackgroundColour() if self.__clear_bg else Selection_btn_color_normal
            self.SetBackgroundColour(color)
        else:
            # select it
            self.__is_selected = True
            self.SetBackgroundColour(Selection_btn_color_pressed)
            #
            if self.on_select_func:
                self.on_select_func(self.btn_idx, self.data)

        self.Refresh()
        super(ToggleButton, self).on_click(evt)

    def deselect(self):
        self.__is_selected = False
        if self.on_deselect_func:
            self.on_deselect_func(self.btn_idx)

    def on_hover(self, evt):
        evt.Skip()
