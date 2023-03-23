import sys
import traceback
import editor.core as ed_core
import editor.nodes as ed_nodepaths
import editor.gizmos as gizmos
import editor.constants as constants
import editor.commands as commands
import editor.utils as ed_utils

from datetime import date

from panda3d.core import NodePath, PointLight, Spotlight, DirectionalLight, AmbientLight, get_model_path, \
    LVecBase3f, Material, LColor, Camera
from direct.showbase.DirectObject import DirectObject
from direct.showbase.Loader import Loader
from direct.gui.OnscreenText import TextNode

from editor.project import Project
from editor.selection import Selection
from editor.pluginManager import PluginsManager
from editor.editorSettings import EditorSettings


LIGHT_MAP = {constants.POINT_LIGHT: (PointLight, ed_nodepaths.EdPointLight, constants.POINT_LIGHT_MODEL),
             constants.SPOT_LIGHT: (Spotlight, ed_nodepaths.EdSpotLight, constants.SPOT_LIGHT_MODEL),
             constants.DIRECTIONAL_LIGHT: (DirectionalLight, ed_nodepaths.EdDirectionalLight,
                                           constants.DIR_LIGHT_MODEL),
             constants.AMBIENT_LIGHT: (AmbientLight, ed_nodepaths.EdAmbientLight,
                                       constants.AMBIENT_LIGHT_MODEL)}

NODE_TYPE_MAP = {constants.DIRECTIONAL_LIGHT: ed_nodepaths.EdDirectionalLight,
                 constants.POINT_LIGHT: ed_nodepaths.EdPointLight,
                 constants.SPOT_LIGHT: ed_nodepaths.EdSpotLight,
                 constants.AMBIENT_LIGHT: ed_nodepaths.EdAmbientLight,
                 constants.CAMERA_NODEPATH: ed_nodepaths.CameraNodePath,
                 constants.NODEPATH: ed_nodepaths.ModelNodePath,
                 constants.ACTOR_NODEPATH: ed_nodepaths.ActorNodePath}

POS_GIZMO = "PosGizmo"
ROT_GIZMO = "RotGizmo"
SCALE_GIZMO = "ScaleGizmo"


