import os
import shutil
import wx
import editor.constants as constants
import editor.uiGlobals as uiGlobals
import editor.wxUI.globals as wxGlobals
import editor.resources.globals as resourceGlobals

from editor.wxUI.baseTreeControl import BaseTreeControl
from editor.utils.exceptionHandler import try_execute
from editor.utils import DirWatcher
from thirdparty.wxCustom.imageTilesPanel import ImageTilesPanel
from editor.utils import PathUtils

# event ids for different event types
EVT_NEW_DIR = wx.NewId()
EVT_RENAME_ITEM = wx.NewId()
EVT_DUPLICATE_ITEM = wx.NewId()
EVT_REMOVE_ITEM = wx.NewId()
EVT_SHOW_IN_EXPLORER = wx.NewId()

EVT_CREATE_PY_MOD = wx.NewId()
EVT_CREATE_TXT_FILE = wx.NewId()
EVT_CREATE_P3D_USER_MOD = wx.NewId()
EVT_CREATE_ED_TOOL = wx.NewId()

EVT_APPEND_LIBRARY = wx.NewId()
EVT_IMPORT_ASSETS = wx.NewId()


# ----------------- Methods for building context menus ----------------- #
def create_generic_menu_items(parent_menu):
    menu_items = [(EVT_RENAME_ITEM, "&Rename", None),
                  (EVT_REMOVE_ITEM, "&Remove", None),
                  (EVT_DUPLICATE_ITEM, "&Duplicate", None)]
    wxGlobals.build_menu(parent_menu, menu_items)


def create_3d_model_menu_items(parent_menu):
    menu_items = [(EVT_LOAD_MODEL, "&Load Model", None),
                  (EVT_LOAD_ACTOR, "&Load As Actor", None)]
    wxGlobals.build_menu(parent_menu, menu_items)


def create_add_menu_items(parent_menu):
    # add objects menu
    objects_items = [
        (EVT_CREATE_PY_MOD, "&Python Module", None),
        (EVT_CREATE_P3D_USER_MOD, "&User Module", None),
        (EVT_CREATE_ED_TOOL, "&Editor Plugin", None),
        (EVT_CREATE_TXT_FILE, "&Text File", None),
        (EVT_NEW_DIR, "&New Folder", None)
    ]
    objects_menu = wx.Menu()
    wxGlobals.build_menu(objects_menu, objects_items)
    parent_menu.Append(wx.ID_ANY, "Add", objects_menu)

    # import assets menu
    import_assets_item = wx.MenuItem(parent_menu, EVT_IMPORT_ASSETS, "Import Assets")
    parent_menu.Append(import_assets_item)
    parent_menu.AppendSeparator()

    # show in explorer menu
    library_items = [(EVT_SHOW_IN_EXPLORER, "&Show In Explorer", None)]
    wxGlobals.build_menu(parent_menu, library_items)


class ResourceBrowser(wx.Panel):
    class State:
        """class representing a saved state of ResourceBrowser"""

        def __init__(self, selected_items: list):
            self.selected_items = selected_items

    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.wx_main = args[0]

        self.splitter_win = wx.SplitterWindow(self)

        self.resource_tree = ResourceTree(self.splitter_win, self.wx_main)
        self.tiles_panel = ImageTilesPanel(self.splitter_win, self.resource_tree)

        self.splitter_win.SplitVertically(self.resource_tree, self.tiles_panel)
        self.splitter_win.SetMinimumPaneSize(180)
        # self.splitter_win.SetSashPosition(, True)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.splitter_win, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.Layout()


