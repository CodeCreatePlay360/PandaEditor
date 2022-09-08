import wx
import wx.lib.agw.customtreectrl as customtree
from editor.constants import obs, object_manager


class BaseTreeControl(customtree.CustomTreeCtrl):
    def __init__(self, parent, *args, **kwargs):
        """Base tree controls implements a custom drag drop operation"""

        customtree.CustomTreeCtrl.__init__(self, parent, *args, **kwargs)

        # for drag drop operations
        self.mouse_left_down = False
        self.is_dragging = False
        self.current_selected = []

        self.Bind(wx.EVT_LEFT_DOWN, self.on_evt_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_evt_left_up)
        self.Bind(wx.EVT_MOTION, self.on_evt_mouse_move)

    def on_evt_left_down(self, evt):
        self.mouse_left_down = True
        evt.Skip()

    def on_evt_mouse_move(self, evt):
        if self.mouse_left_down:
            self.is_dragging = True

            for item in self.current_selected:
                self.SetItemTextColour(item, wx.Colour(0, 0, 0, 255))

            # highlight item under the mouse, when dragging
            self.current_selected.clear()
            x, y = evt.GetPosition()
            (_id, flag) = self.HitTest((x, y))
            if _id:
                self.SetItemTextColour(_id, wx.Colour(255, 255, 190, 255))
                self.current_selected.append(_id)

        if not self.is_dragging and len(self.current_selected) > 0:
            self.end_drag()

        evt.Skip()

    def on_evt_left_up(self, evt):
        # do drag drop here
        x, y = evt.GetPosition()
        (_id, flag) = self.HitTest((x, y))

        if self.is_dragging and _id:
            # print("{0} dropped onto {1}".format(self.GetSelections(), self.GetItemText(_id)) )
            selections = []
            for item in self.GetSelections():
                if _id == item:
                    continue

                selections.append(item)

            self.do_drag_drop(selections, _id)

        self.mouse_left_down = False
        self.is_dragging = False
        obs.trigger("OnMouse1up", self)
        evt.Skip()

    def end_drag(self):
        for item in self.current_selected:
            self.SetItemTextColour(item, wx.Colour(0, 0, 0, 255))
        self.is_dragging = False
        self.mouse_left_down = False

    def do_drag_drop(self, src_items: list, target_dir: str):
        print("do drag drop is empty")
