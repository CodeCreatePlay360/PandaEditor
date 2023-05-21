import webbrowser
import wx

from thirdparty.event.observable import Observable
from editor.globals import editor
from editor.constants import GAME_STATE, TAG_GAME_OBJECT
from editor.utils import safe_execute


obs = Observable()


# Events mostly related to project
@obs.on("CreateNewProject")
def create_new_project(*args):
    print("create new project")


@obs.on("OpenProject")
def open_project(*args):
    print("open project")


@obs.on("BuildProject")
def build_project(*args):
    print("build project")


@obs.on("CreateNewSession")
def create_new_session(*args):
    le = editor.level_editor

    if le.ed_state is GAME_STATE:
        print("Exit game mode to create a new scene..!")
        return

    dlg = wx.MessageDialog(parent=None,
                           message="Confirm create new session ?",
                           caption="NewSession",
                           style=wx.YES | wx.NO | wx.ICON_QUESTION)
    res = dlg.ShowModal()
    if res == wx.ID_YES:
        le.create_new_scene()


@obs.on("OpenSession")
def open_session(*args):
    print("open session")


@obs.on("SaveSession")
def save_session(*args):
    print("save session")


@obs.on("SaveSessionAs")
def save_session_as(*args):
    print("save session as")


@obs.on("AppendLibrary")
def append_library(*args):
    le = editor.level_editor
    resource_tree = editor.resource_browser
    wx_main = editor.wx_main

    if le.ed_state is GAME_STATE:
        print("Exit game mode to append new library..!")
        return

    dir_dialog = wx.DirDialog(None, style=wx.DD_DEFAULT_STYLE)

    if dir_dialog.ShowModal() == wx.ID_OK:
        path = dir_dialog.GetPath()
        dlg = wx.TextEntryDialog(wx_main, 'LibraryName', 'Set Library Name', value="")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()

            if name != "":
                resource_tree.append_library(name, path)


@obs.on("CreateAsset")
def create_asset(asset_type, path):
    def indent_file(_file, spaces):
        # add indentation by adding empty spaces
        for i in range(spaces):
            _file.write(" ")

    def write_p3d_module(base_class, new_class_name):
        with open(path, "w") as file_:
            file_.write("import math\n")
            file_.write("import panda3d.core as p3d_core\n")
            file_.write("from editor.core import {0}\n\n\n".format(base_class))

            # class header and init method
            file_.write("class {0}({1}):".format(new_class_name, base_class))
            file_.write("\n")
            indent_file(file_, 4)
            file_.write("def __init__(self, *args, **kwargs):\n")

            indent_file(file_, 8)
            file_.write(base_class + ".__init__(self, *args, **kwargs)\n\n")

            indent_file(file_, 8)
            file_.write("# __init__ should not contain anything except for variable declaration\n\n")

            # write start method
            indent_file(file_, 4)
            file_.write("def on_start(self):\n")
            indent_file(file_, 8)
            file_.write("# this method is called only once\n")
            indent_file(file_, 8)
            file_.write("pass\n\n")

            # write update method
            indent_file(file_, 4)
            file_.write("def on_update(self):\n")
            indent_file(file_, 8)
            file_.write("# this method is called every frame\n")
            indent_file(file_, 8)
            file_.write("pass\n\n")

    def write_py_module(class_name, base_class):
        with open(path, "w") as file_:
            file_.write("import math\n\n\n")

            # class header and init method
            file_.write("class {0}({1}):".format(class_name, base_class))
            file_.write("\n")
            indent_file(file_, 4)
            file_.write("def __init__(self, *args, **kwargs):\n")

            indent_file(file_, 8)
            file_.write("pass\n")

    if asset_type == "p3d_user_mod":
        base_mod_name = "runtimeModule"
        base_class_name = "RuntimeModule"
        path += ".py"

    elif asset_type == "p3d_ed_tool":
        base_mod_name = "editorPlugin"
        base_class_name = "EditorPlugin"
        path += ".py"

    elif asset_type == "component":
        base_mod_name = "component"
        base_class_name = "Component"
        path += ".py"

    elif asset_type == "txt_file":
        path += ".txt"
        with open(path, "w") as txt_file:
            txt_file.write("pass\n")
        return

    else:
        base_mod_name = "object"
        base_class_name = "object"
        path += ".py"
    # ------------------------------------------ #

    cls_name = path.split(".")[0]
    cls_name = cls_name.split("/")[-1]
    cls_name = cls_name[0].upper() + cls_name[1:]  # capitalize class name

    # write_to_file(base_module, base_cls, new_cls_name)
    if base_mod_name == "object":
        write_py_module(cls_name, base_class_name)
    else:
        write_p3d_module(base_class_name, cls_name)


