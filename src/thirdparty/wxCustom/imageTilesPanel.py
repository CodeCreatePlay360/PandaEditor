import os
import math
import wx
import editor.constants as constants
import editor.edPreferences as edPreferences
import editor.wxUI.globals as wxGlobals
import editor.commands as commands

from editor.utils import PathUtils
from wx.lib.scrolledpanel import ScrolledPanel
from editor.wxUI.custom import ControlGroup, SelectionButton
from editor.wxUI.custom import SearchBox
from editor.globals import editor


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

        self.sizer.Add(self.image_ctrl, 1, wx.EXPAND)
        self.sizer.Add(self.text_ctrl, 0, wx.EXPAND)

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
        if self.image is None:
            return
        else:
            self.image.Clear()

        self.image = wx.Image(self.image_path, type=wx.BITMAP_TYPE_ANY)
        width = self.image.GetWidth()
        height = self.image.GetHeight()

        if width > height:
            self.max_image_size = 40
        else:
            self.max_image_size = 40

        if width > height:
            new_width = self.max_image_size
            new_height = self.max_image_size * (height / width)
        else:
            new_height = self.max_image_size
            new_width = self.max_image_size * (width / height)

        if new_height < 1:
            new_height = 1
        if new_width < 1:
            new_width = 1

        self.image = self.image.Scale(new_width, new_height)
        self.image_ctrl.SetBitmap(wx.Bitmap(self.image))

    def on_select(self, evt=None):
        self.parent.deselect_all()
        self.parent.select_tiles([self], False)
        # self.parent.options.set_item_info_text(self.data)

        self.is_selected = True
        self.text_ctrl.SetBackgroundColour(edPreferences.Colors.Image_Tile_Selected)
        self.Refresh()

        editor.observer.trigger("OnResourceTileSelected", self.data)

        if evt:
            evt.Skip()

    def on_deselect(self):
        self.is_selected = False
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
        def rename(new_label):
            if new_label != self.label:
                PathUtils.rename(self.data, new_label, self.extension)

        dial = wx.TextEntryDialog(None, "Rename resource item", "Rename", self.label)
        if dial.ShowModal():
            rename(dial.GetValue())

    def duplicate_item(self):
        pass

    def delete_item(self):
        def remove():
            PathUtils.delete(self.data)

        dial = wx.MessageDialog(None, "Confirm remove item ?", "Remove item",
                                style=wx.YES_NO | wx.ICON_QUESTION).ShowModal()
        if dial == wx.ID_YES:
            remove()

    def load_model(self):
        path = self.data
        editor.command_mgr.do(commands.LoadModel(editor.p3d_app, path=path, is_actor=False))

    def load_actor(self):
        path = self.data
        editor.command_mgr.do(commands.LoadModel(editor.p3d_app, path=path, is_actor=True))


