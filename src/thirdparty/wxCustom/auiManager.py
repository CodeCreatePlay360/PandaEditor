import wx.lib.agw.aui as aui


AUI_NOTEBOOK_FLAGS = aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS | \
                     aui.AUI_NB_CLOSE_ON_ALL_TABS | aui.AUI_NB_TOP | aui.AUI_NB_TAB_EXTERNAL_MOVE | \
                     aui.AUI_NB_TAB_FIXED_WIDTH


class AuiManagerSaveData:
    def __init__(self, layout, panels):
        self.layout = layout
        self.panels = panels


class AuiManager(aui.AuiManager):
    def __init__(self, wx_main):
        aui.AuiManager.__init__(self)
        self.wx_main = wx_main
        self.__saved_layouts = {}

        # tell AuiManager to manage this frame
        self.SetManagedWindow(self.wx_main)
        self.Bind(aui.EVT_AUI_PANE_CLOSE, self.on_evt_pane_closed)

    def save_current_layout(self, name):
        if name not in self.__saved_layouts.keys():
            layout = self.SavePerspective()
            panel_names = [x.name for x in self.GetAllPanes()]
            save_data_obj = AuiManagerSaveData(layout, panel_names)
            self.__saved_layouts[name] = save_data_obj
            return True
        else:
            print("[AuiManager (function: save_current_layout)] Unable to save layout, key {0} already "
                  "exists".format(name))
            return False

    def save_layout(self, name, panels, layout):
        save_data_obj = AuiManagerSaveData(layout, panels)
        self.__saved_layouts[name] = save_data_obj

    def load_layout(self, layout):
        if layout in self.__saved_layouts.keys():
            layout_data = self.__saved_layouts[layout]

            # get names of all panels available in current session
            current_panels = [x.name for x in self.GetAllPanes()]

            # make sure all the panels from saved layout are available in this session as well
            for panel_name in layout_data.panels:
                if panel_name in current_panels:
                    pass
                else:
                    print("unable to load layout {0}, pane {1} is not available in current session...!".
                          format(layout, panel_name))
                    return

            # close all panels except for toolbar panels
            all_panes = self.GetAllPanes()
            for panel in all_panes:
                if panel.name not in self.wx_main.tb_panes:
                    self.ClosePane(panel)

            self.LoadPerspective(layout_data.layout)
            return True

        else:
            print("unable to load tab {0}".format(layout))
            return False

    def has_layout(self, layout):
        if layout in self.__saved_layouts.keys():
            return True
        return False

    def get_saved_layouts(self):
        return self.__saved_layouts

    def on_evt_pane_closed(self, evt):
        self.wx_main.on_pane_close(evt.GetPane().name)
        evt.Skip()
