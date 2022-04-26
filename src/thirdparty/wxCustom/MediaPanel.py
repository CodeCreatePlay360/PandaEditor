import wx
from wxCustom.wxCustomPanel import WxScrolledPanel, WxPanel
from constants import *


def get_best_size():
    pass


def image_tile_selected(tile):
    obs.trigger("image tile selected", tile.image)
    if ImageTilesPanel.SELECTED_TILE is not None:
        ImageTilesPanel.SELECTED_TILE.on_deselect()
    ImageTilesPanel.SELECTED_TILE = tile


class MediaViewerPanel(WxPanel):
    SELF = None

    def __init__(self, parent, label, style, color):
        WxPanel.__init__(self, parent, label, style, color)
        self.image = None
        self.image_ctrl = None
        self.max_size = -1
        MediaViewerPanel.SELF = self
        self.Bind(wx.EVT_SIZE, self.on_evt_resize)

    def finish_init(self):
        self.create_layout()
        self.base_panel.SetSize(self.GetClientSize())
        self.image_ctrl = wx.StaticBitmap(self.base_panel)
        self.base_panel_sizer.Add(self.image_ctrl, 1, wx.EXPAND)

    @staticmethod
    @obs.on("image tile selected")
    def set_image_(image):
        MediaViewerPanel.SELF.image = image
        MediaViewerPanel.SELF.update_image()

    def clear_media(self):
        self.image = None
        if self.image_ctrl is not None:
            self.image_ctrl.Destroy()
            self.image_ctrl = wx.StaticBitmap(self.base_panel)
        self.Layout()

    def update_image(self):
        if self.image is None:
            return

        self.base_panel.SetSize(self.GetClientSize())
        """ Update the currently shown photo """
        image = wx.Image(self.image, type=wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        width = image.GetWidth()
        height = image.GetHeight()

        if width > height:
            self.max_size = self.base_panel.GetClientSize().x
        else:
            self.max_size = self.base_panel.GetClientSize().y

        if width > height:
            new_width = self.max_size
            new_height = self.max_size * (height / width)
        else:
            new_height = self.max_size
            new_width = self.max_size * (width / height)
        image = image.Scale(new_width, new_height)
        self.image_ctrl.SetBitmap(wx.Bitmap(image))

        self.Layout()

    def on_evt_resize(self, evt):
        super().on_evt_resize(evt)
        try:
            self.update_image()
        except AttributeError as e:
            print("error occurred, details:", e)
        evt.Skip()


class ImageTile(wx.Panel):
    def __init__(self, parent, label, style, color, size, position, tile_index=-1, func=None, func_args=None,
                 deselect_func=None, deselect_func_args=None):

        wx.Panel.__init__(self, parent)
        self.SetWindowStyleFlag(style)
        self.SetBackgroundColour(color)
        self.SetSize(size)
        self.SetPosition(position)

        self.parent = parent
        self.label = label
        self.tile_index = tile_index
        self.function = func
        self.func_args = func_args
        self.deselect_func = deselect_func
        self.deselect_func_args = deselect_func_args

        self.is_selected = False
        self.image = None
        self.image_control = None
        self.max_image_size = -1

        self.image_ctrl = wx.StaticBitmap(self)
        self.image_ctrl.SetSize(self.GetClientSize())

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.Layout()

        self.image_ctrl.Bind(wx.EVT_LEFT_DOWN, self.on_select)
        self.Bind(wx.EVT_SIZE, self.on_event_size)

    def get_active(self):
        return self.is_selected

    def get_image(self):
        return self.image

    def set_active(self, value):
        self.is_selected = value

    def set_image(self, path, fixed=False):
        self.image = path

        if self.image is None:
            return

        if fixed:
            pass

        """ Update the currently shown photo """
        image = wx.Image(self.image, type=wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        width = image.GetWidth()
        height = image.GetHeight()

        if width > height:
            self.max_image_size = self.image_ctrl.GetSize().x
        else:
            self.max_image_size = self.image_ctrl.GetSize().y

        if width > height:
            new_width = self.max_image_size
            new_height = self.max_image_size * (height / width)
        else:
            new_height = self.max_image_size
            new_width = self.max_image_size * (width / height)
        image = image.Scale(new_width, new_height)
        self.image_ctrl.SetBitmap(wx.Bitmap(image))
        self.update()

    def update(self):
        self.image_ctrl.SetSize((self.GetSize().x - 5, self.GetSize().y - 5))
        self.image_ctrl.SetBackgroundColour(GREY)
        self.image_ctrl.SetPosition((2.5, 2.5))
        self.max_image_size = self.image_ctrl.GetSize().y

    def on_select(self, evt):
        if self.function is not None:
            if self.func_args is None:
                self.function(self)
            else:
                self.function(self.func_args)

        self.is_selected = True
        self.SetBackgroundColour(GREY)
        self.Refresh()
        evt.Skip()

    def on_deselect(self):
        if self.deselect_func is not None:
            if self.deselect_func_args is None:
                self.deselect_func(self)
            else:
                self.deselect_func(self.deselect_func_args)

        self.is_selected = False
        self.SetBackgroundColour(DARK_GREY)
        self.Refresh()

    def on_event_size(self, evt):
        self.update()
        evt.Skip()


class ImageTilesPanel(WxScrolledPanel):
    """class representing a single image tile"""
    SELECTED_TILE = None

    def __init__(self, parent, label, style, color):
        WxScrolledPanel.__init__(self, parent, label, style, color)
        self.parent = parent
        self.image_tiles = []
        self.next_empty_tile_index = 0
        self.selected_tile = None

        object_manager.add_object("ImageTilesPanel", self)

    def finish_init(self):
        self.create_layout()
        self.base_panel.SetSize(self.GetClientSize())
        self.update_tiles()

    tiles_per_row = 5
    tile_pos_offset = 4

    def update_tiles(self, start=0, stop=0, num_row=0):
        stop += self.tiles_per_row
        tile_size = (self.GetSize().x / self.tiles_per_row)

        list_index = 0
        for i in range(start, stop):
            if i > len(self.image_tiles) - 1:
                return

            tile = self.image_tiles[i]
            tile.SetSize((tile_size - self.tile_pos_offset, tile_size - self.tile_pos_offset))
            tile.update()
            tile.SetPosition(((tile_size * list_index) + self.tile_pos_offset / 2.1,
                              (tile_size * num_row) + self.tile_pos_offset / 2.1))
            list_index += 1

        num_row += 1
        self.update_tiles(stop, stop, num_row)
        self.base_panel.Layout()
        self.Layout()
        self.Refresh()

    def add_image(self, path):
        tile = ImageTile(
            parent=self.base_panel,
            label="",
            style=wx.BORDER_NONE,
            color=DARK_GREY,
            size=(0, 0),
            position=(0, 0),
            tile_index=-1,
            func=image_tile_selected,
        )

        self.image_tiles.append(tile)
        self.update_tiles()
        tile.set_image(path)

    def remove_all_images(self):
        for tile in self.image_tiles:
            tile.Destroy()
        self.image_tiles = []
        ImageTilesPanel.SELECTED_TILE = None

    def get_selected_tile(self, name=False):
        if self.SELECTED_TILE is not None:
            if name:
                return ImageTilesPanel.SELECTED_TILE.image
            else:
                return ImageTilesPanel.SELECTED_TILE

    def on_evt_resize(self, evt):
        super().on_evt_resize(evt)
        self.update_tiles()
        evt.Skip()


class MultimediaPanel(wx.Panel):
    SELF = None

    def __init__(self, parent, label, style, color):
        wx.Panel.__init__(self, parent)
        MultimediaPanel.SELF = self
        self.label = label
        self.style = style
        self.color = color

        object_manager.add_object("MultimediaPanel", self)

        self.SetBackgroundColour(GREY)
        self.SetWindowStyle(wx.BORDER_SUNKEN)

        self.splitterWindow = wx.SplitterWindow(self)
        self.splitterWindow.SetWindowStyle(wx.SP_THIN_SASH | wx.SP_LIVE_UPDATE)

        self.media_viewer_panel = None
        self.image_tiles_panel = None
        self.finish_init()

        self.Bind(wx.EVT_SIZE, self.on_evt_size)

    def finish_init(self):
        self.splitterWindow.SetSize(self.GetClientSize())

        self.media_viewer_panel = MediaViewerPanel(self.splitterWindow, "MediaViewerPanel", self.style, self.color)
        self.image_tiles_panel = ImageTilesPanel(self.splitterWindow, "ImageTilesPanel", self.style, self.color)

        self.splitterWindow.SplitVertically(self.image_tiles_panel, self.media_viewer_panel, 180)

        self.image_tiles_panel.SetSize(self.splitterWindow.GetWindow1().GetClientSize())
        self.image_tiles_panel.finish_init()

        self.media_viewer_panel.SetSize(self.splitterWindow.GetWindow2().GetClientSize())
        self.media_viewer_panel.finish_init()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.splitterWindow, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        # self.test()

    def test(self):
        self.image_tiles_panel.add_image("C:/Users/Obaid ur Rehman/Desktop/Girls/1604332241_Dtqa6h1yePI.jpg")

    def on_evt_size(self, evt):
        evt.Skip()

    def update_image_tiles(self, **kwargs):
        self.image_tiles_panel.remove_all_images()
        for image in kwargs.pop("item_images"):
            self.image_tiles_panel.add_image(image)