@obs.on("OnSceneStart")
def on_scene_start():
    """should be called after a new scene is created"""
    wx_main = editor.wx_main
    level_editor = editor.level_editor
    inspector = editor.inspector
    scene_graph = editor.scene_graph
    # resource_tree = editor.resource_browser

    wx_main.freeze()

    # set a default active object for inspector
    inspector.select_inspector(0)
    cube = level_editor.active_scene.render.find("**/cube.fbx")
    cube = cube.getPythonTag(TAG_GAME_OBJECT)
    # inspector.set_object(cube, cube.get_name(), cube.get_properties())

    # scene_graph.ExpandAll()  # expand scene graph
    # resource_tree.schedule_dir_watcher()  # start the project directory watcher
    wx_main.thaw()


@obs.on("OnSceneClean")
def on_scene_clean(scene):
    """is called just before the scene is about to be cleaned"""
    pass


# ---------------------------------------- ** ---------------------------------------- #
# Events related to LevelEditor
@obs.on("ViewportEvent")
def viewport_event(evt_type: str, *args):
    if evt_type == "FrameSelectedNPs":
        align_dir = args[0]
        nps = editor.level_editor.selection.selected_nps
        editor.p3d_app.show_base.ed_camera.frame(nps, align_dir)
    elif evt_type == "ResetView":
        editor.p3d_app.show_base.ed_camera.reset()


@obs.on("EditorEvent")
def viewport_event(evt_type: str, *args):
    if evt_type == "ToggleHotkeysText":
        editor.level_editor.toggle_hot_keys_text()
    elif evt_type == "ReloadEditor":
        reload_editor()
    elif evt_type == "UndoLastCommand":
        undo_last_command()


@obs.on("AlignToEdView")
def align_game_view_to_ed_view(*args):
    ed_cam = editor.p3d_app.show_base.ed_camera
    game_cam = editor.level_editor.active_scene.main_camera
    if game_cam:
        game_cam.setPos(ed_cam.getPos())
        game_cam.setHpr(ed_cam.getHpr())
        game_cam.setY(game_cam, -15)


@obs.on("XFormTask")
def on_xform_task(force_update_all=False):
    """updates properties panel according to currently selected object"""
    if editor.inspector and editor.inspector.has_object():
        editor.inspector.update(force_update_all=force_update_all)


@obs.on("OnAddNPs")
def on_add_nps(nps):
    app = editor.p3d_app
    wx_main = editor.wx_main
    scene_graph = editor.scene_graph
    inspector = editor.inspector
    resource_tree = editor.resource_browser

    wx_main.freeze()
    app.level_editor.deselect_all()
    resource_tree.deselect_all_files()
    app.level_editor.set_selected(nps)

    for np in nps:
        scene_graph.add(np)

    scene_graph.select(nps)
    inspector.layout_auto()
    wx_main.thaw()


@obs.on("OnRemoveNPs")
def on_remove_nps(nps):
    app = editor.p3d_app
    scene_graph = editor.scene_graph
    inspector = editor.inspector

    app.level_editor.deselect_all()
    scene_graph.on_remove(nps)
    inspector.layout_auto()


@obs.on("OnDeselectAllNPs")
def on_deselect_all_nps():
    editor.scene_graph.UnselectAll()
    editor.inspector.layout_auto()


@obs.on("SwitchEdState")
def switch_ed_state(state=None):
    le = editor.level_editor
    wx_main = editor.wx_main

    if state is None:
        ed_state = le.ed_state  # 0 = editor, 1 = game_state
        if ed_state == 0:
            le.switch_state(1)
        elif ed_state == 1:
            le.switch_state(0)
    else:
        ed_state = state
        le.switch_state(ed_state)

    # change graphics
    if le.ed_state == 1:
        wx_main.ply_btn.SetBitmap(wx_main.stop_icon)
        wx_main.file_menu_tb.ToggleTool(wx_main.ply_btn.GetId(), True)
    elif le.ed_state == 0:
        wx_main.ply_btn.SetBitmap(wx_main.play_icon)
        wx_main.file_menu_tb.ToggleTool(wx_main.ply_btn.GetId(), False)

    wx_main.file_menu_tb.Realize()


@obs.on("OnEnableEditorState")
def on_enable_ed_state():
    editor.scene_graph.rebuild()
    editor.scene_graph.UnselectAll()


@obs.on("OnEnableGameState")
def on_enable_game_state():
    editor.scene_graph.UnselectAll()
    editor.console.on_enter_game_state()


@obs.on("ToggleSceneLights")
def toggle_lights(value=None):
    le = editor.level_editor
    wx_main = editor.wx_main

    current_status = le.toggle_scene_lights()

    # change graphics
    if current_status:
        wx_main.lights_toggle_btn.SetBitmap(wx_main.lights_on_icon)
        wx_main.file_menu_tb.ToggleTool(wx_main.lights_toggle_btn.GetId(), True)
    elif not current_status:
        wx_main.lights_toggle_btn.SetBitmap(wx_main.lights_off_icon)
        wx_main.file_menu_tb.ToggleTool(wx_main.lights_toggle_btn.GetId(), False)

    wx_main.file_menu_tb.Refresh()


@obs.on("PluginFailed")
def plugin_execution_failed(plugin):
    editor.level_editor.unregister_editor_plugin(plugin)


