import os
import pathlib
import pickle
import math
import wx
import editor.constants as constants
import editor.ui.utils as wxUtils
import editor.commands as commands

from pathlib import Path
from panda3d.core import Filename
from wx.lib.scrolledpanel import ScrolledPanel

from editor.ui.etc.dragDropData import ResourceDragDropData
from editor.ui.custom import SelectionButton
from editor.ui.custom import SearchBox
from editor.globals import editor
from editor.core import RuntimeModule, EditorPlugin, Component
from editor.utils import FileUtils


# event ids for different event types
EVT_RENAME_ITEM = wx.NewId()
EVT_DUPLICATE_ITEM = wx.NewId()
EVT_REMOVE_ITEM = wx.NewId()
EVT_LOAD_MODEL = wx.NewId()
EVT_LOAD_ACTOR = wx.NewId()

# icons for selection grid
Model_icon = str(pathlib.Path(constants.ICONS_PATH + "/3D-objects-icon.png"))
Texture_icon = str(pathlib.Path(constants.ICONS_PATH + "/images.png"))
Sound_icon = str(pathlib.Path(constants.ICONS_PATH + "/music.png"))
Script_icon = str(pathlib.Path(constants.ICONS_PATH + "/script_code.png"))
Video_icon = str(pathlib.Path(constants.ICONS_PATH + "/video.png"))

# file extension icons for tiles
AudioFile_icon = str(pathlib.Path(constants.ICONS_PATH + "/ResourceTiles/audio.png"))
VideoFile_icon = str(pathlib.Path(constants.ICONS_PATH + "/ResourceTiles/video.png"))
ImageFile_icon = str(pathlib.Path(constants.ICONS_PATH + "/ResourceTiles/image.png"))
TextFile_icon = str(pathlib.Path(constants.ICONS_PATH + "/ResourceTiles/text.png"))
UserModule_icon = str(pathlib.Path(constants.ICONS_PATH + "/ResourceTiles/userModule.png"))
EditorPlugin_icon = str(pathlib.Path(constants.ICONS_PATH + "/ResourceTiles/plugin.png"))
UnknownFile_icon = str(pathlib.Path(constants.ICONS_PATH + "/ResourceTiles/file.png"))
ModelFile_icon = str(pathlib.Path(constants.ICONS_PATH + "/ResourceTiles/3dModel.png"))


def create_generic_menu_items(parent_menu):
    menu_items = [(EVT_RENAME_ITEM, "&Rename", None),
                  (EVT_REMOVE_ITEM, "&Remove", None),
                  (EVT_DUPLICATE_ITEM, "&Duplicate", None)]
    wxUtils.build_menu(parent_menu, menu_items)


def create_3d_model_menu_items(parent_menu):
    menu_items = [(EVT_LOAD_MODEL, "&Load Model", None),
                  (EVT_LOAD_ACTOR, "&Load As Actor", None)]
    wxUtils.build_menu(parent_menu, menu_items)