class LevelEditor(DirectObject):
    def __init__(self, panda_app, *args, **kwargs):
        """Actual Level / scene editor all editor systems should be initialized from here"""

        DirectObject.__init__(self)
        self.__app = panda_app

        self.__project = Project(panda_app)
        self.__editor_settings = EditorSettings(self)
        self.__plugins_manager = PluginsManager()

        self.__active_scene = None

        # gizmos, grid, selection
        self.__grid_np = None
        self.__selection = None
        self.__gizmo = False
        self.__gizmo_mgr_root_np = None
        self.__gizmo_mgr = None
        self.__active_gizmo = None  # position, rotation, or scale

        '''grid, selection and gizmos'''
        self.create_grid(200, 40, 5)
        self.setup_selection_system()
        self.setup_gizmo_manager()

        # create event map for various keyboard events and bind them
        self.__key_event_map = {"q": (self.set_active_gizmo, "None"),
                                "w": (self.set_active_gizmo, POS_GIZMO),
                                "e": (self.set_active_gizmo, ROT_GIZMO),
                                "r": (self.set_active_gizmo, SCALE_GIZMO),
                                "space": (self.toggle_gizmo_local, None),
                                "+": (self.__gizmo_mgr.SetSize, 2),
                                "-": (self.__gizmo_mgr.SetSize, 0.5),
                                "control-d": (self.on_duplicate_nps, None),
                                "x": (
                                    lambda: self.__app.command_manager.do(
                                        commands.RemoveObjects(self.__selection.selected_nps)), None),
                                "control-z": (self.__app.command_manager.undo, None),

                                "mouse1": (self.on_mouse1_down, [False]),
                                "mouse2": (self.on_mouse2_down, None),

                                "mouse1-up": (self.on_mouse1_up, None),
                                "mouse2-up": (self.on_mouse2_up, None),

                                "shift-mouse1": (self.on_mouse1_down, [True]),
                                "control-mouse1": (self.on_mouse1_down, None)
                                }

        self.__scene_lights_on = False  # scene lights are on or off ?
        self.__ed_state = constants.EDITOR_STATE  # is current state editor or game state ?

        self.__game_viewport_maximized = False
        # self.current_mouse_mode = None

        # editor update task
        # self.update_task = None
        self.__inspector_update_interval = 0
        self.__inspector_update_delay = 0.1  # delay time before updating inspector panel

        # available loaded resources
        # TODO replace this with ResourceHandler
        self.__loader = Loader(self.__app.show_base)
        self.__user_modules = {}
        self.__ed_plugins = {}
        self.__text_files = {}
        # ---------------------------------------

        self.__user_commands = {}

        self.__on_screen_text = self.create_on_screen_text()

        self.bind_key_events()

        self.__app.command_manager.clear()
        get_model_path().clear()

    def update(self, task):
        """this method should be called ever frame in editor_state and game_state"""

        # update the inspector after inspector update delay
        if task.time > self.__inspector_update_interval:
            self.__app.observer.trigger("XFormTask")
            self.__inspector_update_interval += self.__inspector_update_delay

        # --------------------------------------------------------------

        # TODO fix this to update conditionally
        self.update_gizmo()  # this has to be updated regularly otherwise gizmo movement appears jagged

    def create_on_screen_text(self):
        text = "__HotKeys__\n" \
               "F: Frame selected node-paths\n" \
               "ctrl-D: Duplicate selected node-paths\n" \
               "X: Remove selected\n" \
               "Q: Show/Hide gizmos\n" \
               "W, E, R: Pos, rot and scale gizmo respectively\n" \
               "Space: Toggle gizmo local or world-space\n" \
               "ctrl-G: Align game camera to viewport\n" \
               "ctrl-Z: Undo\n" \
               "shift-R: Reset viewport camera\n" \
               "ctrl-R: Reload editor"

        on_screen_text = TextNode("OnScreenText")
        on_screen_text.setText(text)
        on_screen_text.setAlign(TextNode.ALeft)
        on_screen_text.setCardColor(0.4, 0.4, 0.4, 1)
        on_screen_text.setCardAsMargin(0, 0, 0, 0)
        on_screen_text.setCardDecal(True)
        text_np = self.__app.show_base.ed_aspect2d.attachNewNode(on_screen_text)
        text_np.setScale(0.07)
        return text_np

    def on_evt_size(self):
        aspect_ratio = self.__app.show_base.ed_camera.node().getLens().getAspectRatio()
        self.__on_screen_text.setPos(-aspect_ratio, 0, 1 - 0.055)

    def toggle_hot_keys_text(self):
        if self.__on_screen_text.isHidden():
            self.__on_screen_text.show()
        else:
            self.__on_screen_text.hide()

    # --------------------------------Scene operations-----------------------------#
    def create_new_project(self, name, path):
        if self.__ed_state == constants.GAME_STATE:
            print("[Editor] Cannot create new project in game mode")
            return

        self.__project.set_project(name, path)
        # self.create_new_scene(initial=True)

    def create_new_scene(self, initial: bool = False):
        """creates and set up a default scene
        initial: Is this the first default scene when a project is created ?"""

        if self.__active_scene:
            self.clean_active_scene()

        # create a new scene
        self.__active_scene = self.__project.game.create_new_scene("default")

        # get the wx-scene graph panel and set it up
        self.__app.wx_main.scene_graph_panel.scene_graph.init(self.__active_scene.render)

        # update active active
        self.__selection.set_render(self.__active_scene.render)

        # finally, set up the default scene
        self.setup_default_scene()

    def setup_default_scene(self):
        # add a default sunlight
        self.__app.command_manager.do(commands.AddLight("__DirectionalLight__"), select=False)
        light_np = self.__active_scene.render.find("**/DirectionalLight")
        light_np = light_np.getPythonTag(constants.TAG_GAME_OBJECT)
        light_np.setPos(400, 200, 350)
        light_np.setHpr(LVecBase3f(115, -25, 0))
        light_np.set_color(LColor(1, 0.95, 0.5, 255))

        # add a default player camera
        self.__app.command_manager.do(commands.AddCamera())
        cam = self.__active_scene.render.find("**/Camera").getNetPythonTag(constants.TAG_GAME_OBJECT)
        cam.setPos(-239.722, 336.966, 216.269)
        cam.setHpr(LVecBase3f(-145.0, -20, 0))

        # add a default cube
        self.__app.command_manager.do(commands.ObjectAdd(constants.CUBE_PATH))
        obj = self.__active_scene.render.find("**/cube.fbx")
        obj.setScale(0.5)

        self.set_active_gizmo(POS_GIZMO)

        self.__app.observer.trigger("OnSceneStart")
        self.__app.observer.trigger("ToggleSceneLights")

    def clean_active_scene(self):
        self.__app.observer.trigger("OnSceneClean", None)

        self.__scene_lights_on = False
        self.__selection.deselect_all()
        self.__active_scene.render.remove_node()

    # -------------------------------Resources section-----------------------------#
    # load and register resources
    # TODO replace this with ResourceHandler

    def register_user_modules(self, modules_paths):
        """Imports, instantiates, reload and registers RuntimeModules and EditorPlugins
        modules_paths = all python modules in project"""

        def init_runtime_module(name, runtime_module, path_):
            instance = runtime_module(
                name=name,
                show_base=self.__project.game.show_base,
                win=self.__project.game.win,
                dr=self.__project.game.dr,
                dr2d=self.__project.game.dr_2D,
                mouse_watcher_node=self.__project.game.mouse_watcher_node,
                render=self.__active_scene.render,
                render2d=self.__active_scene.render_2D,
                aspect2d=self.__active_scene.aspect_2D,
                game=self.__project.game,
                path=path_
            )
            return instance

        def init_ed_plugin(name, plugin, path_):
            instance = plugin(
                name=name,
                win=self.__app.show_base.main_win,
                dr=self.__app.show_base.edDr,
                dr2d=self.__app.show_base.edDr2d,
                mouse_watcher_node=self.__app.show_base.ed_mouse_watcher_node,
                render=self.__app.show_base.render,
                render2d=None,
                aspect2d=self.__app.show_base.ed_aspect2d,
                level_editor=self,
                path=path_,
                command_manager=self.__app.command_manager
            )
            return instance

        if len(modules_paths) == 0:
            return True

        imported_modules = ed_utils.safe_execute(ed_utils.Importer.import_modules,
                                                 modules_paths,
                                                 return_func_val=True)
        if imported_modules is None:
            return

        saved_data = {}  # cls_name: user_mod.saved_data
        for key in self.__user_modules.keys():
            user_mod = self.__user_modules[key]
            #
            cls_instance = user_mod.class_instance
            cls_instance.ignore_all()
            #
            user_mod.save_data()
            saved_data[key] = user_mod.saved_data

        self.__app.show_base.clear_ed_aspect_2d()
        self.__user_modules.clear()
        self.unregister_editor_plugins()
        self.unregister_user_commands()

        game_modules = {}  # save runtime modules here
        ed_plugins = []  # save editor plugins here

        for path, mod, cls_name in imported_modules:
            if hasattr(mod, cls_name):
                cls = getattr(mod, cls_name)
                obj_type = None

                try:
                    obj_type = cls.__mro__[1]
                except AttributeError:
                    pass

                # make sure to load only EditorPlugin and RuntimeModule object types
                xx = [ed_core.runtimeModule.RuntimeModule, ed_core.editorPlugin.EditorPlugin]
                # only allow objects of type RuntimeModules and EditorPlugins to pass through
                if obj_type in xx:
                    pass
                elif obj_type is ed_core.Component:
                    continue
                else:
                    continue

                # instantiate the class and catch any errors from its init method
                cls_instance = None
                try:
                    if obj_type == ed_core.runtimeModule.RuntimeModule:
                        cls_instance = init_runtime_module(cls_name, cls, path)
                    #
                    if obj_type == ed_core.editorPlugin.EditorPlugin:
                        cls_instance = init_ed_plugin(cls_name, cls, path)

                    module_type = cls_instance.module_type

                except Exception as e:
                    tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
                    for x in tb_str:
                        print(x)
                    print("{0} Unable to load user module {1}".format(date.today(), cls_name))
                    continue

                # create a new user module
                module = ed_core.UserModule(path, cls_instance, cls_instance.sort)
                self.__user_modules[path] = module

                # try restore data
                if saved_data.__contains__(path):
                    # print("[LevelEditor] Attempting to restore data for {0}".format(cls_name))
                    self.__user_modules[path].saved_data = saved_data[path]
                    self.__user_modules[path].reload_data()

                if module_type == constants.RuntimeModule:
                    game_modules[path] = self.__user_modules[path]
                    print("[{0}] Loaded RuntimeUserModule {1}.".format(date.today(), cls_name))

                elif module_type == constants.EditorPlugin:
                    # it's an editor plugin
                    ed_plugin = self.__user_modules[path].class_instance
                    ed_plugins.append(ed_plugin)

        # finally, register editor tools
        self.register_editor_plugins(ed_plugins)
        self.register_user_commands()
        #
        # self.project.game.runtime_modules = game_modules
        self.register_runtime_modules(game_modules)
        #
        return True

    def register_component(self, paths: list, nps=None):
        imported = []
        for path in paths:
            result = ed_utils.safe_execute(ed_utils.Importer.import_module, path, return_func_val=True)
            if result is not None:
                imported.append(result)

        registered = []

        # make sure type is Component
        for path, mod, cls_name in imported:
            if hasattr(mod, cls_name):
                cls = getattr(mod, cls_name)
                obj_type = None

                try:
                    obj_type = cls.__mro__[1]
                except AttributeError:
                    pass

                if obj_type is ed_core.Component:
                    pass
                else:
                    continue

                nps_ = nps if nps else self.__selection.selected_nps
                for np in nps_:
                    # initialize
                    cls_instance = ed_utils.try_execute_1(self.initialize_component, cls_name, cls, path, np)
                    # cls_instance = self.initialize_component(cls_name, cls, path, np)
                    if cls_instance is None:
                        continue
                    # wrap into a UserModule object
                    module = ed_core.UserModule(path, cls_instance, cls_instance.sort)
                    # and attach it to NodePath
                    np.attach_component(path, module)
                    #
                    registered.append(module)

        return registered

    def register_text_files(self, paths):
        self.__text_files.clear()
        for path in paths:
            if sys.platform == "win32" or sys.platform == "win64":
                name = path.split("\\")[-1]
                name = name.split(".")[0]
            else:
                name = path.split("/")[-1]
                name = name.split(".")[0]

            self.__text_files[path] = ed_core.TextFile(path)
            print("[{0}] Loaded TextFile {1}.".format(date.today(), name))

    def register_runtime_modules(self, runtime_modules):
        self.__project.game.set_runtime_modules(runtime_modules)

    def register_editor_plugins(self, plugins: list):
        """load all editor plugins"""
        for plugin in plugins:
            self.__ed_plugins[plugin.name] = plugin
            res = plugin.start(sort=1)
            if res:
                self.__app.wx_main.menu_bar.add_ed_plugin_menu(plugin.name)

    def unregister_editor_plugins(self):
        """unloads all editor plugins"""
        for key in self.__ed_plugins.keys():
            self.__ed_plugins[key].stop()

        self.__ed_plugins.clear()
        self.__app.wx_main.menu_bar.clear_ed_plugin_menus()

    def unregister_editor_plugin(self, plugin):
        if plugin.name in self.__ed_plugins.keys():
            self.unregister_user_commands()
            del self.__ed_plugins[plugin.name]
            del self.__user_modules[plugin.path]
            print("[LevelEditor] Unloading Editor Plugin: {0}".format(plugin.name))

        self.__app.wx_main.menu_bar.clear_ed_plugin_menus()  # clear all plugin menu bar entries
        self.__app.wx_main.menu_bar.clear_user_command_menus()  # clear all user commands menu bar entries

        # add the plugin menu bar entries for remaining plugins
        for plugin in self.__ed_plugins.keys():
            self.__app.p3d_app.wx_main.menu_bar.add_ed_plugin_menu(plugin.name)

        # add the user commands menu bar entries for remaining plugins
        self.register_user_commands()

    def register_user_commands(self):
        for plugin_name in self.__ed_plugins.keys():
            plugin = self.__ed_plugins[plugin_name]
            for cmd_name in plugin.commands.keys():
                self.__user_commands[cmd_name] = plugin.commands[cmd_name]
                self.__app.wx_main.menu_bar.add_user_command_menu(cmd_name)

    def unregister_user_commands(self):
        self.__user_commands.clear()
        self.__app.wx_main.menu_bar.clear_user_command_menus()  # clear menu bar entries for user commands

    def initialize_component(self, name, component, path, np):
        instance = component(
            name=name,
            show_base=self.__project.game.show_base,
            win=self.__project.game.win,
            dr=self.__project.game.dr,
            dr2d=self.__project.game.dr_2D,
            mouse_watcher_node=self.__project.game.mouse_watcher_node,
            render=self.__active_scene.render,
            render2d=self.__active_scene.render_2D,
            aspect2d=self.__active_scene.aspect_2D,
            game=self.__project.game,
            path=path,
            np=np
        )
        return instance

    def reload_components(self, paths: list):
        saved_components = {}  # np: [components_paths]

        # get all existing components and save them
        existing_components = self.__project.game.components  # game.component return as a dict (np: components)
        for np in existing_components.keys():
            # ---------------------------------
            for comp in existing_components[np]:
                comp.save_data()
                comp.class_instance.ignore_all()
                #
                if comp.path not in paths:
                    continue
                #
                if not saved_components.__contains__(np):
                    saved_components[np] = []
                #
                saved_components[np].append(comp)
            # ---------------------------------
            np.clear_components()

        # now reload the saved_components
        for np in saved_components.keys():
            # get all component paths for this np
            new_comp = None
            for comp in saved_components[np]:
                result = self.register_component(paths=[comp.path], nps=[np])  # register again
                if len(result) == 0:  # meaning registration failed
                    # keep using the component in existing state
                    np.attach_component(comp.path, comp)
                    new_comp = comp
                    # and set the script/component status to error to inform user about it
                    comp.class_instance.set_status(constants.SCRIPT_STATUS_ERROR)
                else:
                    new_comp = result[0]

            # finally, reload saved data
            for comp in saved_components[np]:
                if comp.path == new_comp.path:
                    saved_data = comp.saved_data
                    new_comp.saved_data = saved_data
                    new_comp.reload_data()

    def get_module(self, file_path):
        """returns a user module by path"""
        if file_path in self.__user_modules.keys():
            return self.__user_modules[file_path].class_instance
        return None

    def get_text_file(self, file_name):
        if self.__text_files.__contains__(file_name):
            return self.__text_files[file_name]
        return None

    def is_module(self, file_path):
        """returns a user module by path"""
        if file_path in self.__user_modules.keys():
            return True
        return False

    def is_text_file(self, name):
        if self.__text_files.__contains__(name):
            return True
        return False

    @property
    def active_scene(self):
        return self.__active_scene

    @property
    def editor_settings(self):
        return self.__editor_settings

    @property
    def grid_np(self):
        return self.__grid_np

    @property
    def selection(self):
        return self.__selection

    @property
    def project(self):
        return self.__project

    @property
    def user_modules(self):
        user_modules = []
        for key in self.__user_modules.keys():
            user_modules.append(self.__user_modules[key].class_instance)
        return user_modules

    @property
    def user_commands(self):
        return self.__user_commands

    # ------------------------------Level editor section ----------------------------- #

    def setup_selection_system(self):
        self.__selection = Selection(
            camera=self.__app.show_base.ed_camera,
            render=self.__app.show_base.edRender,
            render2d=self.__app.show_base.edRender2d,
            win=self.__app.show_base.main_win,
            mouseWatcherNode=self.__app.show_base.ed_mouse_watcher_node,
        )

    def create_grid(self, size, grid_step, sub_divisions):
        # grid_np = self.app.show_base.edRender.find("AxisGrid")
        if self.__grid_np:
            self.__grid_np.clearPythonTag("AxisGridNP")
            self.__grid_np.remove_node()

        grid_np = ed_core.ThreeAxisGrid()
        grid_np.setPythonTag(grid_np, "AxisGridNP")
        grid_np.create(size, grid_step, sub_divisions)
        grid_np.reparent_to(self.__app.show_base.edRender)
        grid_np.show(constants.ED_GEO_MASK)
        grid_np.hide(constants.GAME_GEO_MASK)
        self.__grid_np = grid_np

    def setup_gizmo_manager(self):
        """Create gizmo manager."""
        self.__gizmo_mgr_root_np = NodePath("Gizmos")
        self.__gizmo_mgr_root_np.reparent_to(self.__app.show_base.edRender)

        kwargs = {
            "camera": self.__app.show_base.ed_camera,
            "render": self.__gizmo_mgr_root_np,
            "root2d": self.__app.show_base.edRender2d,
            "win": self.__app.show_base.main_win,
            "mouseWatcherNode": self.__app.show_base.ed_mouse_watcher_node,
        }

        self.__gizmo_mgr = gizmos.Manager(**kwargs)
        self.__gizmo_mgr.AddGizmo(gizmos.Translation(POS_GIZMO, **kwargs))
        self.__gizmo_mgr.AddGizmo(gizmos.Rotation(ROT_GIZMO, **kwargs))
        self.__gizmo_mgr.AddGizmo(gizmos.Scale(SCALE_GIZMO, **kwargs))

        for key in self.__gizmo_mgr._gizmos.keys():
            gizmo = self.__gizmo_mgr._gizmos[key]
            gizmo.hide(constants.GAME_GEO_MASK)

    def start_transform(self):
        self.__selection.previous_matrices.clear()
        for np in self.__selection.selected_nps:
            self.__selection.previous_matrices[np] = np.get_transform()

    def stop_transform(self):
        if len(self.__selection.previous_matrices) > 0:
            cmd = commands.TransformNPs(self.__selection.previous_matrices)
            self.__app.command_manager.do(cmd)

    def set_active_gizmo(self, gizmo):
        self.__active_gizmo = gizmo
        self.__gizmo_mgr.SetActiveGizmo(gizmo)

    def set_gizmo_local(self, val):
        self.__gizmo_mgr.SetLocal(val)

    def set_selected(self, selections: list):
        if len(selections) > 0:
            self.__selection.set_selected(selections)
            self.update_gizmo()

    def toggle_gizmo_local(self, *args):
        self.__gizmo_mgr.ToggleLocal()

    def update_gizmo(self):
        if self.__active_gizmo is not None:
            nps = self.__selection.selected_nps
            self.__gizmo_mgr.AttachNodePaths(nps)
            self.__gizmo_mgr.RefreshActiveGizmo()

    def bind_key_events(self):
        for key in self.__key_event_map.keys():
            func = self.__key_event_map[key][0]
            args = self.__key_event_map[key][1]

            if args is None:
                self.accept(key, func)
            else:
                self.accept(key, func, [args])

        # self.app.show_base.ed_camera.disabled = False

    def unbind_key_events(self):
        # for key in self.key_event_map.keys():
        #     self.ignore(key)
        # self.app.show_base.ed_camera.disabled = True
        pass

    def on_mouse1_down(self, shift):
        if not self.__gizmo_mgr.IsDragging() and ed_core.MOUSE_ALT not in self.__app.show_base.ed_camera.mouse.modifiers:
            self.__selection.start_drag_select(shift[0])

        elif self.__gizmo_mgr.IsDragging():
            self.start_transform()

    def on_mouse1_up(self):
        if self.__selection.marquee.IsRunning():
            last_selections = [np for np in self.__selection.selected_nps]
            nps = self.__selection.stop_drag_select()

            # select nps and start transform
            if len(nps) > 0:
                self.__app.command_manager.do(commands.SelectObjects(nps, last_selections))
            else:
                self.deselect_all()

        elif self.__gizmo_mgr.IsDragging():
            self.stop_transform()

    def on_mouse2_down(self):
        pass

    def on_mouse2_up(self):
        pass

    def deselect_all(self, trigger_deselect_event=True):
        self.__selection.deselect_all()
        self.update_gizmo()
        if trigger_deselect_event:
            self.__app.observer.trigger("OnDeselectAllNPs")

    def deselect_nps(self, nps):
        pass

    def switch_state(self, state):
        if state == constants.GAME_STATE:
            self.enable_game_state()

        elif state == constants.EDITOR_STATE:
            self.enable_editor_state()

        else:
            print("[LevelEditor] Undefined editor state {0}".format(state))

    def enable_editor_state(self):
        # print("[LevelEditor] Editor state enabled.")

        self.__ed_state = constants.EDITOR_STATE
        self.__project.game.stop()
        self.deselect_all()  # call to deselect all, triggers OnDeselectAllNps event which properly handles
        # UI updates (inspector, scene graph etc.)
        self.__app.command_manager.clear()

        self.update_game_view_port_style()

        # -----------------------------------------------
        # clear the runtime scene graph
        for np in self.__active_scene.render.get_children():
            self.traverse_scene_graph(np,
                                      light_func=self.__active_scene.render.clear_light if self.__scene_lights_on else None)
            np.remove_node()

        self.__active_scene.clear_cam()

        # restore original saved scene graph
        for np in self.hidden_np.getChildren():
            np.reparent_to(self.__active_scene.render)
            self.traverse_scene_graph(np,
                                      cam_func=self.__active_scene.set_active_camera,
                                      light_func=self.__active_scene.render.set_light if self.__scene_lights_on else None)

        self.hidden_np.remove_node()
        self.hidden_np = None

        self.__app.observer.trigger("OnEnableEditorState")  # for any cleanup operations

    def enable_game_state(self):
        # print("[LevelEditor] Game state enabled.")

        self.__ed_state = constants.GAME_STATE
        self.deselect_all()  # call to deselect all, triggers OnDeselectAllNps event which properly handles
        # UI updates (inspector, scene graph etc.)
        self.__app.command_manager.clear()

        # saves current active scene into a hidden np
        # duplicate current active scene node-path
        self.hidden_np = NodePath("Hidden")
        self.hidden_np = self.__active_scene.render.copy_to(self.hidden_np)
        self.traverse_scene_graph(self.hidden_np, recreate=True)

        self.update_game_view_port_style()

        self.__app.observer.trigger("OnEnableGameState")
        self.__app.observer.trigger("ResizeEvent")
        self.__project.game.start()

    @staticmethod
    def add_children(np, path):
        if len(np.getChildren()) > 0:
            for child in np.getChildren():
                if not type(child) == NodePath:
                    continue

                # print("child: {0} type: {1}".format(child, type(child)))
                child = ed_nodepaths.ModelNodePath(child, path=path)
                child.setColor(LColor(1, 1, 1, 1))
                child.setPythonTag(constants.TAG_GAME_OBJECT, child)
                if child.get_name() == "":
                    child.set_name("NoName")
                LevelEditor.add_children(child, path)

    def load_model(self, path):
        """loads a 3d model from path """

        np = ed_utils.safe_execute(self.__loader.loadModel, path, return_func_val=True)
        if not np:
            return

        np = ed_nodepaths.ModelNodePath(np, path=path)
        np.setColor(LColor(1, 1, 1, 1))
        np.setPythonTag(constants.TAG_GAME_OBJECT, np)

        LevelEditor.add_children(np, path)

        np.reparent_to(self.__active_scene.render)
        self.__app.observer.trigger("OnAddNPs", [np])
        self.set_selected([np])
        return np

    def add_actor(self, path):
        try:
            actor = ed_nodepaths.ActorNodePath(path, tag=constants.TAG_GAME_OBJECT)
        except Exception as e:
            print(e)
            return

        LevelEditor.add_children(actor, path)
        actor.reparentTo(self.__active_scene.render)

        self.__app.observer.trigger("OnAddNPs", [actor])
        self.set_selected([actor])

        return actor

    def add_camera(self):
        # create a panda3d camera
        np = NodePath(Camera("CameraNodePath"))

        # and wrap it into editor camera
        cam_np = ed_nodepaths.CameraNodePath(np=np, path="")
        cam_np.set_name("Camera")
        cam_np.node().setCameraMask(constants.GAME_GEO_MASK)
        cam_np.setPythonTag(constants.TAG_GAME_OBJECT, cam_np)
        cam_np.reparent_to(self.__active_scene.render)
        cam_np.setLightOff()

        # create a handle for visual representation in editor mode
        cam_handle = self.__loader.loadModel(constants.CAMERA_MODEL)
        cam_handle.show(constants.ED_GEO_MASK)
        cam_handle.hide(constants.GAME_GEO_MASK)
        cam_handle.reparent_to(cam_np)
        cam_handle.setScale(12)

        if not self.__active_scene.main_camera:
            self.__active_scene.set_active_camera(cam_np)

        self.__app.observer.trigger("OnAddNPs", [cam_np])
        return cam_np

    def add_object(self, path):
        np = self.__loader.loadModel(path, noCache=True)
        np.set_scale(0.5)

        # fix this name otherwise folder name also gets included
        name = np.get_name()
        name = name.split("\\")[-1]
        np.set_name(name)
        # ------------------------------------------------------

        np = ed_nodepaths.ModelNodePath(np=np, path=path)
        np.reparent_to(self.__active_scene.render)
        np.setPythonTag(constants.TAG_GAME_OBJECT, np)

        LevelEditor.add_children(np, path)

        # setup some defaults
        np.setHpr(LVecBase3f(0, 90, 0))
        #
        mat = Material()
        mat.setDiffuse((1, 1, 1, 1))
        np.setMaterial(mat)

        self.__app.observer.trigger("OnAddNPs", [np])
        return np

    def add_light(self, light: str):
        if LIGHT_MAP.__contains__(light):
            x = LIGHT_MAP[light]

            name = light.split("_")[2]
            light_node = x[0]
            ed_handle = x[1]
            model = x[2]

            # initialize
            light_node = light_node(name)

            # # no shadows for ambient lights
            # if not isinstance(light_node, AmbientLight):
            #     light_node.setShadowCaster(True, 512, 512)

            # create a np for it
            np = NodePath(name)
            np = np.attachNewNode(light_node)
            np.reparent_to(self.__active_scene.render)

            # wrap it into an editor node-path
            np = ed_handle(np=np, path="")
            np.setPythonTag(constants.TAG_GAME_OBJECT, np)

            # re-parent node-path to a model for visual representation in editor mode
            model = self.__loader.loadModel(model, noCache=True)
            model.setLightOff()
            model.show(constants.ED_GEO_MASK)
            model.hide(constants.GAME_GEO_MASK)
            model.reparentTo(np)

            if self.__scene_lights_on:
                self.__active_scene.render.setLight(np)

            self.__app.observer.trigger("OnAddNPs", [np])
            return np

    def on_duplicate_nps(self):
        if len(self.__selection.selected_nps) > 0:
            (self.__app.command_manager.do(commands.DuplicateNPs(self.__app)))

    def duplicate_nps(self, selections=None, render=None):
        selections = self.__selection.selected_nps if selections is None else selections
        new_selections = []

        for np in selections:

            is_shadow_caster = False
            if isinstance(np.node(), PointLight) or \
                    isinstance(np.node(), Spotlight) or \
                    isinstance(np.node(), DirectionalLight):
                np.node().setShadowCaster(False)
                is_shadow_caster = True

            x = np.copyTo(self.__active_scene.render)
            self.traverse_scene_graph(x,
                                      light_func=self.__active_scene.render.set_light if self.__scene_lights_on else None,
                                      recreate=True)

            if is_shadow_caster:
                x.node().setShadowCaster(True)
                np.node().setShadowCaster(True)

            new_selections.append(x.getPythonTag(constants.TAG_GAME_OBJECT))

        self.__app.observer.trigger("OnAddNPs", new_selections)
        return new_selections

    def reparent_np(self, src_nps, target_np):
        for i in range(len(src_nps)):
            src_np = src_nps[i]

            if type(target_np) is list:
                target_np_ = target_np[i]
            else:
                target_np_ = target_np

            src_np.wrtReparentTo(target_np_)

        return True

    def remove_nps(self, nps: list = None, permanent=False):
        """removes the given nps or current selected nps from active_scene but does not delete them"""
        nps = self.__selection.selected_nps if nps is None else nps
        self.__app.observer.trigger("OnRemoveNPs", nps)
        for np in nps:
            self.traverse_scene_graph(np,
                                      cam_func=self.__active_scene.clear_cam,
                                      light_func=self.__active_scene.render.clear_light if self.__scene_lights_on else None)
        for np in nps:
            np.remove_node() if permanent else np.detach_node()

    def restore_nps(self, nps: list):
        """restores given nps or current selected nps from ed_render to active_scene"""

        restored_nps = []
        for np, parent in nps:
            np.reparent_to(parent)
            self.traverse_scene_graph(np,
                                      self.__active_scene.set_active_camera if not self.__active_scene.main_camera else None,
                                      self.__active_scene.render.setLight)
            restored_nps.append(np)
        restored_nps = [np for np in restored_nps if np.get_parent() not in restored_nps]

        self.__app.observer.trigger("OnAddNPs", restored_nps)
        return restored_nps

    def toggle_scene_lights(self):
        """inverts scene_light_on status and returns inverted value"""

        if self.__scene_lights_on:
            self.__scene_lights_on = False
            self.__active_scene.render.clear_light()

        else:
            for light in self.__active_scene.scene_lights:
                self.__active_scene.render.set_light(light)
            self.__scene_lights_on = True

        return self.__scene_lights_on

    def switch_ed_viewport_style(self):
        self.__game_viewport_maximized = not self.__game_viewport_maximized

    def update_game_view_port_style(self):
        # toggle on maximized game display region
        if self.__game_viewport_maximized and self.__ed_state == constants.GAME_STATE:
            self.__app.show_base.edDr.setActive(False)
            self.__project.game.dr.set_dimensions((0, 1, 0, 1))
            self.__project.game.dr_2D.set_dimensions((0, 1, 0, 1))
        else:
            self.__app.show_base.edDr.setActive(True)
            self.__project.game.dr.set_dimensions((0, 0.4, 0, 0.4))
            self.__project.game.dr_2D.set_dimensions((0, 0.4, 0, 0.4))

    def traverse_scene_graph(self, np, cam_func=None, light_func=None, np_func=None, recreate=False):
        def op(np_):
            result = True
            if isinstance(np_, NodePath) and np_.hasPythonTag(constants.TAG_GAME_OBJECT):
                original_obj = np_.getPythonTag(constants.TAG_GAME_OBJECT)
                if recreate:
                    # then wrap NodePath into editor NodePath object
                    obj_type = NODE_TYPE_MAP[original_obj.id]
                    if original_obj.id == constants.ACTOR_NODEPATH:
                        # creating an instance of an Actor will create a new actor node in scene graph,
                        # so make sure to remove existing
                        new_obj = obj_type(path=original_obj.path, actor_other=original_obj,
                                           tag=constants.TAG_GAME_OBJECT)  # new
                        new_obj.reparent_to(np_.get_parent())  # make sure it has same pos in scene graph.
                        new_obj.set_name(original_obj.get_name())  # sometimes copy constructor of actor changes name
                        LevelEditor.add_children(new_obj, new_obj.path)
                        actors.append(np_)  # collect existing, remove afterwards
                        result = False
                    else:
                        new_obj = obj_type(np_, path=original_obj.path)
                        np_.clearPythonTag(constants.TAG_GAME_OBJECT)  # existing
                        np_.setPythonTag(constants.TAG_GAME_OBJECT, new_obj)  # set new

                    new_obj.copy_properties(original_obj)

                    # --------------------------------------
                    # Components have to be registered again
                    component_paths = original_obj.components.keys()
                    registered = self.register_component(component_paths, [new_obj])
                    # copy components data as well
                    i = 0
                    for key in original_obj.components.keys():
                        registered[i].copy_data(original_obj.components[key])
                        i += 1
                    #
                    original_obj = new_obj

                if original_obj.id in ["__PointLight__", "__DirectionalLight__", "__SpotLight__", "__AmbientLight__"]:
                    if light_func:
                        light_func(original_obj)
                elif original_obj.id == "__CameraNodePath__":
                    if cam_func:
                        cam_func(original_obj)
                else:
                    if np_func:
                        np_func(original_obj)

            return result

        actors = []

        def traverse(np_):
            result = op(np_)
            for child in np_.getChildren():
                if not result:
                    continue
                traverse(child)

        traverse(np)

        for actor in actors:
            actor.clearPythonTag(constants.TAG_GAME_OBJECT)
            actor.remove_node()

    @property
    def game_viewport_maximized(self):
        return self.__game_viewport_maximized

    @property
    def app(self):
        return self.__app

    @property
    def ed_state(self):
        return self.__ed_state
