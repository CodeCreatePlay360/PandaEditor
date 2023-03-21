import pickle
import wx
import wx.lib.agw.customtreectrl as customtree
import editor.constants as constants
import editor.edPreferences as edPreferences
from panda3d.core import NodePath
from editor.wxUI.custom import SearchBox
from editor.commands import ReparentNPs, SelectObjects, RemoveObjects, RenameNPs
from editor.globals import editor

EVT_RENAME_ITEM = wx.NewId()
EVT_REMOVE_ITEM = wx.NewId()

CAMERA_ICON = constants.ICONS_PATH + "/SceneGraph/video.png"
LIGHT_ICON = constants.ICONS_PATH + "/SceneGraph/lightbulb.png"
OBJECT_ICON = constants.ICONS_PATH + "/SceneGraph/cube.png"


class SceneBrowserPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        # self.SetWindowStyleFlag(wx.BORDER_SUNKEN)
        self.SetBackgroundColour(edPreferences.Colors.Panel_Dark)
        self.wx_main = args[0]

        self.scene_graph = SceneBrowser(self, self.wx_main)
        self.search_box = SearchBox(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.search_box, 1, wx.EXPAND | wx.BOTTOM, border=1)
        sizer.Add(self.scene_graph, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.Layout()


class SceneBrowser(customtree.CustomTreeCtrl):
    class State:
        def __init__(self, item_names: list):
            self.item_names = item_names

    def __init__(self, parent, wx_main, *args, **kwargs):
        customtree.CustomTreeCtrl.__init__(self, parent, *args, **kwargs)
        self.wx_main = wx_main
        self.organize_tree = True  # organize a tree based on file_extensions

        # ---------------------------------------------------------------------------- #
        self.SetBackgroundColour(edPreferences.Colors.Panel_Normal)

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

        self.camera_icon = wx.Bitmap(CAMERA_ICON)
        self.light_icon = wx.Bitmap(LIGHT_ICON)
        self.np_icon = wx.Bitmap(OBJECT_ICON)

        self.image_list.Add(self.camera_icon)
        self.image_list.Add(self.light_icon)
        self.image_list.Add(self.np_icon)

        self.SetImageList(self.image_list)

        self.image_to_item_map = {

            constants.CAMERA_NODEPATH: 0,

            constants.AMBIENT_LIGHT: 1,
            constants.POINT_LIGHT: 1,
            constants.DIRECTIONAL_LIGHT: 1,
            constants.SPOT_LIGHT: 1,

            constants.NODEPATH: 2,

            constants.ACTOR_NODEPATH: 2
        }
        # ---------------------------------------------------------------------------- #

        self.saved_state = None

        self.root = self.AddRoot("RootItem", data=None)
        self.scene_graph_item = None
        self.scene_np = None
        self.np_id_to_tree_item_map = {}  # np: tree_item

        self.evt_map = {EVT_RENAME_ITEM: self.rename_item,
                        EVT_REMOVE_ITEM: self.remove_item}

        # create a drop target
        self.can_drag_drop = True
        dt = TestDropTarget(self)
        self.SetDropTarget(dt)

        # bind events
        self.Bind(wx.EVT_MENU, self.on_evt_popup_menu)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_evt_select)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.create_popup_menu)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag)
        self.Bind(wx.EVT_TREE_END_DRAG, self.on_end_drag)

    def init(self, parent_np):
        self.DeleteChildren(self.root)
        self.scene_np = parent_np
        self.scene_graph_item = self.AppendItem(self.root, "SceneGraph", data=parent_np)
        self.np_id_to_tree_item_map[parent_np] = self.scene_graph_item

    def create_popup_menu(self, evt):
        for sel in self.GetSelections():
            if self.GetItemText(sel) == "SceneGraph":
                return

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
            if item == self.scene_graph_item:
                continue
            np = self.GetItemPyData(item)
            np = np.getPythonTag(constants.TAG_GAME_OBJECT)
            selections.append(np)

        if len(selections) == 0:
            return

        le = editor.level_editor
        editor.command_mgr.do(SelectObjects(selections, [np for np in le.selection.selected_nps], from_le=False))
        evt.Skip()

    def on_begin_drag(self, evt):
        # create data that is being dragged
        dragged_data = TestDragDropData()
        dragged_data.set_source(None)

        # pickle dragged data
        picked_data = pickle.dumps(dragged_data, 1)

        # create a custom data obj and set its data to dragged data
        custom_data_obj = wx.CustomDataObject(wx.DataFormat('SceneBrowserData'))
        custom_data_obj.SetData(picked_data)

        # create a source for drag and drop
        drop_source = TestDropSource(self, win=self)
        drop_source.SetData(custom_data_obj)

        # Initiate the Drag Operation
        drag_result = drop_source.DoDragDrop()
        editor.wx_main.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        evt.Skip()

    def on_end_drag(self, evt):
        evt.Skip()

    def rebuild(self):
        """rebuild tree from parent nodepath"""
        self.UnselectAll()
        self.np_id_to_tree_item_map.clear()
        self.DeleteChildren(self.scene_graph_item)
        self.np_id_to_tree_item_map[self.scene_np] = self.scene_graph_item
        for np in self.scene_np.getChildren():
            self.add(np)

    def add(self, np, parent_item=None, only_children=False):
        """recursively add a nodepath and its children into tree"""
        def add_(np_, tree_item):
            for child in np_.getChildren():
                tree_item_ = None
                if isinstance(child, NodePath) and child.hasPythonTag(constants.TAG_GAME_OBJECT):

                    obj = child.getPythonTag(constants.TAG_GAME_OBJECT)
                    image = self.image_to_item_map[obj.id]
                    tree_item_ = self.AppendItem(tree_item,
                                                 child.get_name(),
                                                 data=obj,
                                                 image=image)

                    self.np_id_to_tree_item_map[child] = tree_item_

                if tree_item_ is not None:
                    add_(child, tree_item_)
                else:
                    add_(child, tree_item)

        # first check if parent of np to be added already exists
        if parent_item:
            parent_item_ = parent_item
        elif np.get_parent() in self.np_id_to_tree_item_map.keys():
            parent_item_ = self.np_id_to_tree_item_map[np.get_parent()]
        else:
            parent_item_ = self.scene_graph_item

        if not only_children:
            np = np.getPythonTag(constants.TAG_GAME_OBJECT)
            image = self.image_to_item_map[np.id]
            parent_item_ = self.AppendItem(parent_item_, np.get_name(), data=np, image=image)
            self.np_id_to_tree_item_map[np] = parent_item_

        add_(np, parent_item_)
        self.select(np)
        self.Refresh()

    def add_many(self):
        pass

    def remove_item(self):
        editor.command_mgr.do(RemoveObjects(self.get_selected_nps()))
        self.Refresh()

    def on_remove(self, nps):
        """recursively removes a nodepath and its children from tree"""

        def remove_(np_):
            for child in np_.getChildren():
                if isinstance(child, NodePath) and child.hasPythonTag(constants.TAG_GAME_OBJECT):
                    if self.np_id_to_tree_item_map.__contains__(child):
                        del self.np_id_to_tree_item_map[child]
                remove_(child)

        for np in nps:
            remove_(np)

        for np in nps:
            try:
                tree_item = self.np_id_to_tree_item_map[np]  # get tree item from np
                self.Delete(tree_item)
                del self.np_id_to_tree_item_map[np]
            except KeyError:
                pass

        self.Refresh()

    def select(self, selection):
        self.UnselectAll()

        # temporarily unbind this, otherwise self.SelectItem will trigger
        # a call to self.on_evt_select
        self.Unbind(wx.EVT_TREE_SEL_CHANGED)

        # sometimes self.SelectItem called from SetData of TestDropTarget, triggers
        # EVT_TREE_BEGIN_DRAG operation again, so unbind it.
        self.Unbind(wx.EVT_TREE_BEGIN_DRAG)

        if type(selection) is list:
            for np in selection:
                self.SelectItem(self.np_id_to_tree_item_map[np])
        else:
            self.SelectItem(self.np_id_to_tree_item_map[selection])

        # bind this again
        self.Refresh()
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_evt_select)

    def reparent(self, src_nps, target_np):
        """src_np = the nodepath being reparented,
        target_np = nodepath on which the src_np was dropped or dragged onto"""

        target_item = self.np_id_to_tree_item_map[target_np]

        for np in src_nps:
            src_np = np

            # delete old
            try:
                self.Delete(self.np_id_to_tree_item_map[src_np])  # the tree item
                del self.np_id_to_tree_item_map[src_np]
            except ValueError:
                pass

            obj = src_np.getPythonTag(constants.TAG_GAME_OBJECT)
            image = self.image_to_item_map[obj.id]
            tree_item = self.AppendItem(target_item, src_np.get_name(), data=src_np, image=image)
            self.np_id_to_tree_item_map[src_np] = tree_item

            self.add(src_np, tree_item, only_children=True)

        self.Refresh()

    def rename_item(self, np=None, new_name=None):
        if np and new_name:
            tree_item = self.np_id_to_tree_item_map[np]
            self.SetItemText(tree_item, new_name)
        else:
            np = self.get_selected_nps()[0]
            old_name = np.get_name()
            dial = wx.TextEntryDialog(None, "Enter new name", "Rename", old_name)
            if dial.ShowModal():
                new_name = dial.GetValue()
                if new_name != old_name:
                    tree_item = self.np_id_to_tree_item_map[np]
                    self.SetItemText(tree_item, new_name)

                    # finally, create the rename command
                    editor.command_mgr.do(RenameNPs(np, old_name, new_name))

        self.Refresh()

    def get_selected_nps(self):
        nps = []
        for item in self.GetSelections():
            nps.append(self.GetItemData(item))
        return nps

    def save_state(self):
        self.saved_state = None

    def reload_state(self):
        self.UnselectAll()

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


