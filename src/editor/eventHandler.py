import os.path
import webbrowser
import editor.commands as commands

from commons import ed_logging
from editor.globals import editor
from editor.constants import GAME_STATE
from game.constants import TAG_GAME_OBJECT


def handle_ui_event(*args, **kwargs):
    if not editor.get_ui_evt_handler():
        return None

    return editor.get_ui_evt_handler().handle_event(*args, **kwargs)


class Project_Events:
    @staticmethod
    @editor.observer.on("AppendLibrary")
    def append_library(name: str = None, path: str = None):
        le = editor.level_editor

        if le.get_ed_state() is GAME_STATE:
            print("Exit game mode to append new library!")
            return

        if not path:
            name, path = handle_ui_event("AppendLibrary")
            le.append_library(name, path)
        else:
            if path and os.path.exists(path):
                name = name if name is not None else os.path.basename(path)
                le.append_library(name, path)

    @staticmethod
    @editor.observer.on("BuildProject")
    def build_project():
        print("build project")

    @staticmethod
    @editor.observer.on("CreateNewProject")
    def create_new_project():
        print("create new project")

    @staticmethod
    @editor.observer.on("CreateNewSession")
    def create_new_session():
        le = editor.level_editor

        if le.get_ed_state() is GAME_STATE:
            print("Exit game mode to create a new scene..!")
            return

        if handle_ui_event("CreateNewSession") is False:
            pass
        else:
            le.create_new_scene()

    @staticmethod
    @editor.observer.on("OpenProject")
    def open_project():
        print("open project")

    @staticmethod
    @editor.observer.on("OpenSession")
    def open_session():
        print("open session")

    # @staticmethod
    # @editor.observer.on("OnSceneStart")
    # def on_create_new_scene(scene):
    #     """should be called after a new scene is created"""
    #     editor.inspector.select_tab(0)

    @staticmethod
    @editor.observer.on("OnSceneStart")
    def on_scene_start():
        """should be called after a new scene is created"""
        editor.inspector.select_tab(0)

    @staticmethod
    @editor.observer.on("OnSceneClean")
    def on_scene_clean():
        """is called just before the scene is about to be cleaned"""
        pass

    @staticmethod
    @editor.observer.on("RemoveLibrary")
    def remove_library(name: str):
        editor.level_editor.remove_library(name)
        #handle_ui_event("RemoveLibrary")
        #print("remove_library")

    @staticmethod
    @editor.observer.on("SaveSession")
    def save_session():
        print("save session")

    @staticmethod
    @editor.observer.on("SaveSessionAs")
    def save_session_as(*args):
        print("save session as")


class ViewportEvents:
    @staticmethod
    @editor.observer.on("AlignToEdView")
    def align_game_view_to_ed_view():
        ed_cam = editor.p3D_app.show_base.ed_camera
        game_cam = editor.level_editor.active_scene.main_camera
        if game_cam:
            game_cam.setPos(ed_cam.getPos())
            game_cam.setHpr(ed_cam.getHpr())
            game_cam.setY(game_cam, -15)

    @staticmethod
    @editor.observer.on("FrameSelectedNPs")
    def frame_sel_nps(*args):
        nps = editor.level_editor.selection.selected_nps
        editor.p3D_app.show_base.ed_camera.frame(nps, args[0])

    @staticmethod
    @editor.observer.on("ResetView")
    def reset_view():
        editor.p3D_app.show_base.ed_camera.reset()