@obs.on("CleanUnusedLoadedNPs")
def clean_unused_loaded_nps(nps_to_remove):
    editor.level_editor.remove_nps(nps_to_remove, permanent=True)


@obs.on("EditorReload")
def reload_editor(*args):
    le = editor.level_editor
    wx_main = editor.wx_main
    inspector = editor.inspector
    resource_tree = editor.resource_browser
    scene_graph = editor.scene_graph

    editor.console.on_ed_reload()

    resource_tree.save_state()
    selected_nps = le.selection.selected_nps
    #
    obs.trigger("DeselectAll")

    wx_main.freeze()

    # rebuild resources tree and reload all resources
    resource_tree.create_or_rebuild_tree(le.project.project_path, rebuild_event=True)
    le.register_user_modules(resource_tree.resources["py"])
    le.reload_components(resource_tree.resources["py"])
    le.register_text_files(resource_tree.resources["txt"])
    # ---------------------------------------------------

    scene_graph.rebuild()  # rebuild the scene graph

    # brings things back to their pre-reload state
    resource_tree.reload_state()

    if len(selected_nps) > 0:
        le.set_selected(selected_nps)
        scene_graph.select(selected_nps)

    inspector.layout_auto()  # layout the inspector
    wx_main.thaw()


@obs.on("UndoLastCommand")
def undo_last_command():
    editor.p3d_app.command_manager.undo()


# ---------------------------------------- Wx EVENTs ---------------------------------------- #
@obs.on("SwitchEdViewportStyle")
def switch_ed_viewport_style():
    """toggles between minimized and maximized game viewport"""
    editor.level_editor.switch_ed_viewport_style()


@obs.on("OnResourceTileSelected")
def on_resource_tile_selected(file_path):
    def on_module_selected(module):
        inspector.layout(module, module.name, module.get_properties())

    def on_txt_file_selected(txt_file):
        inspector.set_text(txt_file.text)

    wx_main = editor.wx_main
    le = editor.level_editor
    scene_graph = editor.scene_graph
    inspector = editor.inspector

    # deselect all node-paths
    # ** do not trigger "OnDeselectAllNPs" event, otherwise it
    # will cause the inspector layout event **
    le.deselect_all(trigger_deselect_event=False)
    scene_graph.UnselectAll()

    if le.is_module(file_path):
        on_module_selected(le.get_module(file_path))

    elif le.is_text_file(file_path):
        on_txt_file_selected(le.get_text_file(file_path))

    else:
        inspector.set_text("No inspector defined for this item.")


@obs.on("OnSelUserCommandMenuEntry")
def on_user_cmd(cmd_name):
    # find the user command and execute it
    le = editor.level_editor
    app = editor.p3d_app

    for cmd_name in le.user_commands.keys():
        if cmd_name == cmd_name:
            # get the command
            cmd_data = le.user_commands[cmd_name]
            cmd = cmd_data[0]
            args = cmd_data[1]
            #
            cmd = safe_execute(cmd, *args, return_func_val=True)
            if cmd:
                safe_execute(app.command_manager.do, cmd)


@obs.on("DeselectAll")
def deselect_all():
    le = editor.level_editor
    resource_browser = editor.resource_browser
    # inspector = editor.inspector
    scene_graph = editor.scene_graph

    if len(le.selection.selected_nps) > 0:
        le.deselect_all()

    scene_graph.UnselectAll()
    resource_browser.deselect_all_files()
    # inspector.reset()


@obs.on("PropertyModified")
def property_modified(property_):
    """is called after a wx-property is modified from inspector,
    call any post property modify event here"""
    le = editor.level_editor
    le.update_gizmo()

    # TODO this should be replaced by some kind of property flag
    if property_.ed_property.name in ["Near-Far", "Field Of View", "FilmSize", "Lens Type"]:
        obs.trigger("ShowBaseResize")

        for np in le.selection.selected_nps:
            np.create_properties()
        editor.inspector.mark_dirty()


@obs.on("ShowBaseResize")
def resize_event(*args):
    """emitted when window is resized, can be called manually as well"""
    level_editor = editor.level_editor
    app = editor.p3d_app

    # this event also gets called before initialization of level editor, so make sure it's not None
    if level_editor and app:
        app.show_base.update_aspect_ratio()

        for module in level_editor.user_modules:
            module.on_resize_event()

        level_editor.on_evt_size()
        level_editor.project.game.resize_event()


@obs.on("OnPluginMenuEntrySelected")
def on_plugin_menu_entry_selected(plugin_name):
    print(plugin_name)


@obs.on("OpenSocialMediaLink")
def open_social_media_link(link: str):
    if link == "Patreon":
        webbrowser.open("https://www.patreon.com/PandaEditor_", new=2)

    elif link == "Panda3dDiscourse":
        webbrowser.open("https://discourse.panda3d.org/t/pandaeditor-alpha-release/28408", new=2)

    elif link == "Discord":
        webbrowser.open("https://discord.gg/QU2y6q7G9F", new=2)


@obs.on("CloseApp")
def exit_app(close_wx=True):
    if close_wx:
        editor.wx_main.Close()
    editor.p3d_app.quit()
