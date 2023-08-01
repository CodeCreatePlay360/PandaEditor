import os
import pickle
import shutil
import sys
import wx
import wx.lib.agw.customtreectrl as customtree
import editor.ui.utils as wxUtils

from pathlib import Path
from editor.utils.exceptionHandler import try_execute
from editor.utils import DirWatcher, FileUtils
from editor.ui.etc.dragDropData import ResourceDragDropData
from editor.globals import editor
from editor.constants import ICONS_PATH
from thirdparty.wxCustom.imageTilesPanel import ImageTilesPanel

# resources
FOLDER_ICON_BLUE = str(Path(ICONS_PATH + "/folder16.png"))
LIB_FOLDER_ICON = str(Path(ICONS_PATH + "/libFolderIcon.png"))
#
Music_icon = str(Path(ICONS_PATH + "/ResourceTiles/music.png"))
Video_icon = str(Path(ICONS_PATH + "/ResourceTiles/video.png"))
#
# all supported extensions
EXTENSIONS = {"generic": Music_icon,

              # model files
              "egg":  Music_icon,
              "bam":  Music_icon,
              "pz":   Music_icon,
              # "fbx":  MODEL_ICON,
              "obj":  Music_icon,
              # "gltf": MODEL_ICON,

              # image files
              "tiff": Music_icon,
              "tga":  Music_icon,
              "jpg":  Music_icon,
              "png":  Music_icon,

              # other
              "py":  Music_icon,
              "ed_plugin": Music_icon,
              "txt": Music_icon,

              # audio
              "mp3": Music_icon,
              "wav": Music_icon,

              # video
              ".mp4": Music_icon,
              }
#
# event ids for different event types
EVT_NEW_DIR = wx.NewId()
EVT_RENAME_ITEM = wx.NewId()
EVT_DUPLICATE_ITEM = wx.NewId()
EVT_REMOVE_ITEM = wx.NewId()
EVT_SHOW_IN_EXPLORER = wx.NewId()

EVT_CREATE_RUNTIME_MOD = wx.NewId()
EVT_CREATE_COMPONENT = wx.NewId()
EVT_CREATE_ED_PLUGIN = wx.NewId()
EVT_CREATE_PY_MOD = wx.NewId()
EVT_CREATE_TXT_FILE = wx.NewId()

EVT_APPEND_LIBRARY = wx.NewId()
EVT_IMPORT_ASSETS = wx.NewId()


# ----------------- Methods for building context menus ----------------- #
def create_generic_menu_items(parent_menu):
    menu_items = [(EVT_RENAME_ITEM, "&Rename", None),
                  (EVT_REMOVE_ITEM, "&Remove", None),
                  (EVT_DUPLICATE_ITEM, "&Duplicate", None)]
    wxUtils.build_menu(parent_menu, menu_items)


def create_add_menu_items(parent_menu):
    # add objects menu
    objects_items = [
        (EVT_CREATE_RUNTIME_MOD, "RuntimeUserModule", None),
        (EVT_CREATE_COMPONENT, "Component", None),
        (EVT_CREATE_ED_PLUGIN, "EditorPlugin", None),
        (EVT_CREATE_PY_MOD, "Python Module", None),
        (EVT_CREATE_TXT_FILE, "Text File", None),
        (EVT_NEW_DIR, "New Folder", None)
    ]
    objects_menu = wx.Menu()
    wxUtils.build_menu(objects_menu, objects_items)
    parent_menu.Append(wx.ID_ANY, "Add", objects_menu)

    # import assets menu
    import_assets_item = wx.MenuItem(parent_menu, EVT_IMPORT_ASSETS, "Import Assets")
    parent_menu.Append(import_assets_item)
    parent_menu.AppendSeparator()

    # show in explorer menu
    library_items = [(EVT_SHOW_IN_EXPLORER, "&Show In Explorer", None)]
    wxUtils.build_menu(parent_menu, library_items)


# TODO make implementation in this class as part of image tiles panel
class ResourceTiles(wx.Panel):
    def __init__(self, parent, *args):
        wx.Panel.__init__(self, parent, *args)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.tiles_panel = ImageTilesPanel(self)

        static_line = wx.Panel(self)
        static_line.SetMaxSize(wx.Size(-1, 3))
        static_line.SetBackgroundColour(wx.Colour(60, 60, 60, 255))

        self.sizer.Add(self.tiles_panel.tool_bar, 0, wx.EXPAND)
        self.sizer.Add(static_line, 0, wx.EXPAND)
        self.sizer.Add(self.tiles_panel, 1, wx.EXPAND)


