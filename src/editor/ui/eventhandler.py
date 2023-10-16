import os.path
import wx
from editor.UIEvtHandlerABC import UIEvtHandlerABC
from editor.ui.panels import ID_PROPERTIES_PANEL_OBJECT_TAB
from editor.globals import editor
from game.constants import TAG_GAME_OBJECT


class WxEventHandler(UIEvtHandlerABC):
    @staticmethod
    def handle_event(*args):
        if args[0] == "AddObject":
            nps = args[1]

            editor.resource_browser.deselect_all_files()

            for np in nps:
                editor.scene_graph.add(np)

            editor.scene_graph.select(nps)
            editor.inspector.layout_auto()

        elif args[0] == "AppendLibrary":
            dir_dialog = wx.DirDialog(None, style=wx.DD_DEFAULT_STYLE)
            if dir_dialog.ShowModal() == wx.ID_OK:
                path = dir_dialog.GetPath()
                dlg = wx.TextEntryDialog(None, 'LibraryName', 'Set Library Name', value=os.path.basename(path))

                if dlg.ShowModal() == wx.ID_OK:
                    name = dlg.GetValue()
                    if name == "":
                        return False
                    # editor.wx_main.resource_browser.tree.append_library(name, path)
                    tree = editor.wx_main.resource_browser.tree
                    tree.AppendItem(tree.GetRootItem(), name, data=path, image=1)
                    tree.Refresh()
                    return name, path
                else:
                    return False

        elif args[0] == "CreateNewSession":
            dlg = wx.MessageDialog(parent=None,
                                   message="Confirm create new session ?",
                                   caption="NewSession",
                                   style=wx.YES | wx.NO | wx.ICON_QUESTION)
            res = dlg.ShowModal()
            if res == wx.ID_YES:
                return True
            return False

        elif args[0] == "DeselectAll":
            editor.scene_graph.UnselectAll()
            editor.inspector.layout_auto()

        elif args[0] == "EditorReload":
            project_path = args[1]
            ed_selections = args[2]

            editor.console.on_ed_reload()
            editor.resource_browser.create_or_rebuild_tree(project_path, rebuild_event=True)
            wx.CallAfter(editor.inspector.layout_auto)
            return editor.resource_browser.resources

        elif args[0] == "OnEnableEditorState":
            editor.scene_graph.rebuild()
            editor.scene_graph.UnselectAll()
            editor.inspector.layout_auto()

        elif args[0] == "OnEnableGameState":
            # editor.scene_graph.UnselectAll()
            editor.console.on_enter_game_state()

        elif args[0] == "OnRemoveNPs":
            nps = args[1]
            editor.scene_graph.on_remove(nps)

        elif args[0] == "SwitchEdState":
            wx_main = editor.wx_main
            state = args[1]

            # change graphics
            if state == 1:
                wx_main.ply_btn.SetBitmap(wx_main.stop_icon)
                wx_main.file_menu_tb.ToggleTool(wx_main.ply_btn.GetId(), True)
            elif state == 0:
                wx_main.ply_btn.SetBitmap(wx_main.play_icon)
                wx_main.file_menu_tb.ToggleTool(wx_main.ply_btn.GetId(), False)

            wx_main.file_menu_tb.Realize()

        elif args[0] == "ToggleSceneLights":
            wx_main = editor.wx_main
            toggled_on = args[1]

            # change graphics
            if toggled_on:
                wx_main.lights_toggle_btn.SetBitmap(wx_main.lights_on_icon)
                wx_main.file_menu_tb.ToggleTool(wx_main.lights_toggle_btn.GetId(), True)
            elif not toggled_on:
                wx_main.lights_toggle_btn.SetBitmap(wx_main.lights_off_icon)
                wx_main.file_menu_tb.ToggleTool(wx_main.lights_toggle_btn.GetId(), False)

            wx_main.file_menu_tb.Refresh()

        elif args[0] == "XFormTask":
            """updates properties panel according to currently selected object"""
            force_update_all = args[1]
            if editor.inspector and editor.inspector.has_object():
                editor.inspector.update(force_update_all=force_update_all)


@editor.observer.on("ResourceTileSelected")
def resource_tile_selected(file_path):
    def on_module_selected(module):
        inspector.layout(module, module.module_name, module.get_properties())

    def on_txt_file_selected(txt_file):
        inspector.set_text(txt_file.text)

    inspector = editor.inspector
    if inspector.get_selected_tab() is not ID_PROPERTIES_PANEL_OBJECT_TAB:
        return
    
    editor.level_editor.deselect_all()
    editor.scene_graph.UnselectAll()

    if editor.level_editor.is_module(file_path):
        on_module_selected(editor.level_editor.get_module(file_path))
    elif editor.level_editor.is_text_file(file_path):
        on_txt_file_selected(editor.level_editor.get_text_file(file_path))
    else:
        inspector.set_text("No inspector defined for this item.")