class TestDropSource(wx.DropSource):
    def __init__(self, tree, win):
        wx.DropSource.__init__(self, win=win)
        self.tree = tree
        self.data = None
        self.cannot_drop = False

    def SetData(self, data):
        wx.DropSource.SetData(self, data)
        self.data = data

    def GiveFeedback(self, effect):
        (window_x, window_y) = wx.GetMousePosition()
        (x, y) = self.tree.ScreenToClient(window_x, window_y)
        (item_under_mouse, flag) = self.tree.HitTest((x, y))

        self.tree.can_do_drag_drop(item_under_mouse)
        if not self.tree.can_drag_drop:
            editor.wx_main.SetCursor(wx.Cursor(wx.CURSOR_NO_ENTRY))
            effect = wx.DragNone
            return True
        else:
            editor.wx_main.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
            return False


class TestDragDropData(object):
    def __init__(self):
        self.data = []

    def __repr__(self):
        return "DragDropData"

    def set_source(self, data):
        self.data = data


class TestDropTarget(wx.PyDropTarget):
    """ This is a custom DropTarget object designed to match drop behavior to the feedback given by the custom
       Drag Object's GiveFeedback() method. """

    def __init__(self, tree):
        wx.DropTarget.__init__(self)
        self.tree = tree

        self.drop_item = None
        self.drop_location = None

        # specify the data formats to accept
        self.data_format = wx.DataFormat('SceneBrowserData')
        self.custom_data_obj = wx.CustomDataObject(self.data_format)
        self.SetDataObject(self.custom_data_obj)

    def OnEnter(self, x, y, d):
        # print "OnEnter %s, %s, %s" % (x, y, d)
        # Just allow the normal wxDragResult (d) to pass through here
        return d

    def OnLeave(self):
        # print "OnLeave"
        pass

    def OnDrop(self, x, y):
        (id_, flag) = self.tree.HitTest((x, y))
        if not id_:
            return False
        temp_str = self.tree.GetItemText(id_)
        self.drop_item = id_
        self.drop_location = temp_str
        # print("Dropped on %s." % temp_str)
        return True

    def OnData(self, x, y, d):
        def is_ok(np_):
            for np in np_.getChildren():
                is_ok(np)

        if self.GetData():
            data = pickle.loads(self.custom_data_obj.GetData())
        else:
            return wx.DragNone

        self.tree.can_do_drag_drop(self.drop_item)
        target_np = self.tree.GetItemData(self.drop_item)  # nps / tree items dropped onto
        nps = self.tree.get_selected_nps()  # nps / tree items being dragged

        if not self.tree.can_drag_drop:
            return wx.DragError
        else:
            editor.command_mgr.do(ReparentNPs(nps, target_np))

        return d