class EditorEvents:
    @staticmethod
    @editor.observer.on("AddObject")
    def add_object(path):
        editor.command_mgr.do(commands.ObjectAdd(path))
        nps = editor.level_editor.selection.selected_nps
        handle_ui_event("AddObject", nps)

    @staticmethod
    @editor.observer.on("AddCamera")
    def add_camera():
        editor.command_mgr.do(commands.AddCamera())
        nps = editor.level_editor.selection.selected_nps
        handle_ui_event("AddObject", nps)

    @staticmethod
    @editor.observer.on("AddLight")
    def add_light(light):
        editor.command_mgr.do(commands.AddLight(light))
        nps = editor.level_editor.selection.selected_nps
        handle_ui_event("AddObject", nps)

    @staticmethod
    @editor.observer.on("CreateAsset")
    def create_asset(asset_type, path):
        def indent_file(_file, spaces):
            for i in range(spaces):
                _file.write(" ")  # add indentation by adding empty spaces

        def write_p3d_module(base_class, new_class_name):
            with open(path, "w") as file_:
                file_.write("import math\n")
                file_.write("import panda3d.core as p3d_core\n")
                file_.write("from game.resources import {0}\n\n\n".format(base_class))

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

    @staticmethod
    @editor.observer.on("CleanUnusedLoadedNPs")
    def clean_unused_loaded_nps(nps_to_remove):
        editor.level_editor.remove_nps(nps_to_remove, permanent=True)

    @staticmethod
    @editor.observer.on("DeselectAll")
    def deselect_all():
        editor.level_editor.deselect_all()
        handle_ui_event("DeselectAll")

    @staticmethod
    @editor.observer.on("OnSelUserCommandMenuEntry")
    def execute_user_command(cmd_name):
        # find the user command and execute it
        le = editor.level_editor
        app = editor.p3D_app

        for cmd_name_ in le.user_commands.keys():
            if cmd_name_ == cmd_name:
                # get the command
                cmd_data = le.user_commands[cmd_name]
                cmd_class = cmd_data[0]  # the command class
                args = cmd_data[1]  # args to constructor
                #
                cmd = None
                try:
                    cmd = cmd_class(*args)  # create instance of command class
                except Exception as exception:
                    ed_logging.log_exception(exception)

                if cmd:  # execute the command
                    app.command_manager.do(cmd)

    @staticmethod
    @editor.observer.on("OnAddNPs")
    def on_add_nps(nps):
        handle_ui_event("AddObject", nps)

    @staticmethod
    @editor.observer.on("OnEnableEditorState")
    def on_enable_ed_state():
        handle_ui_event("OnEnableEditorState")

    @staticmethod
    @editor.observer.on("OnEnableGameState")
    def on_enable_game_state():
        handle_ui_event("OnEnableGameState")

    @staticmethod
    @editor.observer.on("OnRemoveNPs")
    def on_remove_nps(nps):
        handle_ui_event("OnRemoveNPs", nps)

    @staticmethod
    @editor.observer.on("on_window_event")
    def resize_event():
        """this event is fired when window is resized, can be called manually as well"""
        # this event can also get called when window is created so make sure editor.globals is initialized.
        if editor.level_editor and editor.p3D_app:
            editor.p3D_app.editor_workspace.update_aspect_ratio()

            for module in editor.level_editor.user_modules:
                module.on_resize_event()

            editor.level_editor.project.game.resize_event()

    @staticmethod
    @editor.observer.on("PropertyModified")
    def property_modified(property_):
        """is called after a wx-property is modified from inspector,
        call any post property modify event here"""
        le = editor.level_editor
        le.update_gizmo()
        # print("property modified")
        # TODO this should be replaced by some kind of property flag
        if property_.ed_property.name in ["Lens Type"]:
            editor.observer.trigger("on_window_event")

            for np in le.selection.selected_nps:
                np.getPythonTag(TAG_GAME_OBJECT).create_properties()

            # TODO
            editor.inspector.mark_dirty()

    @staticmethod
    @editor.observer.on("PluginFailed")
    def plugin_execution_failed(plugin):
        editor.level_editor.unregister_editor_plugin(plugin)

    @staticmethod
    @editor.observer.on("EditorReload")
    def reload_editor():
        if not editor.level_editor.can_reload():
            return

        project_path = editor.level_editor.project.project_path
        selected_nps = editor.level_editor.selection.selected_nps
        #
        resources = handle_ui_event("EditorReload", project_path, selected_nps)
        #
        editor.level_editor.register_user_modules(resources["py"])
        editor.level_editor.reload_components(resources["py"])
        editor.level_editor.register_text_files(resources["txt"])

    @staticmethod
    @editor.observer.on("ResourceTileSelected")
    def resource_tile_selected(file_path):
        pass

    @staticmethod
    @editor.observer.on("SelectPlugin")
    def select_plugin(plugin_name):
        print(plugin_name)

    @staticmethod
    @editor.observer.on("SwitchEdState")
    def switch_ed_state(state: int = None):
        le = editor.level_editor

        if state is None:
            ed_state = le.get_ed_state()  # 0 = editor, 1 = game_state
            if ed_state == 0:
                le.switch_state(1)
            elif ed_state == 1:
                le.switch_state(0)
        else:
            ed_state = state
            le.switch_state(ed_state)

        handle_ui_event("SwitchEdState", le.get_ed_state())

    @staticmethod
    @editor.observer.on("SwitchEdViewportStyle")
    def switch_ed_viewport_style():
        """toggles between minimized and maximized game viewport"""
        editor.level_editor.switch_ed_viewport_style()

    @staticmethod
    @editor.observer.on("ToggleHotkeysText")
    def toggle_hot_keys_text():
        editor.level_editor.toggle_hot_keys_text()
       
    @staticmethod
    @editor.observer.on("ToggleGizmos")
    def toggle_gizmos():
        editor.level_editor.set_active_gizmo("None")
        
    @staticmethod
    @editor.observer.on("ToggleSceneLights")
    def toggle_lights():
        toggle_status = editor.level_editor.toggle_scene_lights()
        handle_ui_event("ToggleSceneLights", toggle_status)

    @staticmethod
    @editor.observer.on("UndoLastCommand")
    def undo_last_command():
        editor.p3D_app.command_manager.undo()

    @staticmethod
    @editor.observer.on("XFormTask")
    def xform_task(force_update_all=False):
        handle_ui_event("XFormTask", force_update_all)


@editor.observer.on("OpenSocialMediaLink")
def open_social_media_link(link: str):
    if link == "Patreon":
        webbrowser.open("https://www.patreon.com/PandaEditor_", new=2)

    elif link == "Panda3dDiscourse":
        webbrowser.open("https://discourse.panda3d.org/t/pandaeditor-alpha-release/28408", new=2)

    elif link == "Discord":
        webbrowser.open("https://discord.gg/QU2y6q7G9F", new=2)


@editor.observer.on("CloseApp")
def exit_app(close_wx=True):
    if close_wx:
        editor.wx_main.Close()
    editor.p3D_app.quit()