class ResourceBrowser(wx.Panel):
    class State:
        """class representing a saved state of ResourceBrowser"""

        def __init__(self, open_or_close: dict):
            """open_or_close = tree item paths to their corresponding expanded to unexpanded state map"""
            self.open_or_close = open_or_close

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # constants.object_manager.add_object("ResourceBrowser", self)

        self.wx_main = args[0]
        self.splitter_win = wx.SplitterWindow(self)
        self.splitter_win.SetWindowStyleFlag(wx.SP_NO_XP_THEME)  # NO_XP_THEME, otherwise you cannot change BG color
        self.splitter_win.SetBackgroundColour(wx.Colour(200, 200, 200, 255))

        self.tiles = ResourceTiles(self.splitter_win)
        self.tree = ResourceTree(self.splitter_win, self.wx_main, self.tiles.tiles_panel)

        self.splitter_win.SplitVertically(self.tree, self.tiles)
        self.splitter_win.SetMinimumPaneSize(180)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.splitter_win, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.Layout()


class ResourceTree(customtree.CustomTreeCtrl):
    def __init__(self, parent, wx_main, preview_tiles_panel, *args, **kwargs):
        customtree.CustomTreeCtrl.__init__(self, parent, *args, **kwargs)

        self.__parent = parent
        self.__wx_main = wx_main
        self.__organize_tree = True  # should tree be organized based on file extensions ?

        self.__tiles_panel = preview_tiles_panel

        # ---------------------------------------------------------------------------- #
        self.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))

        agw_win_styles = wx.TR_DEFAULT_STYLE | wx.TR_SINGLE | wx.TR_MULTIPLE | wx.TR_HIDE_ROOT
        agw_win_styles |= wx.TR_TWIST_BUTTONS

        self.SetAGWWindowStyleFlag(agw_win_styles)
        self.SetIndent(10)
        self.SetSpacing(10)

        self.SetBorderPen(wx.Pen((0, 0, 0), 0, wx.TRANSPARENT))
        self.EnableSelectionGradient(True)
        self.SetGradientStyle(True)
        self.SetFirstGradientColour(wx.Colour(46, 46, 46))
        self.SetSecondGradientColour(wx.Colour(123, 123, 123))

        # ---------------------------------------------------------------------------- #
        self.__image_list = wx.ImageList(16, 16)  # create an image list for tree control to use

        self.__folder_icon_bitmap_blue = wx.Bitmap(FOLDER_ICON_BLUE)
        self.__folder_icon_bitmap_green = wx.Bitmap(LIB_FOLDER_ICON)
        self.__image_list.Add(self.__folder_icon_bitmap_blue)
        self.__image_list.Add(self.__folder_icon_bitmap_green)
        self.SetImageList(self.__image_list)
        # ---------------------------------------------------------------------------- #

        self.__root_node = self.AddRoot("RootNode", data="")
        self.__root_path = ""

        self.__saved_state = None

        # ---------------------------------------------------------------------------- #
        self.__libraries = {}  # all current loaded libraries
        self.__resources = {}  # save all resources with same file extension e.g [py] = {all .py resources}...
        self.__path_to_item = {}  # maps a file's or directory's name to it's corresponding tree item
        # e.g. name_to_item[file_name] = item

        self.__event_map = {
            EVT_NEW_DIR: (self.on_file_op, "add_folder"),
            EVT_RENAME_ITEM: (self.on_file_op, "rename_item"),
            EVT_DUPLICATE_ITEM: (self.on_file_op, "duplicate"),
            EVT_REMOVE_ITEM: (self.on_file_op, "remove_item"),
            EVT_SHOW_IN_EXPLORER: (self.on_file_op, "show_in_explorer"),

            EVT_CREATE_RUNTIME_MOD: (self.create_asset, "p3d_user_mod"),
            EVT_CREATE_COMPONENT: (self.create_asset, "component"),
            EVT_CREATE_ED_PLUGIN: (self.create_asset, "p3d_ed_tool"),
            EVT_CREATE_PY_MOD: (self.create_asset, "py_mod"),
            EVT_CREATE_TXT_FILE: (self.create_asset, "txt_file"),

            EVT_APPEND_LIBRARY: (self.append_library, None),
            EVT_IMPORT_ASSETS: (self.import_assets, None),
        }

        # start the directory watcher
        self.__dir_watcher = DirWatcher()

        # create a drop target
        self.can_drag_drop = True
        dt = TestDropTarget(self)
        self.SetDropTarget(dt)

        # finally, bind event handlers with corresponding function calls
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_item_selected)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.on_item_expanding)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.create_popup_menu)
        self.Bind(wx.EVT_MENU, self.on_select_context)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag)

    # ----------------- All methods bounded to different tree events ----------------- #
    def on_item_selected(self, evt):
        selections = []
        for item in self.GetSelections():
            name = self.GetItemText(item)
            data = self.GetItemData(item)
            selections.append((name, data))

        # constants.obs.trigger("OnSelectFolder", selections)
        self.__tiles_panel.set_from_selections(selections)
        evt.Skip()

    def on_item_expanding(self, evt):
        self.Refresh()
        evt.Skip()

    def create_popup_menu(self, evt):
        popup_menu = wx.Menu()

        create_add_menu_items(popup_menu)
        create_generic_menu_items(popup_menu)

        self.PopupMenu(popup_menu, evt.GetPoint())
        popup_menu.Destroy()

        evt.Skip()

    def on_select_context(self, event):
        if event.GetId() in self.__event_map.keys():
            foo = self.__event_map[event.GetId()][0]
            args = self.__event_map[event.GetId()][1]
            foo(args)

        event.Skip()

    def on_begin_drag(self, evt):
        # create data that is being dragged
        dragged_data = ResourceDragDropData(ResourceDragDropData.RESOURCE_BROWSER)
        dragged_data.set_source([])

        # pickle dragged data
        picked_data = pickle.dumps(dragged_data, 1)

        # create a custom data obj and set its data to dragged data
        custom_data_obj = wx.CustomDataObject(wx.DataFormat('ResourceBrowserData | ImageTileData'))
        custom_data_obj.SetData(picked_data)

        # create a source for drag and drop
        drop_source = TestDropSource(self, win=self)
        drop_source.SetData(custom_data_obj)

        # Initiate the Drag Operation
        drag_result = drop_source.DoDragDrop()
        editor.wx_main.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        evt.Skip()

    def collapse_all(self):
        for path in self.__path_to_item.keys():
            item = self.__path_to_item[path]
            self.Collapse(item)

    # ---------------------- All methods for building tree items ---------------------- #
    def create_or_rebuild_tree(self, path, rebuild_event: bool):
        """rebuild a tree from scratch from argument path or rebuild tree from libraries if rebuild_event"""
        if not rebuild_event:
            # clear libraries
            self.remove_all_libs()
            self.__resources.clear()
            self.__path_to_item.clear()
            self.DeleteChildren(self.GetRootItem())
            self.UnselectAll()

            self.__root_path = path

            # create a key for each know file type
            for ext in EXTENSIONS.keys():
                self.__resources[ext] = []

            # setup, a default project library
            # tree_item = self.AppendItem(self.root_node, "Project", data=path, image=1)
            tree_item = self.append_library("Project", path)

            self.create_tree_from_dir(dir_path=path, parent=tree_item)
        else:
            print("[ResourceBrowser] Rebuilding resources")
            # TODO unschedule and re-schedule directory watcher

            self.__resources.clear()
            self.__path_to_item.clear()
            self.DeleteChildren(self.GetRootItem())
            self.UnselectAll()

            # create a key for each know file type
            for ext in EXTENSIONS.keys():
                self.__resources[ext] = []

            # recreate all the libraries
            for key in self.__libraries.keys():
                path = self.__libraries[key][0]
                tree_item = self.AppendItem(self.__root_node, key, data=path, image=1)
                self.__path_to_item[key] = tree_item
                self.create_tree_from_dir(path, tree_item)

        self.ExpandAll()
        self.Refresh()

    def create_tree_from_dir(self, dir_path=None, parent=None):
        dir_files = os.listdir(dir_path)

        for file in dir_files:
            file_path = os.path.join(str(Path(dir_path)), file)
            # print(file_path)
            if os.path.isdir(file_path) and file != "__pycache__":
                item = self.AppendItem(parent, file, data=file_path, image=0)
                self.__path_to_item[file_path] = item
                self.create_tree_from_dir(file_path, item)

            elif os.path.isfile(file_path) and file != "__init__":
                extension = file_path.split(".")[-1]

                # make sure extension exists otherwise add a new key
                if extension in self.__resources.keys():
                    pass
                else:
                    self.__resources[extension] = []

                self.__resources[extension].append(file_path)

    def schedule_dir_watcher(self):
        for key in self.__libraries.keys():
            path = self.__libraries[key][0]
            self.__dir_watcher.schedule(path)

    def append_library(self, name, path, schedule=False):
        if name not in self.__libraries.keys():
            tree_item = self.AppendItem(self.__root_node, name, data=path, image=1)
            self.__libraries[name] = (path, tree_item)
            # print("[ResourceTree] AppendedLib name: {0} path: {1}".format(name, path))
            if schedule:
                self.__dir_watcher.schedule(path)
            return tree_item
        else:
            print("Library with name {0} already exists".format(name))

    def remove_library(self, name, remove_key=True):
        path = self.__libraries[name][0]
        tree_item = self.__libraries[name][1]
        self.Delete(tree_item)
        self.__dir_watcher.unschedule(path)
        if remove_key:
            del self.__libraries[name]

    def remove_all_libs(self):
        for name in self.__libraries.keys():
            self.remove_library(name, remove_key=False)
        self.__libraries.clear()

    # ----------------- file explorer operations ----------------- #
    def on_file_op(self, op, *args, **kwargs):
        def can_perform_operation():
            if self.GetSelection() == self.GetRootItem():
                return False
            return True

        if op == "add_folder":
            curr_dir = self.GetItemData(self.GetSelection())
            self.add_dir(curr_dir)

        elif op == "show_in_explorer":
            self.show_in_explorer(self.GetItemData(self.GetSelection()))

        elif op == "rename_item" and can_perform_operation():
            self.rename_item()

        elif op == "duplicate" and can_perform_operation():
            self.duplicate()

        elif op == "remove_item" and can_perform_operation():
            self.remove_item()

    def do_drag_drop(self, src_items, target_item):
        """src_path = file / dir being dragged
        target_path = path where src_path is dropped onto"""

        for i in range(len(src_items)):

            src_item = src_items[i]

            if self.GetItemText(src_item) in self.__libraries.keys():
                print("Cannot drag drop library item")
                return

            src_path = self.GetItemData(src_item)
            target_path = self.GetItemData(target_item)

            # target directory must exist
            if not os.path.isdir(target_path):
                print("[ResourceBrowser] Invalid target dir {0}".format(target_path))
                return

            # source file / dir must exist
            if os.path.isfile(src_path) or os.path.isdir(src_path):

                # generate a new target path by combining target_path with src file or dir name
                if sys.platform == "win32" or sys.platform == "win64":
                    new_target_path = os.path.join(target_path, src_path.split("\\")[-1])
                else:
                    new_target_path = os.path.join(target_path, src_path.split("/")[-1])

                # make sure the new_target_path already does not exist
                if os.path.exists(new_target_path):
                    print("[ResourceBrowser] File or directory already exists {0}".format(new_target_path))
                    return

                shutil.move(src_path, new_target_path)

            else:
                print("[ResourceBrowser] Invalid source file or directory {0}".format(src_path))

    @staticmethod
    def show_in_explorer(path):
        path = os.path.realpath(path)
        if sys.platform == "linux":
            os.system('xdg-open "%s"' % path)
        else:
            # os.system('xdg-open "%s"' % path)
            os.startfile(path)

    @staticmethod
    def add_dir(curr_directory):
        """adds a new directory and returns it"""

        def create(_new_dir_name):
            if _new_dir_name == "":
                return

            curr_dir = curr_directory
            new_dir = curr_dir + "/" + _new_dir_name

            # make sure new_dir already does not exist
            if os.path.isdir(new_dir):
                print("[ResourceBrowser] Directory already exists")
                return

            os.mkdir(new_dir)
            return _new_dir_name

        dial = wx.TextEntryDialog(None, "New Directory", "Enter name", "NewDirectory")
        if dial.ShowModal() == wx.ID_OK:
            create(dial.GetValue())

    def rename_item(self):
        def rename(new_label):
            if new_label == "":
                print("[ResourceBrowser] Invalid item name}")
                return

            selection = self.GetSelection()
            current_path = self.GetItemData(selection)
            item_text = self.GetItemText(selection)

            if item_text == "Project":
                print("[ResourceBrowser] Cannot rename this item...!")
                return

            # if the selected item is a library item, then remove existing library entry,
            # and create a new one with existing data as of original entry
            # also make sure libraries does not have an existing entry matching new text
            if item_text in self.__libraries.keys():
                if new_label not in self.__libraries.keys():
                    del self.__libraries[item_text]
                    self.__libraries[new_label] = current_path
                else:
                    print("[ResourceBrowser]: Failed to rename item")
            else:
                old_path = current_path
                if sys.platform == "linux":
                    old_name_ = old_path.split("/")[-1]
                elif sys.platform == "win32" or sys.platform == "win64":
                    old_name_ = old_path.split("\\")[-1]
                else:
                    return

                new_path = old_path[:len(old_path) - len(old_name_) - 1]
                new_path = os.path.join(new_path, new_label)

                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)

        old_name = self.GetItemText(self.GetSelections()[0])
        dial = wx.TextEntryDialog(None, "Rename resource item", "Rename", old_name)
        if dial.ShowModal():
            new_name = dial.GetValue()
            if new_name != old_name:
                rename(new_name)

    def duplicate(self, *args):
        pass

    def remove_item(self, *args):
        def remove():
            selections = self.GetSelections()
            for item in selections:
                item_text = self.GetItemText(item)
                item_path = self.GetItemData(item)

                if item_text == "Project":
                    print("[ResourceBrowser] Cannot remove project path...!")
                    continue

                if item_text in self.__libraries.keys():
                    self.remove_library(item_text)
                else:
                    success = False
                    try:
                        success = FileUtils.delete(item_path)
                    except PermissionError:
                        print("PermissionError")
                    finally:
                        if success:
                            del self.__path_to_item[item_text]  # remove from name_to_items
                            self.Delete(item)

        dial = wx.MessageDialog(None, "Confirm remove folder ?", "Remove item",
                                style=wx.YES_NO | wx.ICON_QUESTION).ShowModal()
        if dial == wx.ID_YES:
            remove()

    def create_asset(self, _type):
        def create(text):
            if text == "":
                return

            path = self.GetItemData(self.GetSelection())
            path = path + "/" + text

            if os.path.exists(path):
                print("path already exists...!")
                return

            editor.observer.trigger("CreateAsset", _type, path)

        dial = wx.TextEntryDialog(None, "Create New Asset", "New Asset Name", "NewAsset")
        if dial.ShowModal() == wx.ID_OK:
            create(dial.GetValue())

    def import_assets(self, *args):
        def create_wild_card(wild_card=""):
            for ext in EXTENSIONS:
                wild_card += "*" + "." + ext + ";"
            return wild_card

        def copy_item(src_item, _dst):
            shutil.copyfile(src_item, _dst)

        # create wildcard from supported extensions
        wd = "import assets |"
        wd = create_wild_card(wd)

        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
        with wx.FileDialog(self, "Import Assets", style=style) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed to import the selected files
            selected_file_paths = fileDialog.GetPaths()  # paths of all selected files
            target_destination = self.GetItemData(self.GetSelection())  # destination to copy to

            for path in selected_file_paths:
                file_name = path.split("\\")[-1]  # get file name
                new_path = target_destination + "\\" + file_name  # create a new path

                if os.path.exists(new_path):
                    print("copy error file {0} already exists...!".format(file_name))
                    pass

                try_execute(copy_item, path, new_path)  # copy file from path to new_pat

    # ----------------- other ----------------- #
    def select(self, selection):
        self.UnselectAll()

        # temporarily unbind this, otherwise self.SelectItem will trigger
        # a call to self.on_evt_select
        self.Unbind(wx.EVT_TREE_SEL_CHANGED)

        # sometimes self.SelectItem called from SetData of TestDropTarget, triggers
        # EVT_TREE_BEGIN_DRAG operation again, so unbind it.
        self.Unbind(wx.EVT_TREE_BEGIN_DRAG)

        if type(selection) is list:
            for item in selection:
                self.SelectItem(item)
        else:
            self.SelectItem(selection)

        # bind this again
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_item_selected)
        self.Refresh()

    def deselect_all_files(self):
        self.__tiles_panel.deselect_all()

    def save_state(self):
        """saves the current state of tree e.g. currently selected tree items"""
        open_or_close = {}  # tree item paths to their corresponding expanded to unexpanded state map

        for path in self.__path_to_item.keys():
            item = self.__path_to_item[path]
            if self.IsExpanded(item):
                open_or_close[path] = item

        self.__saved_state = ResourceBrowser.State(open_or_close)

    def reload_state(self):
        """reloads saved state"""
        for path in self.__path_to_item.keys():
            if path == "Project":
                continue
            item = self.__path_to_item[path]
            self.Collapse(item)

        for path in self.__saved_state.open_or_close.keys():
            if path in self.__path_to_item.keys():
                self.Expand(self.__path_to_item[path])
        self.__tiles_panel.remove_all_tiles()
        self.Refresh()

    def can_do_drag_drop(self, drop_item):
        def is_ok_(item_):
            for child_ in item_.GetChildren():
                if child_ == drop_item:
                    self.can_drag_drop = False
                else:
                    is_ok_(child_)

        self.can_drag_drop = True
        for item in self.GetSelections():
            if drop_item == item:
                self.can_drag_drop = False
        for item in self.GetSelections():
            is_ok_(item)

    def get_selected_path(self):
        """Get the selected path"""
        sel = self.GetSelection()
        path = self.GetItemPyData(sel)
        return path

    def get_selected_paths(self):
        """Get a list of selected paths"""
        selections = self.GetSelections()
        paths = [self.GetItemPyData(sel) for sel in selections]
        return paths

    def get_item_by_path(self, item_name=""):
        if self.__path_to_item.__contains__(item_name):
            return self.__path_to_item[item_name]
        return None

    @property
    def selected_folders(self):
        return self.get_selected_paths()

    @property
    def selected_files(self):
        return self.__tiles_panel.get_selected_tiles(paths=True)

    @property
    def resources(self):
        return self.__resources

    @property
    def libraries(self):
        return self.__libraries


