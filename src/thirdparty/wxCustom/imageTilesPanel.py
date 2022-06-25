import math
import wx
import editor.constants as constants
import editor.uiGlobals as uiGlobals
import editor.wxUI.globals as wxGlobals
import editor.commands as commands
from editor.utils import PathUtils
from wx.lib.scrolledpanel import ScrolledPanel


# event ids for different event types
EVT_RENAME_ITEM = wx.NewId()
EVT_DUPLICATE_ITEM = wx.NewId()
EVT_REMOVE_ITEM = wx.NewId()
EVT_LOAD_MODEL = wx.NewId()
EVT_LOAD_ACTOR = wx.NewId()


def create_generic_menu_items(parent_menu):
    menu_items = [(EVT_RENAME_ITEM, "&Rename", None),
                  (EVT_REMOVE_ITEM, "&Remove", None),
                  (EVT_DUPLICATE_ITEM, "&Duplicate", None)]
    wxGlobals.build_menu(parent_menu, menu_items)


def create_3d_model_menu_items(parent_menu):
    menu_items = [(EVT_LOAD_MODEL, "&Load Model", None),
                  (EVT_LOAD_ACTOR, "&Load As Actor", None)]
    wxGlobals.build_menu(parent_menu, menu_items)


class ImageTile(wx.Panel):
    def __init__(self, parent, label, extension, style, color, size, position, tile_index=-1, data=None):

        wx.Panel.__init__(self, parent)

        self.SetWindowStyleFlag(style)
        self.SetBackgroundColour(color)
        self.SetSize(size)
        self.SetPosition(position)

        self.parent = parent
        self.label = label
        self.tile_index = tile_index

        self.is_selected = False
        self.image_path = None
        self.image = None
        self.image_control = None
        self.max_image_size = -1  # TODO remove this
        self.data = data
        self.label = label
        self.extension = extension

        self.image_ctrl = wx.StaticBitmap(self)

        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

        self.text_ctrl = wx.StaticText(self,
                                       label=self.label,
                                       style=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL)
        self.text_ctrl.SetFont(font)
        # self.text_ctrl.SetForegroundColour(uiGlobals.ColorPalette.EDITOR_TEXT_COLOR)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.Layout()

        self.event_map = {
            EVT_RENAME_ITEM: (self.rename_item, "rename_item"),
            EVT_DUPLICATE_ITEM: (self.duplicate_item, "duplicate"),
            EVT_REMOVE_ITEM: (self.delete_item, "remove_item"),

            EVT_LOAD_MODEL: (self.load_model, None),
            EVT_LOAD_ACTOR: (self.load_actor, None),
        }

        self.image_ctrl.Bind(wx.EVT_LEFT_DOWN, self.on_select)
        self.image_ctrl.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.Bind(wx.EVT_MENU, self.on_select_context)

    def set_active(self, value):
        self.is_selected = value

    def set_image(self, path, fixed=False):
        self.image_path = path

        if self.image_path is None:
            return

        self.image = wx.Image(self.image_path, type=wx.BITMAP_TYPE_ANY)
        self.update()

    def update(self):
        self.image_ctrl.SetSize((self.GetSize().x-10, self.GetSize().y-10))
        self.image_ctrl.SetBackgroundColour(uiGlobals.ColorPalette.DARK_GREY)
        self.image_ctrl.SetPosition((self.GetSize().x/12, 0))

        size_y = self.GetSize().y - self.image_ctrl.GetSize().y + 3
        self.text_ctrl.SetSize((self.GetSize().x, size_y))
        self.text_ctrl.SetPosition((0, self.GetSize().y - self.text_ctrl.GetSize().y))

        if self.image is None:
            return
        else:
            self.image.Clear()

        self.image = wx.Image(self.image_path, type=wx.BITMAP_TYPE_ANY)
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

        new_height /= 1.2
        new_width /= 1.2

        if new_height < 1:
            new_height = 1
        if new_width < 1:
            new_width = 1

        self.image = self.image.Scale(new_width, new_height)
        self.image_ctrl.SetBitmap(wx.Bitmap(self.image))

    def on_select(self, evt):
        if ImageTilesPanel.SELECTED_TILE:
            ImageTilesPanel.SELECTED_TILE.on_deselect()

        ImageTilesPanel.SELECTED_TILE = self

        self.is_selected = True
        # self.SetBackgroundColour(uiGlobals.ColorPalette.SKY_BLUE)
        self.text_ctrl.SetBackgroundColour(uiGlobals.ColorPalette.SKY_BLUE)
        self.Refresh()

        constants.obs.trigger("ResourceTileSelected", self.label)
        evt.Skip()

    def on_deselect(self):
        self.is_selected = False
        # self.SetBackgroundColour(uiGlobals.ColorPalette.DARK_GREY)
        self.text_ctrl.SetBackgroundColour(uiGlobals.ColorPalette.DARK_GREY)
        self.Refresh()

    def on_right_down(self, evt):
        if not self.is_selected:
            evt.Skip()
            return
        else:
            popup_menu = wx.Menu()

            if self.extension in constants.MODEL_EXTENSIONS:
                create_3d_model_menu_items(popup_menu)
                popup_menu.AppendSeparator()
            create_generic_menu_items(popup_menu)

            self.PopupMenu(popup_menu, self.image_ctrl.GetPosition())
            popup_menu.Destroy()

            evt.Skip()

    def on_select_context(self, evt):
        if evt.GetId() in self.event_map.keys():
            foo = self.event_map[evt.GetId()][0]
            foo()

        evt.Skip()

    def rename_item(self):
        def on_ok(new_label):
            if new_label != self.label:
                PathUtils.rename(self.data, new_label, self.extension)

        dm = constants.p3d_app.wx_main.dialogue_manager
        dm.create_dialog("TextEntryDialog",
                         "Rename Item",
                         dm,
                         descriptor_text="Rename Selection",
                         ok_call=on_ok,
                         initial_text=self.label)

    def duplicate_item(self):
        pass

    def delete_item(self):
        def on_ok():
            PathUtils.delete(self.data)

        dm = constants.p3d_app.wx_main.dialogue_manager
        dm.create_dialog("YesNoDialog",
                         "Delete Item",
                         dm,
                         descriptor_text="Confirm remove selection(s) ?",
                         ok_call=on_ok)

    def load_model(self):
        path = self.data
        constants.command_manager.do(commands.LoadModel(constants.p3d_app, path=path, is_actor=False))

    def load_actor(self):
        path = self.data
        constants.command_manager.do(commands.LoadModel(constants.p3d_app, path=path, is_actor=True))


