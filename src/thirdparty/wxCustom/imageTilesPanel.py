import wx
from wx.lib.scrolledpanel import ScrolledPanel

DARK_GREY = wx.Colour(127, 127, 127, 255)
YELLOW = wx.YELLOW
GRAY = wx.Colour(167, 167, 167, 255)


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
        self.image_path = None
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
        return self.image_path

    def set_active(self, value):
        self.is_selected = value

    def set_image(self, path, fixed=False):
        self.image_path = path

        if self.image_path is None:
            return

        if fixed:
            pass

        """ Update the currently shown photo """
        self.image = wx.Image(self.image_path, type=wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        width = self.image.GetWidth()
        height = self.image.GetHeight()

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

        self.image = self.image.Scale(new_width, new_height)

        self.image_ctrl.SetBitmap(wx.Bitmap(self.image))
        self.update()

    def update(self):
        self.image_ctrl.SetSize((self.GetSize().x - 5, self.GetSize().y - 5))
        self.image_ctrl.SetBackgroundColour(GRAY)
        self.image_ctrl.SetPosition((2.5, 2.5))

        # scale the image, preserving the aspect ratio

        if self.image is None:
            return
        self.image.Clear()
        width = self.image.GetWidth()
        height = self.image.GetHeight()

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

        self.image = self.image.Scale(new_width, new_height)
        self.image_ctrl.SetBitmap(wx.Bitmap(self.image))

    def on_select(self, evt):
        if self.function is not None:
            if self.func_args is None:
                self.function(self)
            else:
                self.function(self.func_args)

        self.is_selected = True
        self.SetBackgroundColour(YELLOW)
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


class ImageTilesPanel(ScrolledPanel):
    """class representing a single image tile"""
    SELECTED_TILE = None

    def __init__(self, parent, label, style, color):
        ScrolledPanel.__init__(self, parent)
        self.parent = parent
        self.image_tiles = []
        self.next_empty_tile_index = 0
        self.selected_tile = None

        self.Bind(wx.EVT_SIZE, self.on_evt_resize)

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
        self.Layout()
        self.Refresh()

    def add_image(self, path):
        tile = ImageTile(
            parent=self,
            label="",
            style=wx.BORDER_NONE,
            color=DARK_GREY,
            size=(10, 10),
            position=(0, 0),
            tile_index=-1,
            func=None,
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
                return ImageTilesPanel.SELECTED_TILE.image_path
            else:
                return ImageTilesPanel.SELECTED_TILE

    def on_evt_resize(self, evt):
        self.update_tiles()
        evt.Skip()
