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


class ControlGroup(wx.Panel):
    def __init__(self, parent, size=wx.Size(-1, 18), max_size=wx.Size(-1, 18), *args, **kwargs):
        """on_select = the function to call when a button is selected"""

        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.SetMinSize(size)
        self.SetMaxSize(max_size)
        self.SetWindowStyleFlag(wx.BORDER_NONE)
        self.SetBackgroundColour(parent.GetBackgroundColour())

        self.parent = parent

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        self.buttons = []
        self.selected_btn_index = -1

    def add_button(self, selection_btn, flags=wx.EXPAND, border=0):
        self.sizer.Add(selection_btn, 1, flags, border=border)
        self.sizer.Layout()
        self.buttons.append(selection_btn)

    def select_button(self, at_index, **kwargs):
        if at_index < len(self.buttons):
            self.buttons[at_index].on_click(**kwargs)
            self.selected_btn_index = at_index
        else:
            print("[SelectionGrid] Unable to select button, invalid index {0}", at_index)
            self.selected_btn_index = -1

    def deselect_all(self):
        for btn in self.buttons:
            btn.deselect()
        self.selected_btn_index = -1


class ButtonBase(wx.Window):
    def __init__(self,
                 parent,
                 btn_index,
                 label_text, text_pos=(22, 2), center_text=False,
                 image_path="", image_pos=(3, 2), image_scale=14.0,
                 select_func=None, deselect_func=None,
                 bg_color=None,
                 data=None,
                 *args, **kwargs):

        wx.Window.__init__(self, parent)

        self.button_type = -1
        self.parent = parent

        self.button_index = btn_index
        self.image_position = image_pos
        self.image_scale = image_scale
        self.image_path = image_path
        self.has_image = self.image_path != ""

        self.text_pos = text_pos
        self.label_text = label_text
        self.center_text = center_text

        self.on_select_func_call = select_func
        self.on_deselect_func_call = deselect_func

        self.is_selected = False

        self.text_ctrl = None
        self.imageCtrl = None

        self.data = data
        self.background_color = bg_color

        if self.has_image:
            self.image = wx.Image(self.image_path, type=wx.BITMAP_TYPE_ANY)
            self.image = self.image.Scale(self.image_scale, self.image_scale)
            self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Image.ConvertToBitmap(self.image))

            self.imageCtrl.Bind(wx.EVT_LEFT_DOWN, self.on_click)
            self.imageCtrl.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            self.imageCtrl.Bind(wx.EVT_MOTION, self.on_hover)
            self.imageCtrl.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)

        if self.label_text != "":
            self.text_ctrl = wx.StaticText(self, label=self.label_text)
            self.text_ctrl_font = wx.Font(8, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            self.text_ctrl.SetFont(self.text_ctrl_font)
            self.text_ctrl.SetForegroundColour(edPreferences.Colors.Bold_Label)

            self.text_ctrl.Bind(wx.EVT_MOTION, self.on_hover)
            self.text_ctrl.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)

        self.set_defaults()

        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def set_defaults(self):
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.SetWindowStyle(wx.BORDER_NONE)

        if self.background_color:
            pass
        else:
            self.background_color = Selection_btn_color_normal

        self.SetBackgroundColour(self.background_color)
        self.Refresh()

    def on_click(self, evt=None):
        pass

    def on_left_up(self, evt):
        evt.Skip()

    def deselect(self):
        self.SetBackgroundColour(Selection_btn_color_normal)
        self.is_selected = False
        if self.on_deselect_func_call:
            self.on_deselect_func_call(self.button_index)
        self.Refresh()

    def on_hover(self, evt):
        if not self.is_selected:
            self.SetBackgroundColour(Selection_btn_color_hover)
            self.Refresh()
        evt.Skip()

    def on_leave_window(self, evt):
        evt.Skip()

    def on_size(self, event):
        if self.has_image:
            self.imageCtrl.SetPosition(self.image_position)

        if self.text_ctrl and self.center_text:
            self.text_ctrl.SetPosition((self.GetSize().x/2-self.text_ctrl.GetSize().x/2, self.text_pos[1]))
        else:
            if self.text_ctrl:
                self.text_ctrl.SetPosition(self.text_pos)

        self.Refresh()
        event.Skip()


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
        self.parent.deselect_all()
        self.parent.select_button_index = self.button_index
        self.is_selected = True
        self.SetBackgroundColour(Selection_btn_color_pressed)

        if self.on_select_func_call:
            self.on_select_func_call(self.button_index, self.data)

        if evt:
            evt.Skip()

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

    def on_click(self, event=None, **kwargs):
        if self.is_selected:
            self.deselect()
            self.SetBackgroundColour(self.background_color)
        else:
            # select it
            self.is_selected = True
            self.SetBackgroundColour(Selection_btn_color_normal)
            if self.on_select_func_call:
                self.on_select_func_call(self.button_index, self.data)

        self.Refresh()
        if event:
            event.Skip()

    def on_hover(self, evt):
        evt.Skip()

