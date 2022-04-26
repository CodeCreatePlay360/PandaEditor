import wx.lib.agw.aui as aui


AUI_NOTEBOOK_FLAGS = aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS | \
                     aui.AUI_NB_CLOSE_ON_ALL_TABS | aui.AUI_NB_TOP | aui.AUI_NB_TAB_EXTERNAL_MOVE | \
                     aui.AUI_NB_TAB_FIXED_WIDTH


class AuiNotebook(aui.AuiNotebook):
    def __init__(self, parent, agw_flags, art_provider):
        aui.AuiNotebook.__init__(self, parent)
        self.SetAGWWindowStyleFlag(agw_flags)
        self.SetArtProvider(art_provider)

        self.active_tabs = []

        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.on_page_close)

    def add_page(self, panel, name):
        if not self.active_tabs.__contains__(name):
            self.AddPage(panel, name, False)
            self.active_tabs.append(name)

    def load_save_data(self, save_data):
        # make sure save data class is not None or on it's default values
        if save_data.tabs is None or save_data.layout == "":
            return

        page_count = self.notebook.GetPageCount()

        while page_count != -1:
            self.notebook.RemovePage(0)
            page_count -= 1

        self.notebook.clear_all_tabs()
        self.notebook.Refresh()
        self.notebook.Layout()

        for i in range(len(save_data.tabs)):
            panel = self.wx_main.panels_repo[save_data.tabs[i]]
            self.notebook.add_page(panel, save_data.tabs[i].__str__())

        self.notebook.LoadPerspective(save_data.layout)
        
    def clear_all_tabs(self):
        self.active_tabs.clear()
        
    def get_save_data(self):
        notebook_save_data = NotebookSaveData(self.notebook.SavePerspective(), self.notebook.active_tabs)
        return notebook_save_data
        
    def on_page_close(self, evt):
        name = self.GetPage(evt.GetSelection()).name
        if self.active_tabs.__contains__(name):
            self.active_tabs.remove(name)
        evt.Skip()


class NotebookSaveData:
    def __init__(self, layout="", tabs=None):
        self.layout = layout
        self.tabs = []
        if tabs is not None:
            for tab in tabs:
                self.tabs.append(tab)


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
            print(layout)
            panel_names = [x.name for x in self.GetAllPanes()]

            save_data_obj = AuiManagerSaveData(layout, panel_names)

            self.__saved_layouts[name] = save_data_obj

            return True

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