class ImageTilesPanel(ScrolledPanel):
    class State:
        def __init__(self, selected_tiles: list):
            """Class representing state of ImageTilesPanel"""
            self.selected_tiles = selected_tiles

    class Options(wx.Window):
        """Class containing various settings and options for image_tiles_panel"""

        def __init__(self, parent, *args, **kwargs):
            wx.Window.__init__(self, parent, *args, **kwargs)
            self.SetBackgroundColour(edPreferences.Colors.Panel_Dark)
            self.parent = parent

            self.v_sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.SetSizer(self.v_sizer)

            self.search_control = SearchBox(self)

            # create filter selection buttons
            self.filter_buttons_grid = ControlGroup(self)

            inspector_panel_btn = SelectionButton(self.filter_buttons_grid, 0, "Models", image_path=Model_icon)
            world_settings_btn = SelectionButton(self.filter_buttons_grid, 1, "Textures",
                                                 text_pos=(21, 2),
                                                 image_path=Texture_icon,
                                                 image_pos=(3, 2),
                                                 image_scale=13)
            ed_settings_btn = SelectionButton(self.filter_buttons_grid, 2, "Sounds", image_path=Sound_icon)
            plugins_panel_btn = SelectionButton(self.filter_buttons_grid, 3, "Scripts", image_path=Script_icon)

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
            sizer.Add(self.item_info_ctrl, 1, wx.EXPAND | wx.TOP|wx.LEFT, border=2)
            # -------------------------------------------------------------

            self.sizer.Add(self.search_control, 1, wx.EXPAND | wx.LEFT, border=1)
            self.sizer.Add(self.filter_buttons_grid, 1, wx.EXPAND | wx.LEFT, border=1)
            self.v_sizer.Add(self.sizer, 1, wx.EXPAND)
            self.v_sizer.Add(self.panel, 1, wx.EXPAND | wx.TOP, border=1)

        def on_filter_btn_pressed(self, btn_index):
            pass

        def set_item_info_text(self, txt: str):
            self.item_info_ctrl.SetLabel(txt)

    TILES_PER_ROW = 5
    Tile_offset_x = 12
    Tile_offset_y = 42
    TILE_SIZE = 64

    def __init__(self, parent, resource_tree=None):
        ScrolledPanel.__init__(self, parent)
        self.SetBackgroundColour(edPreferences.Colors.Panel_Dark)

        self.options = self.Options(parent)
        self.options.SetMaxSize((-1, 36))

        self.resource_tree = resource_tree
        self.parent = parent
        self.__tiles = []
        self.__selected_tiles = []
        self.__saved_state = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.gridSizer = None
        self.SetSizer(self.sizer)

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

    def on_evt_resize(self, evt):
        if self.gridSizer:
            self.gridSizer.Clear()
        self.update_tiles()
        evt.Skip()

    def create_tile(self, image, label, extension, data):
        tile = ImageTile(parent=self,
                         label=label,
                         extension=extension,
                         style=wx.BORDER_NONE,
                         color=edPreferences.Colors.Panel_Dark,
                         size=(10, 10),
                         position=(0, 0),
                         data=data)

        self.__tiles.append(tile)
        tile.set_image(image)
        tile.Hide()

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
                    image = self.icon_and_extension["generic"]
                    selections_organized["generic"].append((image, file_name, extension, file_path))

        for item in selections_organized.keys():
            value = selections_organized[item]
            for _item in value:
                self.create_tile(_item[0], _item[1], _item[2], _item[3])

        self.update_tiles()

    def select_tiles(self, tiles, select=True):
        if len(tiles) > 0:

            self.deselect_all()

            for i in range(len(tiles)):
                if tiles[i] in self.__tiles:
                    if select:
                        tiles[i].on_select()
                    self.__selected_tiles.append(tiles[i])

            self.options.set_item_info_text(tiles[0].data)

    def select_tiles_from_paths(self, paths, select=True):
        if len(paths) > 0:

            self.deselect_all()

            for i in range(len(paths)):
                if not os.path.exists(paths[i]):
                    continue
                tile = self.get_tile_from_path(paths[i])
                if tile and tile in self.__tiles:
                    if select:
                        tile.on_select()
                    self.__selected_tiles.append(tile)

                self.options.set_item_info_text(tile.data)

    def deselect_all(self):
        for tile in self.__tiles:
            tile.on_deselect()
        self.options.set_item_info_text("No item selected.")
        self.__selected_tiles.clear()

    def update_tiles(self):
        if self.GetSize().x <= 1:
            return

        num_tiles = len(self.__tiles)
        if num_tiles == 0:
            return

        tiles_per_row = math.floor(self.GetSize().x / self.TILE_SIZE)  # num tiles per row
        if tiles_per_row == 0:
            return
        num_rows = math.ceil(num_tiles / tiles_per_row)

        self.gridSizer = wx.GridSizer(num_rows, tiles_per_row, 1, 0)
        self.sizer.Add(self.gridSizer, 1, wx.EXPAND)

        tile_index = 0
        for i in range(num_rows):
            for j in range(tiles_per_row):

                try:
                    tile = self.__tiles[tile_index]
                except IndexError:
                    break

                tile.SetMinSize((self.TILE_SIZE, self.TILE_SIZE))
                tile.update()
                tile_index += 1

                self.gridSizer.Add(tile, 0)
                tile.Show()

        self.gridSizer.Layout()
        self.sizer.Layout()
        self.SetupScrolling(scroll_x=True)

    def remove_all_tiles(self):
        for tile in self.__tiles:
            tile.Destroy()
        self.__tiles = []
        self.__selected_tiles.clear()
        if self.gridSizer:
            self.gridSizer.Clear()
        self.update_tiles()

    def get_selected_tiles(self, paths=False):
        selected = []
        if len(self.__selected_tiles) > 0:
            if paths:
                for tile in self.__selected_tiles:
                    selected.append(tile.data)
            else:
                for tile in self.__selected_tiles:
                    selected.append(tile)
        return selected

    def get_tiles(self, paths=False):
        tiles = []
        for i in range(len(self.__tiles)):
            if paths:
                tiles.append(self.__tiles[i].data)
            else:
                tiles.append(self.__tiles[i].data)
        return tiles

    def get_tile_from_path(self, path):
        for i in range(len(self.__tiles)):
            if self.__tiles[i].data == path:
                return self.__tiles[i]
        return None