class ResourceTree(BaseTreeControl):
    def __init__(self, parent, wx_main, *args, **kwargs):
        BaseTreeControl.__init__(self, parent, *args, **kwargs)

        self.wx_main = wx_main
        self.organize_tree = True  # should tree be organized based on file extensions ?

        constants.object_manager.add_object("ProjectBrowser", self)

        # ---------------------------------------------------------------------------- #
        self.SetBackgroundColour(uiGlobals.ColorPalette.NORMAL_GREY)
        self.SetWindowStyleFlag(wx.BORDER_SUNKEN)

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
        self.image_list = wx.ImageList(16, 16)  # create an image list for tree control to use

        self.folder_icon_bitmap_blue = wx.Bitmap(resourceGlobals.FOLDER_ICON_BLUE)
        self.folder_icon_bitmap_green = wx.Bitmap(resourceGlobals.FOLDER_ICON_GREEN)
        self.image_list.Add(self.folder_icon_bitmap_blue)
        self.image_list.Add(self.folder_icon_bitmap_green)
        self.SetImageList(self.image_list)
        # ---------------------------------------------------------------------------- #

        self.root_node = self.AddRoot("RootNode", data="")
        self.root_path = ""

        # for drag drop operations
        self.mouse_left_down = False
        self.is_dragging = False

        self.saved_state = None

        # ---------------------------------------------------------------------------- #
        self.libraries = {}  # all current loaded libraries
        self.resources = {}  # save all resources with same file extension e.g [py] = {all .py resources}...
        self.name_to_item = {}  # maps a file's or directory's name to it's corresponding tree item
        # e.g. name_to_item[file_name] = item

        self.event_map = {
            EVT_NEW_DIR: (self.on_file_op, "add_folder"),
            EVT_RENAME_ITEM: (self.on_file_op, "rename_item"),
            EVT_DUPLICATE_ITEM: (self.on_file_op, "duplicate"),
            EVT_REMOVE_ITEM: (self.on_file_op, "remove_item"),
            EVT_SHOW_IN_EXPLORER: (self.on_file_op, "show_in_explorer"),

            EVT_CREATE_PY_MOD: (self.create_asset, "py_mod"),
            EVT_CREATE_TXT_FILE: (self.create_asset, "txt_file"),
            EVT_CREATE_P3D_USER_MOD: (self.create_asset, "p3d_user_mod"),
            EVT_CREATE_ED_TOOL: (self.create_asset, "p3d_ed_tool"),

            EVT_APPEND_LIBRARY: (self.append_library, None),
            EVT_IMPORT_ASSETS: (self.import_assets, None),
        }

        # start the directory watcher
        self.dir_watcher = DirWatcher()

        # finally, bind event handlers with corresponding function calls
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_item_expanded)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_item_collapsed)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_item_selected)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_item_activated)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.create_popup_menu)
        self.Bind(wx.EVT_MENU, self.on_select_context)

    # ----------------- All methods bounded to different tree events ----------------- #
    def on_item_expanded(self, event):
        event.Skip()

    def on_item_collapsed(self, event):
        event.Skip()

    def on_item_selected(self, evt):
        selections = []
        for item in self.GetSelections():
            name = self.GetItemText(item)
            data = self.GetItemData(item)
            selections.append((name, data))

        constants.obs.trigger("ResourceItemSelected", selections)
        evt.Skip()

    def on_item_activated(self, evt):
        evt.Skip()

    def create_popup_menu(self, evt):
        popup_menu = wx.Menu()

        create_add_menu_items(popup_menu)
        create_generic_menu_items(popup_menu)

        self.PopupMenu(popup_menu, evt.GetPoint())
        popup_menu.Destroy()

        evt.Skip()

    def on_select_context(self, event):
        if event.GetId() in self.event_map.keys():
            foo = self.event_map[event.GetId()][0]
            args = self.event_map[event.GetId()][1]
            foo(args)

        event.Skip()

    # ---------------------- All methods for building tree items ---------------------- #
    def create_or_rebuild_tree(self, path, rebuild_event: bool):
        """rebuild a tree from scratch from argument path or rebuild tree from libraries if rebuild_event"""
        if not rebuild_event:
            # then recreate it from scratch
            # print("ResourceBrowser --> Building resources")

            self.libraries.clear()
            self.resources.clear()
            self.name_to_item.clear()
            self.DeleteChildren(self.GetRootItem())
            self.UnselectAll()

            self.root_path = path

            # create a key for each know file type
            for ext in resourceGlobals.EXTENSIONS.keys():
                self.resources[ext] = []

            # setup a default project library
            tree_item = self.AppendItem(self.root_node, "Project", data=path, image=1)
            self.libraries["Project"] = (path, tree_item)

            self.create_tree_from_dir(dir_path=path, parent=tree_item)
            self.dir_watcher.schedule(path, append=False)  # start monitoring
            self.Expand(tree_item)
        else:
            print("[ResourceBrowser] Rebuilding resources")

            # TODO unschedule and re-schedule directory watcher

            self.resources.clear()
            self.name_to_item.clear()
            self.DeleteChildren(self.GetRootItem())
            self.UnselectAll()

            # create a key for each know file type
            for ext in resourceGlobals.EXTENSIONS.keys():
                self.resources[ext] = []

            # recreate all the libraries
            for key in self.libraries.keys():
                path = self.libraries[key][0]
                tree_item = self.AppendItem(self.root_node, key, data=path, image=1)
                self.name_to_item[key] = tree_item
                self.create_tree_from_dir(path, tree_item)

            root_node = self.libraries["Project"][1]
            self.Expand(root_node)
            self.Refresh()

    def create_tree_from_dir(self, dir_path=None, parent=None):
        dir_files = os.listdir(dir_path)

        for file in dir_files:
            file_path = dir_path + "/" + file

            if os.path.isdir(file_path) and file != "__pycache__":
                item = self.AppendItem(parent, file, data=file_path, image=0)
                # self.SetItemTextColour(item, wx.Colour(255, 255, 190, 255))
                self.Expand(item)
                self.name_to_item[file] = item

                self.create_tree_from_dir(file_path, item)

            elif os.path.isfile(file_path) and file != "__init__":
                extension = file_path.split(".")[-1]

                # make sure extension exists otherwise add a new key
                if extension in self.resources.keys():
                    pass
                else:
                    self.resources[extension] = []

                self.resources[extension].append(file_path)

    def append_library(self, name, path):
        if name not in self.libraries.keys():
            tree_item = self.AppendItem(self.root_node, name, data=path, image=1)
            self.libraries[name] = (path, tree_item)
            self.dir_watcher.schedule(path)
        else:
            print("Library with name {0} already exists".format(name))

    def remove_library(self, name):
        tree_item = self.libraries[name][1]
        self.Delete(tree_item)
        self.dir_watcher.unschedule(self.libraries[name])
        del self.libraries[name]

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

    def do_drag_drop(self, src_item, target_item):
        """src_path = the file/dir being dragged
        target_path = the file/dir src_path is dropped onto"""

        if self.GetItemText(src_item) in self.libraries.keys():
            print("Cannot drag drop library item")
            return

        src_path = self.GetItemData(src_item)
        target_path = self.GetItemData(target_item)

        # move source file / dir to target path
        # target directory must exist
        if not os.path.isdir(target_path):
            print("[ResourceBrowser] Invalid target dir {0}".format(target_path))
            return

        # source file / dir must exist
        if os.path.isfile(src_path) or os.path.isdir(src_path):

            # generate a new target path (to move src_path to) by combining target_path with src file/dir name
            new_target_path = target_path + "/" + src_path.split("/")[-1]

            # make sure the new_target_path already does not exist
            if os.path.isdir(new_target_path) or os.path.isfile(new_target_path):
                print("[ResourceBrowser] File/directory already exists {0}".format(new_target_path))
                return

            shutil.move(src_path, new_target_path)

        else:
            print("[ResourceBrowser] Invalid source file or directory {0}".format(src_path))

    @staticmethod
    def show_in_explorer(path):
        path = os.path.realpath(path)
        os.startfile(path)

    @staticmethod
    def add_dir(curr_directory):
        """adds a new directory and returns it"""

        def on_ok(_new_dir_name):
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

        wx_main = constants.object_manager.get("WxMain")
        dm = wx_main.dialogue_manager
        dm.create_dialog("TextEntryDialog", "New Directory", dm, descriptor_text="Enter name", ok_call=on_ok)

    def rename_item(self):
        def on_ok(new_label):
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
            if item_text in self.libraries.keys():
                if new_label not in self.libraries.keys():
                    del self.libraries[item_text]
                    self.libraries[new_label] = current_path
                else:
                    print("[ResourceBrowser]: Failed to rename item")
            elif PathUtils.rename(self.GetItemData(self.GetSelection()), new_label):
                self.SetItemText(self.GetSelection(), new_label)
            else:
                print("[ResourceBrowser]: Failed to rename item")

        dm = self.wx_main.dialogue_manager
        dm.create_dialog("TextEntryDialog",
                         "Rename Item",
                         dm, descriptor_text="Rename Selection",
                         ok_call=on_ok,
                         initial_text=self.GetItemText(self.GetSelection()))

    def duplicate(self, *args):
        pass

    def remove_item(self, *args):
        def on_ok():
            selections = self.GetSelections()
            for item in selections:
                item_text = self.GetItemText(item)
                item_path = self.GetItemData(item)

                if item_text == "Project":
                    print("[ResourceBrowser] Cannot remove project path...!")
                    continue

                if item_text in self.libraries.keys():
                    self.remove_library(item_text)
                else:
                    if PathUtils.delete(item_path):
                        del self.name_to_item[item_text]  # remove from name_to_items
                        self.Delete(item)

        dm = self.wx_main.dialogue_manager
        dm.create_dialog("YesNoDialog",
                         "Delete Item",
                         dm,
                         descriptor_text="Confirm remove selection(s) ?",
                         ok_call=on_ok)

    def create_asset(self, _type):
        def on_ok(text):
            if text == "":
                return

            path = self.GetItemData(self.GetSelection())
            path = path + "/" + text

            if os.path.exists(path):
                print("path already exists...!")
                return

            constants.obs.trigger("CreateAsset", _type, path)

        wx_main = constants.object_manager.get("WxMain")
        dm = wx_main.dialogue_manager
        dm.create_dialog("TextEntryDialog", "CreateNewAsset", dm, descriptor_text="New Asset Name", ok_call=on_ok)

    def import_assets(self, *args):
        def create_wild_card(wild_card=""):
            for ext in resourceGlobals.EXTENSIONS:
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

                try_execute(copy_item, path, new_path)  # copy file from path to new_path

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

    def get_item_by_name(self, item_name=""):
        if self.name_to_item.__contains__(item_name):
            return self.name_to_item[item_name]
        return None

    def save_state(self):
        """saves the current state of tree e.g. currently selected tree items"""
        selected_items = []
        for item in self.GetSelections():
            item_text = self.GetItemText(item)
            selected_items.append(item_text)

        self.saved_state = ResourceBrowser.State(selected_items)

    def reload_state(self):
        """reloads saved state"""
        for item_text in self.saved_state.selected_items:
            try:
                self.SelectItem(self.name_to_item[item_text])
            except KeyError:
                print("[ResourceTree] Key {0} was not found".format(item_text))
                self.SelectItem(self.name_to_item["Project"])