class ImageTile(wx.Panel):
    class TestDropSource(wx.DropSource):
        def __init__(self, win):
            wx.DropSource.__init__(self, win=win)
            self.data = None

        def SetData(self, data):
            wx.DropSource.SetData(self, data)
            self.data = data

        def GiveFeedback(self, effect):
            (window_x, window_y) = wx.GetMousePosition()
            if editor.inspector.components_dnd_panel and \
                    editor.inspector.components_dnd_panel.GetScreenRect().Contains(wx.Point(window_x, window_y)):
                return True

            return False

    def __init__(self, parent, label, extension, style, color, size, position, tile_index=-1, data=None):
        """class representing a single image tile, with a text field below image"""

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
        self.path = data
        self.label = label
        self.extension = extension

        self.image_ctrl = wx.StaticBitmap(self)

        font = wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)
        if len(label) > 12:
            style = wx.ALIGN_CENTRE_VERTICAL
            label = self.label[:10] + "..."  # otherwise, it would overflow
        else:
            style = wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL

        self.text_ctrl = wx.StaticText(self, label=label, style=style)
        self.text_ctrl.SetForegroundColour(wx.Colour(20, 20, 20, 255))
        self.text_ctrl.SetFont(font)

        # sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        # create layout
        self.sizer.Add(self.image_ctrl, 1, wx.EXPAND)
        self.sizer.Add(self.text_ctrl, 0, wx.EXPAND)

        # map events
        self.event_map = {
            EVT_RENAME_ITEM: (self.rename_item, "rename_item"),
            EVT_DUPLICATE_ITEM: (self.duplicate_item, "duplicate"),
            EVT_REMOVE_ITEM: (self.delete_item, "remove_item"),

            EVT_LOAD_MODEL: (self.load_model, None),
            EVT_LOAD_ACTOR: (self.load_actor, None),
        }

        # bind events
        self.image_ctrl.Bind(wx.EVT_LEFT_UP, self.on_select)
        self.image_ctrl.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.Bind(wx.EVT_MENU, self.on_select_context)
        self.image_ctrl.Bind(wx.EVT_MOTION, self.on_begin_drag)

        # tooltip
        tool_tip = wx.ToolTip(self.label)
        self.image_ctrl.SetToolTip(tool_tip)

        #
        self.Layout()

    def on_begin_drag(self, evt):
        if evt.Dragging():
            # create data that is being dragged
            dragged_data = ResourceDragDropData(ResourceDragDropData.PREVIEW_TILES_PANEL)
            dragged_data.set_source([self.path])

            # pickle dragged data
            picked_data = pickle.dumps(dragged_data, 1)

            # create a custom data obj and set its data to dragged data
            custom_data_obj = wx.CustomDataObject(wx.DataFormat('ResourceBrowserData | ImageTileData'))
            custom_data_obj.SetData(picked_data)

            # create a source for drag and drop
            drop_source = ImageTile.TestDropSource(win=self)
            drop_source.SetData(custom_data_obj)

            # Initiate the Drag Operation
            drag_result = drop_source.DoDragDrop()
            if drag_result == wx.DragNone:
                print("Drag failed")
            elif drag_result == wx.DragError:
                print("Drag error")

            editor.wx_main.freeze()
            editor.inspector.layout_auto()
            editor.wx_main.thaw()

            editor.wx_main.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
            evt.Skip()

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

        self.image = self.image.Scale(int(new_width), int(new_height))
        self.image_ctrl.SetBitmap(wx.Bitmap(self.image))

    def on_select(self, evt=None):
        self.parent.deselect_all()
        self.parent.select_tiles([self], False)
        # self.parent.options.set_item_info_text(self.data)

        self.is_selected = True
        self.text_ctrl.SetBackgroundColour(editor.ui_config.color_map("Resource_Image_Tile_Sel"))
        self.Refresh()

        editor.observer.trigger("OnResourceTileSelected", self.path)
        if evt:
            evt.Skip()

    def on_deselect(self):
        self.is_selected = False
        self.text_ctrl.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))
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
                FileUtils.rename(self.path, new_label, self.extension)

        dial = wx.TextEntryDialog(None, "Rename resource item", "Rename", self.label)
        if dial.ShowModal():
            rename(dial.GetValue())

    def duplicate_item(self):
        pass

    def delete_item(self):
        def remove():
            FileUtils.delete(self.path)

        dial = wx.MessageDialog(None, "Confirm remove item ?", "Remove item",
                                style=wx.YES_NO | wx.ICON_QUESTION).ShowModal()
        if dial == wx.ID_YES:
            remove()

    def load_model(self):
        # convert to os specific path
        os_path = Path(self.path)
        os_path = os_path.__str__()
        # convert to panda specific
        panda_path = Filename.fromOsSpecific(os_path)
        #
        editor.command_mgr.do(commands.LoadModel(path=panda_path))

    def load_actor(self):
        # convert to os specific path
        os_path = Path(self.path)
        os_path = os_path.__str__()
        # convert to panda specific
        panda_path = Filename.fromOsSpecific(os_path)
        #
        editor.command_mgr.do(commands.AddActor(path=panda_path))


