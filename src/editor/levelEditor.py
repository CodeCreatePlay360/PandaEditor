import traceback
import panda3d.core as p3d_core
import editor.core as ed_core
import editor.nodes as ed_nodepaths
import editor.gizmos as gizmos
import editor.constants as constants
import editor.commands as commands
import editor.utils as ed_utils

from datetime import date

from direct.showbase.DirectObject import DirectObject
from direct.showbase.Loader import Loader
from direct.showbase.ShowBase import taskMgr
from editor.project import Project
from editor.globals import editor
from editor.selection import Selection
from editor.pluginManager import PluginsManager
from editor.editorSettings import EditorSettings

LIGHT_MAP = {constants.POINT_LIGHT: (p3d_core.PointLight, ed_nodepaths.EdPointLight, constants.POINT_LIGHT_MODEL),
             constants.SPOT_LIGHT: (p3d_core.Spotlight, ed_nodepaths.EdSpotLight, constants.SPOT_LIGHT_MODEL),
             constants.DIRECTIONAL_LIGHT: (p3d_core.DirectionalLight, ed_nodepaths.EdDirectionalLight,
                                           constants.DIR_LIGHT_MODEL),
             constants.AMBIENT_LIGHT: (p3d_core.AmbientLight, ed_nodepaths.EdAmbientLight,
                                       constants.AMBIENT_LIGHT_MODEL)}

NODE_TYPE_MAP = {constants.DIRECTIONAL_LIGHT: ed_nodepaths.EdDirectionalLight,
                 constants.POINT_LIGHT: ed_nodepaths.EdPointLight,
                 constants.SPOT_LIGHT: ed_nodepaths.EdSpotLight,
                 constants.AMBIENT_LIGHT: ed_nodepaths.EdAmbientLight,
                 constants.CAMERA_NODEPATH: ed_nodepaths.CameraNodePath,
                 constants.NODEPATH: ed_nodepaths.ModelNodePath,
                 constants.ACTOR_NODEPATH: None}


