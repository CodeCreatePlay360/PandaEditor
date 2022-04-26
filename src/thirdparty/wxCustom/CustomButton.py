import wx


class CustomButton(wx.Panel):
    def __init__(self, parent, bg_color, fucn, image, _id=wx.ID_ANY, pos=(0, 0), size=(24, 24), style=wx.BORDER_NONE,
                 img_pos=(0, 0), img_size=(24, 24), *args, **kwargs):

        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.SetBackgroundColour(bg_color)
        self.SetWindowStyle(style)
        self.SetSize(size)
        self.SetPosition(pos)

        # image
        image_ctrl = wx.StaticBitmap(self)
        image = wx.Image(image, type=wx.BITMAP_TYPE_ANY)
        image_ctrl.SetBitmap(wx.Bitmap(image))
        image_ctrl.SetId(_id)
        image_ctrl.SetSize(img_size)
        image_ctrl.SetPosition(img_pos)

        self.active = False
        image_ctrl.Bind(wx.EVT_LEFT_DOWN, fucn)

    def select(self):
        if self.active:
            self.active = False
            self.SetWindowStyle(wx.BORDER_RAISED)

        elif self.active is False:
            self.active = True
            self.SetWindowStyle(wx.BORDER_SUNKEN)
            self.SetWindowStyleFlag(wx.BORDER_SUNKEN)

        self.Refresh()