class TestDropSource(wx.DropSource):
    def __init__(self, tree, win):
        wx.DropSource.__init__(self, win=win)
        self.tree = tree
        self.data = None

    def SetData(self, data):
        wx.DropSource.SetData(self, data)
        self.data = data

    def GiveFeedback(self, effect):
        (window_x, window_y) = wx.GetMousePosition()

        # first check if we are inside the tree
        (x, y) = self.tree.ScreenToClient(window_x, window_y)
        (item_under_mouse, flag) = self.tree.HitTest((x, y))
        self.tree.can_do_drag_drop(item_under_mouse)
        if not self.tree.can_drag_drop:
            editor.wx_main.SetCursor(wx.Cursor(wx.CURSOR_NO_ENTRY))
            return True
        else:
            editor.wx_main.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
            return False


class TestDropTarget(wx.PyDropTarget):
    """ This is a custom DropTarget object designed to match drop behavior to the feedback given by the custom
       Drag Object's GiveFeedback() method. """

    def __init__(self, tree):
        wx.DropTarget.__init__(self)
        self.tree = tree

        self.target_item = None
        self.drop_location = None

        # specify the data formats to accept
        self.data_format = wx.DataFormat('ResourceBrowserData | ImageTileData')
        self.custom_data_obj = wx.CustomDataObject(self.data_format)
        self.SetDataObject(self.custom_data_obj)

    def OnEnter(self, x, y, d):
        # print "OnEnter %s, %s, %s" % (x, y, d)
        # Just allow the normal wxDragResult (d) to pass through here
        return d

    def OnLeave(self):
        pass

    def OnDrop(self, x, y):
        (id_, flag) = self.tree.HitTest((x, y))
        if not id_:
            return False

        temp_str = self.tree.GetItemText(id_)
        self.target_item = id_
        self.drop_location = temp_str
        # print("Dropped {0} on {1}".format(id_, temp_str))
        return True

    def OnData(self, x, y, d):
        if self.GetData():
            data = pickle.loads(self.custom_data_obj.GetData())
        else:
            return wx.DragNone

        if data.drag_source == ResourceDragDropData.RESOURCE_BROWSER:
            self.tree.can_do_drag_drop(self.target_item)
            if not self.tree.can_drag_drop:
                return wx.DragError
            self.tree.do_drag_drop(src_items=self.tree.GetSelections(), target_item=self.target_item)

        elif data.drag_source == ResourceDragDropData.PREVIEW_TILES_PANEL:
            src_paths = data.paths
            for i in range(len(src_paths)):
                src_path = src_paths[i]

                if sys.platform == "linux":
                    file = src_path.split("/")[-1]
                elif sys.platform == "win32":
                    file = src_path.split("\\")[-1]
                else:
                    return wx.DragError

                new_target_path = os.path.join(self.tree.GetItemData(self.target_item), file)

                if os.path.isfile(new_target_path):
                    print("[ResourceBrowser] File already exists {0}".format(new_target_path))
                    return wx.DragError

                shutil.move(src_path, new_target_path)

        return d