class ImageTilesPanel(ScrolledPanel):
    class State:
        def __init__(self, selected_tiles: list):
            """Class representing state of ImageTilesPanel"""
            self.selected_tiles = selected_tiles

    class ToolBar(wx.Window):
        """Class containing various settings and options for image_tiles_panel"""

        def __init__(self, parent, *args, **kwargs):
            wx.Window.__init__(self, parent, *args, **kwargs)
            self.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))
            self.parent = parent

            # -------------------------------------------------------------------------------------------------
            self.main_sizer = wx.BoxSizer(wx.VERTICAL)  # the main sizer
            self.SetSizer(self.main_sizer)  # set sizer

            static_line = wx.Panel(self)
            static_line.SetMaxSize(wx.Size(-1, 3))
            static_line.SetBackgroundColour(wx.Colour(80, 80, 80, 255))
            self.main_sizer.Add(static_line, 0, wx.EXPAND)

            self.nested_h_sizer = wx.BoxSizer(wx.HORIZONTAL)  # nested h sizer for search control and buttons
            self.main_sizer.Add(self.nested_h_sizer, 0, wx.EXPAND)  # add it to main sizer

            # -------------------------------------------------------------------------------------------------
            # search box control
            self.search_control = SearchBox(self)
            self.search_control.SetMinSize(wx.Size(200, -1))
            self.search_control.SetMaxSize(wx.Size(-1, 14))

            # filter buttons
            self.filter_buttons = []

            models_filter_btn = SelectionButton(self, 0, "Models", image_path=Model_icon)
            texture_filter_btn = SelectionButton(self, 1, "Textures", image_path=Texture_icon)
            sounds_filter_btn = SelectionButton(self, 2, "Sounds", image_path=Sound_icon)
            scripts_filter_btn = SelectionButton(self, 3, "Scripts", image_path=Script_icon)

            self.filter_buttons = [models_filter_btn, texture_filter_btn, sounds_filter_btn, scripts_filter_btn]

            for btn in self.filter_buttons:
                btn.SetMinSize(wx.Size(85, -1))
                btn.SetMaxSize(wx.Size(-1, 14))

            # static line for separation
            static_line = wx.Panel(self)
            static_line.SetMaxSize(wx.Size(-1, 3))
            static_line.SetBackgroundColour(wx.Colour(80, 80, 80, 255))

            # static text panel to display selected item path info
            self.sel_item_label_panel = wx.Panel(self)
            self.sel_item_label_panel.SetBackgroundColour(wx.Colour(110, 110, 110, 255))
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.sel_item_label_panel.SetSizer(sizer)

            self.sel_item_label_ctrl = wx.StaticText(self.sel_item_label_panel, label="")
            self.sel_item_label_ctrl.SetForegroundColour(editor.ui_config.color_map("Panel_Light"))
            self.sel_item_label_ctrl.SetFont(wx.Font(7, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.FONTWEIGHT_BOLD))
            sizer.Add(self.sel_item_label_ctrl, 1, wx.EXPAND | wx.LEFT, border=2)

            # -------------------------------------------------------------------------------------------------
            self.nested_h_sizer.Add(self.search_control, 1, wx.EXPAND | wx.RIGHT, border=1)

            self.nested_h_sizer.Add(models_filter_btn, 1, wx.EXPAND | wx.RIGHT, 1)
            self.nested_h_sizer.Add(texture_filter_btn, 1, wx.EXPAND | wx.RIGHT, 1)
            self.nested_h_sizer.Add(sounds_filter_btn, 1, wx.EXPAND | wx.RIGHT, 1)
            self.nested_h_sizer.Add(scripts_filter_btn, 1, wx.EXPAND | wx.RIGHT, 1)

            self.main_sizer.Add(static_line, 0, wx.EXPAND)
            self.main_sizer.Add(self.sel_item_label_panel, 0, wx.EXPAND | wx.TOP, 0)

        def on_filter_btn_pressed(self, btn_index):
            pass

        def set_item_info_text(self, txt: str):
            self.sel_item_label_ctrl.SetLabel(txt)

    TILES_PER_ROW = 5
    Tile_offset_x = 12
    Tile_offset_y = 42
    TILE_SIZE = 64

    def __init__(self, parent):
        ScrolledPanel.__init__(self, parent)
        self.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))

        self.__tool_bar = self.ToolBar(parent)

        self.__parent = parent
        self.__tiles = []
        self.__selected_tiles = []
        self.__saved_state = None

        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.__gridSizer = None
        self.SetSizer(self.__sizer)

        self.supported_extensions_to_icons_map = {
            "generic": UnknownFile_icon,

            # model files
            "egg": ModelFile_icon,
            "bam": ModelFile_icon,
            "pz": ModelFile_icon,
            "gltf": ModelFile_icon,
            "glb": ModelFile_icon,

            # image files
            "tiff": ImageFile_icon,
            "tga": ImageFile_icon,
            "jpg": ImageFile_icon,
            "png": ImageFile_icon,

            # other
            "py": UserModule_icon,
            "ed_plugin": EditorPlugin_icon,
            "txt": TextFile_icon,

            # audio
            "mp3": AudioFile_icon,
            "wav": AudioFile_icon,

            # video
            ".mp4": VideoFile_icon,
        }

        self.Bind(wx.EVT_SIZE, self.on_evt_resize)

    def on_evt_resize(self, evt):
        if self.__gridSizer:
            self.__gridSizer.Clear()
        self.update_tiles()
        evt.Skip()

    def create_tile(self, image, label, extension, data):
        tile = ImageTile(parent=self,
                         label=label,
                         extension=extension,
                         style=wx.BORDER_NONE,
                         color=editor.ui_config.color_map("Panel_Dark"),
                         size=(10, 10),
                         position=(0, 0),
                         data=data)

        self.__tiles.append(tile)
        tile.set_image(image)
        tile.Hide()

    def set_from_selections(self, selections):
        self.Freeze()
        self.remove_all_tiles()
        selections_organized = {}
        for key in self.supported_extensions_to_icons_map:
            selections_organized[key] = []
        selections_organized["generic"] = []  # add one generic for not supported extensions.

        for _dir, path in selections:
            if not os.path.isdir(path):
                print("[TilesPanel] Path {0} not found".format(path))
                continue
            dir_items = os.listdir(path)
            for item in dir_items:

                if os.path.isdir(os.path.join(path, item)):
                    continue

                split = item.split(".")
                extension = split[-1]
                file_name = split[0]
                file_path = os.path.join(path, item)

                if extension in self.supported_extensions_to_icons_map:

                    if editor.level_editor.is_module(file_path):
                        module = editor.level_editor.get_module(file_path)
                        if isinstance(module, RuntimeModule):
                            image = UserModule_icon
                        elif isinstance(module, Component):
                            pass
                        elif isinstance(module, EditorPlugin):
                            image = EditorPlugin_icon
                    else:
                        image = self.supported_extensions_to_icons_map[extension]

                    selections_organized[extension].append((image, file_name, extension, file_path))
                else:
                    image = self.supported_extensions_to_icons_map["generic"]
                    selections_organized["generic"].append((image, file_name, extension, file_path))

        for item in selections_organized.keys():
            value = selections_organized[item]
            for _item in value:
                self.create_tile(_item[0], _item[1], _item[2], _item[3])

        self.update_tiles()
        self.Thaw()

    def select_tiles(self, tiles, select=True):
        if len(tiles) > 0:
            self.deselect_all()
            for i in range(len(tiles)):
                if tiles[i] in self.__tiles:
                    if select:
                        tiles[i].on_select()
                    self.__selected_tiles.append(tiles[i])

            self.__tool_bar.set_item_info_text(tiles[0].path)

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

                self.__tool_bar.set_item_info_text(tile.path)

    def deselect_all(self):
        for tile in self.__tiles:
            tile.on_deselect()
        self.__tool_bar.set_item_info_text("No item selected.")
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

        self.__gridSizer = wx.GridSizer(num_rows, tiles_per_row, 1, 0)
        self.__sizer.Add(self.__gridSizer, 1, wx.EXPAND)

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

                self.__gridSizer.Add(tile, 0)
                tile.Show()

        self.__gridSizer.Layout()
        self.__sizer.Layout()
        self.SetupScrolling(scroll_x=True)

    def remove_all_tiles(self):
        for tile in self.__tiles:
            tile.Destroy()
        self.__tiles = []
        self.__selected_tiles.clear()
        if self.__gridSizer:
            self.__gridSizer.Clear()
        self.update_tiles()

    def get_selected_tiles(self, paths=False):
        selected = []
        if len(self.__selected_tiles) > 0:
            if paths:
                for tile in self.__selected_tiles:
                    selected.append(tile.path)
            else:
                for tile in self.__selected_tiles:
                    selected.append(tile)
        return selected

    def get_tiles(self, paths=False):
        tiles = []
        for i in range(len(self.__tiles)):
            if paths:
                tiles.append(self.__tiles[i].path)
            else:
                tiles.append(self.__tiles[i].path)
        return tiles

    def get_tile_from_path(self, path):
        for i in range(len(self.__tiles)):
            if self.__tiles[i].path == path:
                return self.__tiles[i]
        return None

    @property
    def tool_bar(self):
        return self.__tool_bar
