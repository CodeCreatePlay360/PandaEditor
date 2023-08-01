import pathlib
import wx
import editor.constants as constants


TextBox_Cursor = str(pathlib.Path(constants.ICONS_PATH + "/text_box_cursor.png"))
REFRESH_ICON = str(pathlib.Path(constants.ICONS_PATH + "/arrow_refresh.png"))
MAGNIFYING_GLASS_ICON = str(pathlib.Path(constants.ICONS_PATH + "/magnifyingGlassIcon.png"))
SEARCH_CANCEL_ICON = str(pathlib.Path(constants.ICONS_PATH + "/cancel.png"))


class SearchBox(wx.Panel):
    def __init__(self, parent, size=wx.Size(-1, 18), *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.SetMaxSize(size)
        self.SetBackgroundColour(wx.Colour(100, 100, 100, 255))

        self.max_size = size
        self.search_icon = None
        self.image_ctrl = None
        self.text_box = None

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        self.create()

    def create(self):
        image = wx.Image(MAGNIFYING_GLASS_ICON, type=wx.BITMAP_TYPE_ANY)
        image = image.Scale(image.GetSize().x*0.95, image.GetSize().y*0.95)
        self.image_ctrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Image.ConvertToBitmap(image))
        self.image_ctrl.SetBackgroundColour(wx.Colour(100, 100, 100, 255))

        self.text_box = wx.TextCtrl(self, value="Search...")
        self.text_box.SetWindowStyleFlag(wx.BORDER_NONE)
        self.text_box.SetBackgroundColour(wx.Colour(100, 100, 100, 255))
        self.text_box.SetForegroundColour(wx.Colour(255, 255, 255, 255))

        cursor = wx.Cursor(wx.Image(TextBox_Cursor, type=wx.BITMAP_TYPE_ANY))
        self.text_box.SetCursor(cursor)

        font = wx.Font(8, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)
        self.text_box.SetFont(font)

        self.sizer.Add(self.image_ctrl, 0, wx.EXPAND | wx.LEFT, border=2)
        self.sizer.Add(self.text_box, 1, wx.EXPAND)
        self.sizer.Layout()
