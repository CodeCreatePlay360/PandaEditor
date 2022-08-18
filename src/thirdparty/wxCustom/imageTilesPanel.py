import os
import math
import wx
import editor.constants as constants
import editor.edPreferences as edPreferences
import editor.wxUI.globals as wxGlobals
import editor.commands as commands
from editor.utils import PathUtils
from wx.lib.scrolledpanel import ScrolledPanel
from editor.wxUI.baseInspectorPanel import SelectionGrid, SelectionButton


# event ids for different event types
EVT_RENAME_ITEM = wx.NewId()
EVT_DUPLICATE_ITEM = wx.NewId()
EVT_REMOVE_ITEM = wx.NewId()
EVT_LOAD_MODEL = wx.NewId()
EVT_LOAD_ACTOR = wx.NewId()

# icons for selection grid
Model_icon = constants.ICONS_PATH + "//" + "3D-objects-icon.png"
Texture_icon = constants.ICONS_PATH + "//" + "images.png"
Sound_icon = constants.ICONS_PATH + "//" + "music.png"
Script_icon = constants.ICONS_PATH + "//" + "script_code.png"
Video_icon = constants.ICONS_PATH + "//" + "video.png"

# file extension icons for tiles
AudioFile_icon = constants.ICONS_PATH + "//" + "ResourceTiles" + "//" + "audio.png"
VideoFile_icon = constants.ICONS_PATH + "//" + "ResourceTiles" + "//" + "video.png"
ImageFile_icon = constants.ICONS_PATH + "//" + "ResourceTiles" + "//" + "image.png"
TextFile_icon = constants.ICONS_PATH + "//" + "ResourceTiles" + "//" + "text.png"
UserModule_icon = constants.ICONS_PATH + "//" + "ResourceTiles" + "//" + "userModule.png"
EditorPlugin_icon = constants.ICONS_PATH + "//" + "ResourceTiles" + "//" + "plugin.png"
UnknownFile_icon = constants.ICONS_PATH + "//" + "ResourceTiles" + "//" + "file.png"
ModelFile_icon = constants.ICONS_PATH + "//" + "ResourceTiles" + "//" + "3dModel.png"


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
    """class representing a single image tile, with a text field below image"""

    def __init__(self, parent, label, extension, style, color, size, position, tile_index=-1, data=None):
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.label = label
        self.tile_index = tile_index

        self.SetWindowStyleFlag(style)
        self.SetBackgroundColour(color)
        self.SetSize(size)
        self.SetPosition(position)

        self.is_selected = False
        self.image_path = None
        self.image = None
        self.image_control = None
        self.data = data
        self.label = label
        self.extension = extension

        self.image_ctrl = wx.StaticBitmap(self)

        font = wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)

        self.text_ctrl = wx.StaticText(self,
                                       label=self.label,
                                       style=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL)
        self.text_ctrl.SetFont(font)

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

    def set_image(self, path):
        self.image_path = path

        if self.image_path is None:
            return

        self.image = wx.Image(self.image_path, type=wx.BITMAP_TYPE_ANY)
        self.update()

    def update(self):
        self.image_ctrl.SetSize((self.GetSize().x - 10, self.GetSize().y - 10))
        self.image_ctrl.SetPosition((self.GetSize().x / 12, 0))

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

    def on_select(self, evt=None):
        if self.parent.SELECTED_TILE:
            self.parent.SELECTED_TILE.on_deselect()

        self.parent.SELECTED_TILE = self
        self.parent.options.set_item_info_text(self.data)

        self.is_selected = True
        self.text_ctrl.SetBackgroundColour(edPreferences.Colors.Image_Tile_Selected)
        self.Refresh()

        constants.obs.trigger("OnResourceTileSelected", self.label)

        if evt:
            evt.Skip()

    def on_deselect(self):
        self.is_selected = False
        self.parent.SELECTED_TILE = None
        self.text_ctrl.SetBackgroundColour(edPreferences.Colors.Image_Tile_BG)
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
    class State:
        def __init__(self, selected_tile_index):
            """Class representing state of ImageTilesPanel"""
            self.selected_tile_index = selected_tile_index

    class Options(wx.Window):
        """Class containing various settings and options for image_tiles_panel"""

        def __init__(self, parent, *args, **kwargs):
            wx.Window.__init__(self, parent, *args, **kwargs)
            self.SetBackgroundColour(edPreferences.Colors.Panel_Dark)
            self.parent = parent

            self.v_sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.SetSizer(self.v_sizer)

            # create a search control
            font = wx.Font(8, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)
            bmp_1 = wx.Bitmap(constants.MAGNIFYING_GLASS_ICON, wx.BITMAP_TYPE_ANY)
            bmp_2 = wx.Bitmap(constants.SEARCH_CANCEL_ICON, wx.BITMAP_TYPE_ANY)

            self.search_control = wx.SearchCtrl(self)
            self.search_control.SetWindowStyleFlag(wx.BORDER_NONE)
            self.search_control.SetBackgroundColour(edPreferences.Colors.Panel_Normal)
            self.search_control.SetForegroundColour(wx.Colour(225, 225, 225, 255))
            self.search_control.SetFont(font)
            self.search_control.SetSearchBitmap(bmp_1)
            self.search_control.SetCancelBitmap(bmp_2)

            # create filter selection buttons
            self.filter_buttons_grid = SelectionGrid(self, self.on_filter_btn_pressed)

            inspector_panel_btn = SelectionButton(self.filter_buttons_grid, 0, Model_icon, "Models")
            world_settings_btn = SelectionButton(self.filter_buttons_grid, 1, Texture_icon, "Textures",
                                                 image_scale=13, image_pos=(3, 2), text_pos=(21, 2))
            ed_settings_btn = SelectionButton(self.filter_buttons_grid, 2, Sound_icon, "Sounds")
            plugins_panel_btn = SelectionButton(self.filter_buttons_grid, 3, Script_icon, "Scripts")

            self.filter_buttons_grid.add_button(inspector_panel_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
            self.filter_buttons_grid.add_button(world_settings_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
            self.filter_buttons_grid.add_button(ed_settings_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
            self.filter_buttons_grid.add_button(plugins_panel_btn, flags=wx.EXPAND)

            self.filter_buttons_grid.select_button(0)

            # static text panel to display selected item path info
            self.panel = wx.Panel(self)
            self.panel.SetBackgroundColour(edPreferences.Colors.Panel_Normal)
            #
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.panel.SetSizer(sizer)
            #
            self.item_info_ctrl = wx.StaticText(self.panel, label="")
            self.item_info_ctrl.SetForegroundColour(edPreferences.Colors.Panel_Light)
            font = wx.Font(8, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.FONTWEIGHT_BOLD)
            self.item_info_ctrl.SetFont(font)
            sizer.Add(self.item_info_ctrl, 1, wx.EXPAND | wx.TOP, border=1)

            self.sizer.Add(self.search_control, 1, wx.EXPAND, border=0)
            self.sizer.Add(self.filter_buttons_grid, 1, wx.EXPAND | wx.LEFT, border=1)
            self.v_sizer.Add(self.sizer, 1, wx.EXPAND)
            self.v_sizer.Add(self.panel, 1, wx.EXPAND | wx.TOP, border=1)

        def on_filter_btn_pressed(self, btn_index):
            pass

        def set_item_info_text(self, txt: str):
            self.item_info_ctrl.SetLabel(txt)

    SELECTED_TILE = None
    TILES_PER_ROW = 5
    Tile_offset_x = 12
    Tile_offset_y = 42
    TILE_SIZE = 64

    def __init__(self, parent, resource_tree=None):
        ScrolledPanel.__init__(self, parent)
        self.SetBackgroundColour(edPreferences.Colors.Panel_Dark)
        self.SetWindowStyleFlag(wx.BORDER_SUNKEN)
        constants.object_manager.add_object("ResourceTilesPanel", self)

        self.options = self.Options(self)
        self.resource_tree = resource_tree
        self.parent = parent
        self.image_tiles = []
        self.saved_state = None

        self.icon_and_extension = {
            "generic": UnknownFile_icon,

            # model files
            "egg": ModelFile_icon,
            "bam": ModelFile_icon,
            "pz": ModelFile_icon,
            # "fbx":  MODEL_ICON,
            # "obj": Model_icon,
            # "gltf": MODEL_ICON,

            # image files
            "tiff": ImageFile_icon,
            "tga": ImageFile_icon,
            "jpg": ImageFile_icon,
            "png": ImageFile_icon,

            # other
            "py": UserModule_icon,
            "ed_plugin": UserModule_icon,
            "txt": TextFile_icon,

            # audio
            "mp3": AudioFile_icon,
            "wav": AudioFile_icon,

            # video
            ".mp4": VideoFile_icon,
        }

        self.Bind(wx.EVT_SIZE, self.on_evt_resize)

    def add_tile(self, image, label, extension, data):
        tile = ImageTile(parent=self,
                         label=label,
                         extension=extension,
                         style=wx.BORDER_NONE,
                         color=edPreferences.Colors.Panel_Dark,
                         size=(10, 10),
                         position=(0, 0),
                         data=data)

        self.image_tiles.append(tile)
        tile.set_image(image)

    def set_from_selections(self, selections):
        self.remove_all_tiles()

        selections_organized = {}
        for key in self.icon_and_extension:
            selections_organized[key] = []
        selections_organized["generic"] = []  # add one generic for not supported extensions.

        for _dir, path in selections:
            dir_items = os.listdir(path)
            for item in dir_items:

                if os.path.isdir(path + "/" + item):
                    continue

                split = item.split(".")
                extension = split[-1]
                file_name = split[0]
                file_path = path + "/" + item

                if extension in self.icon_and_extension:
                    image = self.icon_and_extension[extension]
                    selections_organized[extension].append((image, file_name, extension, file_path))
                else:
                    image = self.icon_and_extension[extension]
                    selections_organized["generic"].append((image, file_name, extension, file_path))

        for item in selections_organized.keys():
            value = selections_organized[item]
            for _item in value:
                self.add_tile(_item[0], _item[1], _item[2], _item[3])

        self.update_tiles()

    def deselect_all(self):
        for tile in self.image_tiles:
            tile.on_deselect()
        self.options.set_item_info_text("No item selected.")
        self.SELECTED_TILE = None

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

                tile_pos_x = (self.TILE_SIZE * j * 1.02) + self.Tile_offset_x
                tile_pos_y = (self.TILE_SIZE * i) + self.Tile_offset_y
                tile.SetPosition((tile_pos_x, tile_pos_y))
                tile.update()
                tile_index += 1

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
        self.options.SetSize((self.GetSize().x, 36))
        self.options.SetPosition((0, 0))
        self.update_tiles()
        evt.Skip()

    def save_state(self):
        for i in range(len(self.image_tiles)):
            if self.SELECTED_TILE == self.image_tiles[i]:
                self.saved_state = ImageTilesPanel.State(i)

    def reload_state(self):
        if self.saved_state:
            self.deselect_all()
            for i in range(len(self.image_tiles)):
                if self.saved_state.selected_tile_index == i:
                    self.image_tiles[i].on_select()
                    self.SELECTED_TILE = self.image_tiles[i]
                    break