class LevelEditor(DirectObject):
    def __init__(self, panda_app, *args, **kwargs):
        """Actual Level / scene editor all editor systems should be initialized from here"""

        DirectObject.__init__(self)
        self.app = panda_app

        # panda_path = p3d_core.Filename.fromOsSpecific(constants.MODELS_PATH)
        # p3d_core.get_model_path().prependDirectory(panda_path)

        self.project = Project(panda_app)
        self.editor_settings = EditorSettings(self)
        self.plugins_manager = PluginsManager()

        self.active_scene = None

        # gizmos, grid, selection
        self.grid_np = None
        self.selection = None
        self.gizmo = False
        self.gizmo_mgr_root_np = None
        self.gizmo_mgr = None
        self.active_gizmo = None  # position, rotation, or scale

        '''grid, selection and gizmos'''
        self.create_grid(200, 40, 5)
        self.setup_selection_system()
        self.setup_gizmo_manager()

        # create event map for various keyboard events and bind them
        self.key_event_map = {"q": (self.set_active_gizmo, "None"),
                              "w": (self.set_active_gizmo, "pos"),
                              "e": (self.set_active_gizmo, "rot"),
                              "r": (self.set_active_gizmo, "scl"),
                              "space": (self.toggle_gizmo_local, None),
                              "+": (self.gizmo_mgr.SetSize, 2),
                              "-": (self.gizmo_mgr.SetSize, 0.5),
                              "control-d": (self.on_duplicate_nps, None),
                              "x": (
                                  lambda: self.app.command_manager.do(
                                      commands.RemoveObjects(self.selection.selected_nps)), None),
                              "control-z": (self.app.command_manager.undo, None),

                              "mouse1": (self.on_mouse1_down, [False]),
                              "mouse2": (self.on_mouse2_down, None),

                              "mouse1-up": (self.on_mouse1_up, None),
                              "mouse2-up": (self.on_mouse2_up, None),

                              "shift-mouse1": (self.on_mouse1_down, [True]),
                              "control-mouse1": (self.on_mouse1_down, None)
                              }

        self.scene_lights_on = False  # scene lights are on or off ?
        self.mouse_1_down = False  # is mouse button 1 down ?
        self.mouse_2_down = False  # is mouse button 2 down ?
        self.ed_state = constants.EDITOR_STATE  # is current state editor or game state ?

        self.__game_viewport_maximized = False
        self.current_mouse_mode = None

        # editor update task
        self.update_task = None
        self.current_xform_time = 0
        self.x_form_delay = 0.1  # delay time before updating inspector panel
        self.update_task = taskMgr.add(self.update, 'EditorUpdateTask', sort=0)

        # available loaded resources
        # TODO replace this with ResourceHandler
        self.__loader = Loader(self.app.show_base)
        self.__user_modules = {}
        self.__ed_plugins = {}
        self.__text_files = {}
        # ---------------------------------------

        self.user_commands = {}

        self.today = date.today()  # TODO replace this with something global
        self.bind_key_events()

    def start(self):
        p3d_core.get_model_path().clear()
        self.create_new_project("DefaultProject", constants.DEFAULT_PROJECT_PATH)
        self.app.command_manager.clear()
        # editor.observer.trigger("EditorReload")

    def update(self, task):
        """this method should be called ever frame in editor_state and game_state"""

        # XFormTask updates Inspector panel
        if task.time > self.current_xform_time:
            editor.observer.trigger("XFormTask")
            self.current_xform_time += self.x_form_delay

        self.update_gizmo()  # this has to be updated regularly otherwise gizmo movement appears jagged
        editor.observer.trigger("EditorUpdate")
        return task.cont

    # --------------------------------Scene operations-----------------------------#
    def create_new_project(self, name, path):
        if self.ed_state == constants.GAME_STATE:
            print("[Editor] Cannot create new project in game mode")
            return

        self.project.set_project(name, path)
        self.create_new_scene(initial=True)

    def create_new_scene(self, initial: bool = False):
        """creates and set up a default scene
        initial: Is this the first default scene when a project is created ?"""

        if self.active_scene:
            self.clean_active_scene()

        # create a new scene
        self.active_scene = self.project.game.create_new_scene("default")

        # get the wx-scene graph panel and set it up
        editor.scene_graph.init(self.active_scene.render)

        #
        self.selection.active_scene = self.active_scene

        # finally, set up the default scene
        self.setup_default_scene()

        # ------------------------------------------------------------------------------------
        # TODO replace this with a general call to reload resources
        if initial:
            editor.resource_browser.remove_all_libs()
            editor.resource_browser.create_or_rebuild_tree(self.project.project_path, rebuild_event=False)
            self.register_user_modules(editor.resource_browser.resources["py"])
            self.register_text_files(editor.resource_browser.resources["txt"])
            editor.resource_browser.schedule_dir_watcher()

    def setup_default_scene(self):
        # add a default sunlight
        self.app.command_manager.do(commands.AddLight("__DirectionalLight__"), select=False)
        light_np = self.active_scene.render.find("**/DirectionalLight")
        light_np = light_np.getPythonTag(constants.TAG_GAME_OBJECT)
        light_np.setPos(400, 200, 350)
        light_np.setHpr(p3d_core.Vec3(115, -25, 0))
        light_np.set_color(p3d_core.Vec4(1, 0.95, 0.5, 255))

        # add a default player camera
        self.app.command_manager.do(commands.AddCamera())
        cam = self.active_scene.render.find("**/Camera").getNetPythonTag(constants.TAG_GAME_OBJECT)
        cam.setPos(-239.722, 336.966, 216.269)
        cam.setHpr(p3d_core.Vec3(-145.0, -20, 0))
        self.set_main_camera(cam)

        # add a default cube
        self.app.command_manager.do(commands.ObjectAdd(constants.CUBE_PATH))
        obj = self.active_scene.render.find("**/cube.fbx")
        obj.setScale(0.5)

        self.set_active_gizmo("pos")

        editor.observer.trigger("OnSceneStart")
        editor.observer.trigger("ToggleSceneLights")

    def clean_active_scene(self):
        editor.observer.trigger("OnSceneClean", None)

        self.scene_lights_on = False
        self.selection.deselect_all()
        self.active_scene.render.remove_node()

    # -------------------------------Resources section-----------------------------#
    # load and register resources
    # TODO replace this with ResourceHandler

    def register_user_modules(self, modules_paths):
        """Imports, instantiates, reload and registers RuntimeModules and EditorPlugins
        modules_paths = all python modules in project"""

        def init_runtime_module(name, runtime_module, path_):
            instance = runtime_module(
                name=name,
                show_base=self.project.game.show_base,
                win=self.project.game.win,
                dr=self.project.game.display_region,
                dr2d=self.project.game.display_region_2d,
                mouse_watcher_node=self.project.game.mouse_watcher_node,
                render=self.active_scene.render,
                render2d=self.active_scene.render_2d,
                aspect2d=self.active_scene.aspect_2d,
                game=self.project.game,
                path=path_
            )
            return instance

        def init_ed_plugin(name, plugin, path_):
            instance = plugin(
                name=name,
                win=self.app.show_base.main_win,
                dr=self.app.show_base.edDr,
                dr2d=self.app.show_base.edDr2d,
                mouse_watcher_node=self.app.show_base.ed_mouse_watcher_node,
                render=self.app.show_base.render,
                render2d=None,
                aspect2d=self.app.show_base.ed_aspect2d,
                level_editor=self,
                globals=self.app.globals,
                path=path_,
                command_manager=self.app.command_manager
            )
            return instance

        if len(modules_paths) == 0:
            return True

        imported_modules = ed_utils.try_execute_1(ed_utils.Importer.import_modules, modules_paths)
        if imported_modules is None:
            return

        saved_data = {}  # cls_name: user_mod.saved_data
        for key in self.__user_modules.keys():
            user_mod = self.__user_modules[key]

            cls_instance = user_mod.class_instance
            cls_instance.ignore_all()

            user_mod.save_data()
            saved_data[key] = user_mod.saved_data

        self.app.show_base.clear_ed_aspect_2d()
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

                    if obj_type == ed_core.editorPlugin.EditorPlugin:
                        cls_instance = init_ed_plugin(cls_name, cls, path)

                    module_type = cls_instance.type

                except Exception as e:
                    tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
                    for x in tb_str:
                        print(x)
                    print("{0} Unable to load user module {1}".format(self.today, cls_name))
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
                    print("[{0}] Loaded RuntimeUserModule {1}.".format(self.today, cls_name))

                elif module_type == constants.EditorPlugin:
                    # it's an editor plugin
                    ed_plugin = self.__user_modules[path].class_instance
                    ed_plugin._sort = 1
                    ed_plugins.append(ed_plugin)

        # finally, register editor tools
        self.register_editor_plugins(ed_plugins)
        self.register_user_commands(ed_plugins)
        #
        # self.project.game.runtime_modules = game_modules
        self.register_runtime_modules(game_modules)
        #
        return True

    def register_component(self, paths: list, nps=None):
        imported = ed_utils.try_execute_1(ed_utils.Importer.import_modules, paths)
        if imported is None:
            return

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

                nps_ = nps if nps else self.selection.selected_nps
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
            name = path.split("/")[-1]
            name = name.split(".")[0]
            self.__text_files[path] = ed_core.TextFile(path)
            print("[{0}] Loaded TextFile {1}.".format(self.today, name))

    def register_runtime_modules(self, runtime_modules):
        self.project.game.runtime_modules = runtime_modules

    def register_editor_plugins(self, plugins):
        """load all editor plugins"""
        for plugin in plugins:
            self.__ed_plugins[plugin.name] = plugin
            res = plugin.start(sort=1)
            if res:
                self.app.wx_main.menu_bar.add_ed_plugin_menu(plugin.name)
                print("[{0}] Loaded EditorPlugin {1}.".format(self.today, plugin.name))

    def unregister_editor_plugins(self):
        """unloads all editor plugins"""
        for key in self.__ed_plugins.keys():
            self.__ed_plugins[key].stop()

        self.__ed_plugins.clear()
        self.app.wx_main.menu_bar.clear_ed_plugin_menus()

    def unregister_editor_plugin(self, plugin):
        if plugin.name in self.__ed_plugins.keys():
            self.unregister_user_commands()
            del self.__ed_plugins[plugin.name]
            del self.__user_modules[plugin.path]
            print("Unloading editor plugin: {0}".format(plugin.name))

        editor.wx_main.menu_bar.clear_ed_plugin_menus()  # clear all plugin menu bar entries
        editor.wx_main.menu_bar.clear_user_command_menus()  # clear all user commands menu bar entries

        # add the plugin menu bar entries for remaining plugins
        for plugin in self.__ed_plugins.keys():
            self.app.wx_main.menu_bar.add_ed_plugin_menu(plugin.name)

        # add the user commands menu bar entries for remaining plugins
        self.register_user_commands(self.__ed_plugins)

    def register_user_commands(self, ed_plugins=None):
        for plugin in ed_plugins:
            for cmd_name in plugin.commands.keys():
                self.user_commands[cmd_name] = plugin.commands[cmd_name]
                self.app.wx_main.menu_bar.add_user_command_menu(cmd_name)

    def unregister_user_commands(self):
        self.user_commands.clear()
        self.app.wx_main.menu_bar.clear_user_command_menus()  # clear menu bar entries for user commands

    def initialize_component(self, name, component, path, np):
        instance = component(
            name=name,
            show_base=self.project.game.show_base,
            win=self.project.game.win,
            dr=self.project.game.display_region,
            dr2d=self.project.game.display_region_2d,
            mouse_watcher_node=self.project.game.mouse_watcher_node,
            render=self.active_scene.render,
            render2d=self.active_scene.render_2d,
            aspect2d=self.active_scene.aspect_2d,
            game=self.project.game,
            path=path,
            np=np
        )
        return instance

    def reload_components(self, paths: list):
        saved_components = {}  # np: [components_paths]

        # get all existing components and save them
        # TODO make sure saved comp exists in incoming paths
        existing_components = self.project.game.components  # game.component return as a dict (np: components)
        for np in existing_components.keys():
            for comp in existing_components[np]:

                comp.save_data()
                comp.class_instance.ignore_all()

                if comp.path not in paths:
                    continue

                if not saved_components.__contains__(np):
                    saved_components[np] = []

                saved_components[np].append(comp)

            np.clear_components()

        # now reload the saved_components
        for np in saved_components.keys():

            paths = []
            for comp in saved_components[np]:
                paths.append(comp.path)

            new_comp = self.register_component(paths=paths, nps=[np])[0]

            old_comp_idx = -1
            for i in range(len(saved_components[np])):
                old_comp = saved_components[np][i]
                if old_comp.path == new_comp.path:
                    old_comp_idx = i

            old_saved_data = saved_components[np][old_comp_idx].saved_data

            new_comp.saved_data = old_saved_data
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
    def user_modules(self):
        user_modules = []
        for key in self.__user_modules.keys():
            user_modules.append(self.__user_modules[key].class_instance)
        return user_modules

    # ------------------------------Level editor section ----------------------------- #

    def setup_selection_system(self):
        self.selection = Selection(
            camera=self.app.show_base.ed_camera,
            render=self.app.show_base.edRender,
            render2d=self.app.show_base.edRender2d,
            win=self.app.show_base.main_win,
            mouseWatcherNode=self.app.show_base.ed_mouse_watcher_node,
            active_scene=self.active_scene
        )

    def create_grid(self, size, grid_step, sub_divisions):
        # grid_np = self.app.show_base.edRender.find("AxisGrid")
        if self.grid_np:
            self.grid_np.clearPythonTag("AxisGridNP")
            self.grid_np.remove_node()

        grid_np = ed_core.ThreeAxisGrid()
        grid_np.setPythonTag(grid_np, "AxisGridNP")
        grid_np.create(size, grid_step, sub_divisions)
        grid_np.reparent_to(self.app.show_base.edRender)
        grid_np.show(constants.ED_GEO_MASK)
        grid_np.hide(constants.GAME_GEO_MASK)
        self.grid_np = grid_np

    def setup_gizmo_manager(self):
        """Create gizmo manager."""
        self.gizmo_mgr_root_np = p3d_core.NodePath("Gizmos")
        self.gizmo_mgr_root_np.reparent_to(self.app.show_base.edRender)

        kwargs = {
            "camera": self.app.show_base.ed_camera,
            "render": self.gizmo_mgr_root_np,
            "root2d": self.app.show_base.edRender2d,
            "win": self.app.show_base.main_win,
            "mouseWatcherNode": self.app.show_base.ed_mouse_watcher_node,
        }

        self.gizmo_mgr = gizmos.Manager(**kwargs)
        self.gizmo_mgr.AddGizmo(gizmos.Translation('pos', **kwargs))
        self.gizmo_mgr.AddGizmo(gizmos.Rotation('rot', **kwargs))
        self.gizmo_mgr.AddGizmo(gizmos.Scale('scl', **kwargs))

        for key in self.gizmo_mgr._gizmos.keys():
            gizmo = self.gizmo_mgr._gizmos[key]
            gizmo.hide(constants.GAME_GEO_MASK)

    def start_transform(self):
        self.selection.previous_matrices.clear()
        for np in self.selection.selected_nps:
            self.selection.previous_matrices[np] = np.get_transform()

    def stop_transform(self):
        if len(self.selection.previous_matrices) > 0:
            cmd = commands.TransformNPs(self.selection.previous_matrices)
            self.app.command_manager.do(cmd)

    def set_active_gizmo(self, gizmo):
        self.active_gizmo = gizmo
        self.gizmo_mgr.SetActiveGizmo(gizmo)

    def set_gizmo_local(self, val):
        self.gizmo_mgr.SetLocal(val)

    def set_selected(self, selections: list):
        if len(selections) > 0:
            self.selection.set_selected(selections)
            self.update_gizmo()

    def toggle_gizmo_local(self, *args):
        self.gizmo_mgr.ToggleLocal()

    def update_gizmo(self):
        if self.active_gizmo is not None:
            nps = self.selection.selected_nps
            self.gizmo_mgr.AttachNodePaths(nps)
            self.gizmo_mgr.RefreshActiveGizmo()

    def bind_key_events(self):
        for key in self.key_event_map.keys():
            func = self.key_event_map[key][0]
            args = self.key_event_map[key][1]

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
        self.mouse_1_down = True

        if not self.gizmo_mgr.IsDragging() and ed_core.MOUSE_ALT not in self.app.show_base.ed_camera.mouse.modifiers:
            self.selection.start_drag_select(shift[0])

        elif self.gizmo_mgr.IsDragging():
            self.start_transform()

    def on_mouse1_up(self):
        self.mouse_1_down = False

        if self.selection.marquee.IsRunning():
            last_selections = [np for np in self.selection.selected_nps]
            nps = self.selection.stop_drag_select()

            # select nps and start transform
            if len(nps) > 0:
                self.app.command_manager.do(commands.SelectObjects(nps, last_selections))
            else:
                self.deselect_all()

        elif self.gizmo_mgr.IsDragging():
            self.stop_transform()

    def on_mouse2_down(self):
        pass

    def on_mouse2_up(self):
        pass

    def deselect_all(self, trigger_deselect_event=True):
        # len_selected = len(self.selection.selected_nps)
        self.selection.deselect_all()
        # self.gizmo_mgr.SetActiveGizmo(None)
        self.update_gizmo()
        if trigger_deselect_event:
            editor.observer.trigger("OnDeselectAllNPs")

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
        print("[LevelEditor] Editor state enabled.")

        self.ed_state = constants.EDITOR_STATE
        self.project.game.stop()
        self.deselect_all()  # call to deselect all, triggers OnDeselectAllNps event which properly handles
        # UI updates (inspector, scene graph etc.)
        self.app.command_manager.clear()

        if self.__game_viewport_maximized:
            self.app.show_base.edDr.setActive(True)
            self.project.game.display_region.set_dimensions((0, 0.4, 0, 0.4))
            self.project.game.display_region_2d.set_dimensions((0, 0.4, 0, 0.4))

        # -----------------------------------------------
        # clear the runtime scene graph
        for np in self.active_scene.render.get_children():
            self.traverse_scene_graph(np,
                                      light_func=self.active_scene.render.clear_light if self.scene_lights_on else None)
            np.remove_node()

        self.active_scene.main_camera = None

        # restore original saved scene graph
        for np in self.hidden_np.getChildren():
            np.reparent_to(self.active_scene.render)
            self.traverse_scene_graph(np,
                                      cam_func=self.set_main_camera,
                                      light_func=self.active_scene.render.set_light if self.scene_lights_on else None)

        self.hidden_np.remove_node()
        self.hidden_np = None

        editor.observer.trigger("OnEnableEditorState")  # for any cleanup operations

    def enable_game_state(self):
        print("[LevelEditor] Game state enabled.")

        self.ed_state = constants.GAME_STATE
        self.deselect_all()  # call to deselect all, triggers OnDeselectAllNps event which properly handles
        # UI updates (inspector, scene graph etc.)
        self.app.command_manager.clear()

        # saves current active scene into a hidden np
        # duplicate current active scene node-path
        self.hidden_np = p3d_core.NodePath("Hidden")
        self.hidden_np = self.active_scene.render.copy_to(self.hidden_np)
        self.traverse_scene_graph(self.hidden_np, recreate=True)

        # toggle on maximized game display region
        if self.__game_viewport_maximized:
            self.app.show_base.edDr.setActive(False)
            self.project.game.display_region.set_dimensions((0, 1, 0, 1))
            self.project.game.display_region_2d.set_dimensions((0, 1, 0, 1))

        editor.observer.trigger("OnEnableGameState")
        editor.observer.trigger("ResizeEvent")
        self.project.game.start()

    def load_model(self, path):
        """loads a 3d model from "path" """

        def add_children(_np):
            if len(_np.getChildren()) > 0:
                for child in _np.getChildren():
                    if not type(child) == p3d_core.NodePath:
                        continue
                    # print("child: {0} type: {1}".format(child, type(child)))
                    child = ed_nodepaths.ModelNodePath(child, path=path)
                    child.setColor(p3d_core.LColor(1, 1, 1, 1))
                    child.setPythonTag(constants.TAG_GAME_OBJECT, child)
                    if child.get_name() == "":
                        child.set_name("NoName")
                    add_children(child)

        np = ed_utils.try_execute_1(self.__loader.loadModel, path)
        if not np:
            return

        np = ed_nodepaths.ModelNodePath(np, path=path)
        np.setColor(p3d_core.LColor(1, 1, 1, 1))
        np.setPythonTag(constants.TAG_GAME_OBJECT, np)

        add_children(np)

        np.reparent_to(self.active_scene.render)
        editor.observer.trigger("OnAddNPs", [np])
        self.set_selected([np])
        return np

    def add_actor(self, path):
        try:
            actor = ed_nodepaths.ActorNodePath(path, uid="ActorNodePath")
        except Exception as e:
            print(e)
            return

        actor.setPythonTag(constants.TAG_GAME_OBJECT, actor)
        actor.reparentTo(self.active_scene.render)

        return actor

    def add_camera(self):
        # create a panda3d camera
        np = p3d_core.NodePath(p3d_core.Camera("CameraNodePath"))

        # and wrap it into editor camera
        cam_np = ed_nodepaths.CameraNodePath(np=np, path="")
        cam_np.set_name("Camera")
        cam_np.node().setCameraMask(constants.GAME_GEO_MASK)
        cam_np.setPythonTag(constants.TAG_GAME_OBJECT, cam_np)
        cam_np.reparent_to(self.active_scene.render)
        cam_np.setLightOff()

        # create a handle for visual representation in editor mode
        cam_handle = self.__loader.loadModel(constants.CAMERA_MODEL)
        cam_handle.show(constants.ED_GEO_MASK)
        cam_handle.hide(constants.GAME_GEO_MASK)
        cam_handle.reparent_to(cam_np)
        cam_handle.setScale(12)

        if not self.active_scene.main_camera:
            self.active_scene.set_active_camera(cam_np)

        editor.observer.trigger("OnAddNPs", [cam_np])
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
        np.reparent_to(self.active_scene.render)
        np.setPythonTag(constants.TAG_GAME_OBJECT, np)
        np.setHpr(p3d_core.Vec3(0, 90, 0))

        mat = p3d_core.Material()
        mat.setDiffuse((1, 1, 1, 1))
        np.setMaterial(mat)

        editor.observer.trigger("OnAddNPs", [np])
        return np

    def add_light(self, light: str):
        if LIGHT_MAP.__contains__(light):
            x = LIGHT_MAP[light]

            name = light.split("_")[2]
            light_node = x[0](name)
            ed_handle = x[1]
            model = x[2]

            # create the panda3d light object
            np = p3d_core.NodePath(name)
            np = np.attachNewNode(light_node)
            np.reparent_to(self.active_scene.render)

            # wrap it into an editor nodepath
            np = ed_handle(np=np, path="")
            np.setPythonTag(constants.TAG_GAME_OBJECT, np)

            # defaults for light object
            np.setLightOff()
            np.show(constants.ED_GEO_MASK)
            np.hide(constants.GAME_GEO_MASK)

            # re-parent nodepath to a model for visual representation in editor mode
            model = self.__loader.loadModel(model, noCache=True)
            model.reparentTo(np)

            if self.scene_lights_on:
                self.active_scene.render.setLight(np)

            editor.observer.trigger("OnAddNPs", [np])
            return np

    def on_duplicate_nps(self):
        if len(self.selection.selected_nps) > 0:
            (self.app.command_manager.do(commands.DuplicateNPs(self.app)))

    def duplicate_nps(self, selections=None, render=None):
        selections = self.selection.selected_nps if selections is None else selections
        new_selections = []

        if render is None:
            render = self.active_scene.render

        for np in selections:
            if not np.hasPythonTag(constants.TAG_GAME_OBJECT):
                print("[LevelEditor] Warning attempt to duplicate a NodePath with no EditorWrapper.")

            x = np.copyTo(np.get_parent())
            self.traverse_scene_graph(x,
                                      light_func=self.active_scene.render.set_light if self.scene_lights_on else None,
                                      recreate=True)
            new_selections.append(x.getPythonTag(constants.TAG_GAME_OBJECT))

        editor.observer.trigger("OnAddNPs", new_selections)
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
        nps = self.selection.selected_nps if nps is None else nps
        editor.observer.trigger("OnRemoveNPs", nps)
        for np in nps:
            self.traverse_scene_graph(np,
                                      cam_func=self.active_scene.clear_cam,
                                      light_func=self.active_scene.render.clear_light if self.scene_lights_on else None)
        for np in nps:
            np.remove_node() if permanent else np.detach_node()

    def restore_nps(self, nps: list):
        """restores given nps or current selected nps from ed_render to active_scene"""

        restored_nps = []
        for np, parent in nps:
            np.reparent_to(parent)
            self.traverse_scene_graph(np,
                                      self.set_main_camera if not self.active_scene.main_camera else None,
                                      self.active_scene.render.setLight)
            restored_nps.append(np)
        restored_nps = [np for np in restored_nps if np.get_parent() not in restored_nps]

        editor.observer.trigger("OnAddNPs", restored_nps)
        return restored_nps

    def toggle_scene_lights(self):
        """inverts scene_light_on status and returns inverted value"""

        if self.scene_lights_on:
            self.scene_lights_on = False
            self.active_scene.render.clear_light()

        else:
            for light in self.active_scene.scene_lights:
                self.active_scene.render.set_light(light)
            self.scene_lights_on = True

        return self.scene_lights_on

    def switch_ed_viewport_style(self):
        self.__game_viewport_maximized = not self.__game_viewport_maximized

    def set_main_camera(self, cam):
        self.active_scene.set_active_camera(cam)

    @property
    def game_viewport_maximized(self):
        return self.__game_viewport_maximized

    def traverse_scene_graph(self, np, cam_func=None, light_func=None, np_func=None, recreate=False):
        def op(np_):
            if isinstance(np_, p3d_core.NodePath) and np_.hasPythonTag(constants.TAG_GAME_OBJECT):

                obj = np_.getPythonTag(constants.TAG_GAME_OBJECT)
                if recreate:
                    # then wrap NodePath into editor NodePath object
                    new_obj = NODE_TYPE_MAP[obj.id]
                    new_obj = new_obj(np_, path=obj.path)
                    np_.setPythonTag(constants.TAG_GAME_OBJECT, new_obj)
                    new_obj.copy_properties(obj)
                    # ** Components have to be registered again **
                    component_paths = obj.components.keys()
                    registered = self.register_component(component_paths, [new_obj])
                    # copy data as well
                    i = 0
                    for key in obj.components.keys():
                        registered[i].copy_data(obj.components[key])
                        i += 1
                    #
                    obj = np_.getPythonTag(constants.TAG_GAME_OBJECT)

                if obj.id in ["__PointLight__", "__DirectionalLight__", "__SpotLight__", "__AmbientLight__"]:
                    if light_func:
                        light_func(obj)
                elif obj.id == "__CameraNodePath__":
                    if cam_func:
                        cam_func(obj)
                else:
                    if np_func:
                        np_func(obj)

        def traverse(np_):
            op(np_)
            for child in np_.getChildren():
                traverse(child)

        traverse(np)

    def get_np_by_uid(self, uid):
        pass