class ImageTilesPanel(ScrolledPanel):
    """class representing a single image tile"""

    SELECTED_TILE = None
    TILES_PER_ROW = 5
    TILE_POS_OFFSET = 12
    TILE_SIZE = 64

    def __init__(self, parent, resource_tree=None):
        ScrolledPanel.__init__(self, parent)
        self.SetBackgroundColour(uiGlobals.ColorPalette.DARK_GREY)

        self.resource_tree = resource_tree
        self.parent = parent
        self.image_tiles = []

        self.Bind(wx.EVT_SIZE, self.on_evt_resize)

    def update_tiles(self):
        if self.GetSize().x <= 1:
            return

        num_tiles = len(self.image_tiles)  #
        tiles_per_row = math.floor(self.GetSize().x / self.TILE_SIZE)  # num tiles per row

        if tiles_per_row <= 1:
            return

        num_rows = math.ceil(num_tiles / tiles_per_row)

        tile_index = 0
        for i in range(num_rows):
            for j in range(tiles_per_row):

                try:
                    tile = self.image_tiles[tile_index]
                except IndexError:
                    break

                tile.SetSize((self.TILE_SIZE, self.TILE_SIZE))

                tile_pos_x = (self.TILE_SIZE * (j * 1.1)) + self.TILE_POS_OFFSET / 1
                tile_pos_y = (self.TILE_SIZE * (i * 1.1)) + self.TILE_POS_OFFSET / 1
                tile.SetPosition((tile_pos_x, tile_pos_y))
                tile.update()
                tile_index += 1

    def add_tile(self, image, label, extension, data):
        tile = ImageTile(parent=self,
                         label=label,
                         extension=extension,
                         style=wx.BORDER_NONE,
                         color=uiGlobals.ColorPalette.DARK_GREY,
                         size=(10, 10),
                         position=(0, 0),
                         data=data)

        self.image_tiles.append(tile)
        tile.set_image(image)

    def remove_all_tiles(self):
        for tile in self.image_tiles:
            tile.Destroy()
        self.image_tiles = []
        ImageTilesPanel.SELECTED_TILE = None
        self.update_tiles()

    def get_selected_tile(self, name=False):
        if self.SELECTED_TILE is not None:
            if name:
                return ImageTilesPanel.SELECTED_TILE.image_path
            else:
                return ImageTilesPanel.SELECTED_TILE

    def on_evt_resize(self, evt):
        self.update_tiles()
        evt.Skip()
