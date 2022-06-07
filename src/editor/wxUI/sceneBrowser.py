import wx
import editor.constants as constants
from panda3d.core import NodePath
from wx.lib.scrolledpanel import ScrolledPanel
from editor.wxUI.baseTreeControl import BaseTreeControl
from editor.colourPalette import ColourPalette as Colours


EVT_RENAME_ITEM = wx.NewId()
EVT_REMOVE_ITEM = wx.NewId()


class SceneBrowserPanel(ScrolledPanel):
    def __init__(self, *args, **kwargs):
        ScrolledPanel.__init__(self, *args, **kwargs)

        self.wx_main = args[0]

        self.scene_graph = SceneBrowser(self, self.wx_main)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.scene_graph, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.Layout()
        self.SetupScrolling()


class SceneBrowser(BaseTreeControl):

    class State:
        """class representing a saved state of SceneBrowser"""
        def __init__(self):
            self.selected_items = []

    def __init__(self, parent, wx_main, *args, **kwargs):
        BaseTreeControl.__init__(self, parent, *args, **kwargs)

        self.wx_main = wx_main
        constants.object_manager.add_object("SceneGraphPanel", self)
        self.organize_tree = True  # organize a tree based on file_extensions

        # ---------------------------------------------------------------------------- #
        self.SetBackgroundColour(Colours.NORMAL_GREY)
        self.SetWindowStyleFlag(wx.BORDER_SUNKEN)

        agw_win_styles = wx.TR_DEFAULT_STYLE | wx.TR_SINGLE | wx.TR_MULTIPLE | wx.TR_HIDE_ROOT
        agw_win_styles |= wx.TR_TWIST_BUTTONS | wx.TR_NO_LINES

        self.SetAGWWindowStyleFlag(agw_win_styles)
        self.SetIndent(10)
        self.SetSpacing(10)

        self.SetBorderPen(wx.Pen((0, 0, 0), 0, wx.TRANSPARENT))
        self.EnableSelectionGradient(True)
        self.SetGradientStyle(True)
        self.SetFirstGradientColour(wx.Colour(46, 46, 46))
        self.SetSecondGradientColour(wx.Colour(123, 123, 123))

        self.root_node = self.AddRoot("SceneGraph", data=None)
        self.parent_node = None

        self.np_to_tree_item_map = {}  # np: tree_item

        self.saved_state = None

        self.evt_map = {EVT_RENAME_ITEM: self.rename_item,
                        EVT_REMOVE_ITEM: self.remove_item}

        # bind events
        self.Bind(wx.EVT_MENU, self.on_evt_popup_menu)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_evt_select)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.create_popup_menu)

    def init(self, parent_np):
        # clear old data
        if self.parent_node is not None:
            old_parent_np = self.GetItemData(self.parent_node)
            del self.np_to_tree_item_map[old_parent_np]
            self.Delete(self.parent_node)

        # add new parent node
        self.parent_node = self.AppendItem(self.root_node, "SceneGraph", data=parent_np)
        self.np_to_tree_item_map[parent_np] = self.parent_node

    def rebuild(self, parent_np):
        """recursively builds scene graph panel from argument node path"""

        parent_np = self.GetItemData(self.parent_node)

        self.np_to_tree_item_map.clear()
        self.np_to_tree_item_map[parent_np] = self.parent_node

        self.DeleteChildren(self.parent_node)
        self._add(parent_np, self.parent_node)

    def add_np(self, selection):
        """recursively add a panda3d node-path into the tree along with its children"""
        def add_np_to_tree(_np):
            if _np.hasNetPythonTag(constants.TAG_PICKABLE):
                _np = _np.getPythonTag(constants.TAG_PICKABLE)
                if _np is None:
                    return
                parent_scene_graph_item = self.np_to_tree_item_map[_np.get_parent()]
                scene_graph_item = self.AppendItem(parent_scene_graph_item, _np.get_name(), data=_np)
                self.np_to_tree_item_map[_np] = scene_graph_item

        def add_children(_np):
            if len(_np.getChildren()) > 0:
                for child in _np.getChildren():
                    add_np_to_tree(child)
                    # print(child)
                    add_children(child)

        if type(selection) is not list:
            selection = [selection]

        if type(selection) is list:
            for np in selection:
                add_np_to_tree(np)
                add_children(np)
        else:
            tree_item = self.AppendItem(self.parent_node, selection.get_name(), data=selection)
            self.np_to_tree_item_map[selection] = tree_item

    def on_remove_nps(self, nps):
        def _remove(selection):
            if len(selection.getChildren()) > 0:
                for child in selection.getChildren():
                    if type(child) is NodePath and child.hasPythonTag(constants.TAG_PICKABLE):
                        child = child.getPythonTag(constants.TAG_PICKABLE)
                        if child in self.np_to_tree_item_map:
                            del self.np_to_tree_item_map[child]
                        _remove(child)

        for np in nps:
            # first remove children of selected node paths from self.np_to_tree_item_map
            np = np.getPythonTag(constants.TAG_PICKABLE)
            _remove(np)

        for np in nps:
            # now remove parent node paths as well
            np = np.getPythonTag(constants.TAG_PICKABLE)
            if np in self.np_to_tree_item_map:
                tree_item = self.np_to_tree_item_map[np]
                self.Delete(tree_item)
                del self.np_to_tree_item_map[np]

    def select_np(self, selection):
        self.deselect_all()

        # temporarily unbind this, otherwise self.SelectItem will trigger
        # a call to self.on_evt_select
        self.Unbind(wx.EVT_TREE_SEL_CHANGED)

        if type(selection) is list:
            for np in selection:
                self.SelectItem(self.np_to_tree_item_map[np])
        else:
            self.SelectItem(self.np_to_tree_item_map[selection])

        # bind this again
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_evt_select)

    def deselect_all(self):
        self.UnselectAll()

    def _add(self, np, tree_item):
        if len(np.getChildren()) > 0:
            for child in np.getChildren():
                if type(child) is NodePath and child.hasPythonTag(constants.TAG_PICKABLE):

                    child = child.getPythonTag(constants.TAG_PICKABLE)

                    if child.get_parent() in self.np_to_tree_item_map.keys():
                        tree_item = self.np_to_tree_item_map[child.get_parent()]
                        tree_item = self.AppendItem(tree_item, child.get_name(), data=child)
                    else:
                        tree_item = self.AppendItem(tree_item, child.get_name(), data=child)

                    self.np_to_tree_item_map[child] = tree_item

                    self._add(child.getPythonTag(constants.TAG_PICKABLE), tree_item)

    def reparent(self, src_np, target_np):
        # get the source and target items
        src_item = self.np_to_tree_item_map[src_np]
        target_item = self.np_to_tree_item_map[target_np]

        # remove target item
        self.Delete(src_item)

        tree_item = self.AppendItem(target_item, src_np.get_name(), data=src_np)
        self.np_to_tree_item_map[src_np] = tree_item

        self._add(src_np, tree_item)

    def create_popup_menu(self, evt):
        popup_menu = wx.Menu()

        # create menu items
        rename_menu = wx.MenuItem(popup_menu, EVT_RENAME_ITEM, "RenameItem")
        popup_menu.Append(rename_menu)

        remove_menu = wx.MenuItem(popup_menu, EVT_REMOVE_ITEM, "RemoveItem")
        popup_menu.Append(remove_menu)

        popup_menu.AppendSeparator()

        self.PopupMenu(popup_menu, evt.GetPoint())
        popup_menu.Destroy()

        # self.on_evt_select()

        evt.Skip()

    def on_evt_popup_menu(self, evt):
        if evt.GetId() in self.evt_map.keys():
            func = self.evt_map[evt.GetId()]
            func()
        evt.Skip()

    def on_evt_select(self, evt):
        selections = []
        for item in self.GetSelections():
            if item == self.parent_node:
                continue
            selections.append(self.GetItemPyData(item))

        constants.obs.trigger("OnSelectSceneGraphItem", selections)
        evt.Skip()

    def do_drag_drop(self, src_item: str, target_item: str):
        src_np = self.GetItemData(src_item)
        target_np = self.GetItemData(target_item)

        # ------------------------TO:FIX----------------------------------------------- #
        # just for the time being, until a proper system is implemented .... ?? for what
        invalid_uids = ["EdCameraNp", "PointLight", "SpotLight", "DirectionalLight"]
        if target_np.getPythonTag(constants.TAG_PICKABLE) and target_np.uid in invalid_uids:
            return
        # ------------------------------------------------------------------------------ #

        constants.obs.trigger(constants.obs.trigger("ReparentNPs", src_np, target_np))

    def on_item_rename(self, np, name):
        tree_item = self.np_to_tree_item_map[np]
        self.SetItemText(tree_item, name)

    def rename_item(self):
        np = self.GetItemData(self.GetSelection())
        constants.obs.trigger("RenameNPs", np)

    def remove_item(self):
        np = self.GetItemData(self.GetSelection())
        constants.obs.trigger("RemoveNPs", [np])

    def get_selected_np(self):
        sel = self.GetSelection()
        if sel:
            return self.GetItemData(sel)

    def save_state(self):
        """saves the current state of tree e.g. currently selected tree items"""
        self.saved_state = SceneBrowser.State()
        for item in self.GetSelections():
            np = self.GetItemData(item)
            self.saved_state.selected_items.append(np)

    def reload_state(self):
        """reloads saved state"""
        for np in self.saved_state.selected_items:
            self.SelectItem(self.np_to_tree_item_map[np])
