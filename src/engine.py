import panda3d.core as p3d

from sceneCam import SceneCamera
from axisGrid import ThreeAxisGrid
from resourceManager import ResourceManager
from scripts import Mouse


class Engine(object):
    def __init__(self):
        object.__init__(self)
        
        # _______________________instance attributes_______________________
        # engine and window
        self.__engine = None
        self.__pipe = None
        self.__win = None
        
        # display region, cam, mouse_watcher_node for 3D rendering
        self.__dr = None
        self.__mouse_watcher_node = None
        self.__render = None    # scene graph for 3D rendering
        self.__scene_cam = None
        
        # other fields
        self.__aspect_ratio = 1.0
        self.__evt_hook = None
        self.__update_callbacks = []  # 
        self.__mouse_watchers = []
        
        # display region, cam, mouse_watcher_node for 2D rendering
        self.__dr2d = None
        self.__mouse_watcher_node_2d = None
        self.__render2d = None  # scene graph for 2D rendering
        self.__aspect2d = None  # aspect corrected 2D scene graph
        self.__cam2d = None
        # -----------------------___________________-----------------------
        
        # data root
        self.__data_root = p3d.NodePath('DataRoot')
        self.__data_graph_trav = p3d.DataGraphTraverser()
        
        # get global event queue and handler
        self.__event_queue = p3d.EventQueue.getGlobalEventQueue()
        self.__event_handler = p3d.EventHandler.getGlobalEventHandler()
        
        # initialize the engine and various systems
        self.create_win()
        self.setup_input_handling()
        self.__mouse = Mouse(self)
        self.create_3d_render()
        self.create_2d_render()
        
        self.create_axis_grid()
        self.create_default_scene()
        
        self.__resource_handler = ResourceManager()
                
        # scene camera needs some references not available at time of its creation
        # so we set them now.
        self.__scene_cam.initialize(self)
                                                           
        # reset everything, 
        self.__scene_cam.reset()

    def create_win(self):
        engine = p3d.GraphicsEngine.get_global_ptr()
        pipe = p3d.GraphicsPipeSelection.get_global_ptr().make_default_pipe()
        
        # create frame buffer properties
        fb_props = p3d.FrameBufferProperties()
        fb_props.set_rgb_color(True)
        fb_props.set_color_bits(3*8)
        fb_props.set_depth_bits(24)
        fb_props.set_back_buffers(1)
        
        win_props = p3d.WindowProperties.getDefault()
        
        # create the main window
        win = engine.make_output(pipe,
                                 name="window",
                                 sort=0,
                                 fb_prop=fb_props,
                                 win_prop=win_props,
                                 flags=p3d.GraphicsPipe.BF_require_window)
                                 
        self.__engine = engine
        self.__pipe = pipe
        self.__win = win
        
    def add_update_callback(self, callback):
        if not callback in self.__update_callbacks:
            self.__update_callbacks.append(callback)
        else:
            pass
                
    def create_3d_render(self):
        # create a new display region
        self.__dr = self.__win.make_display_region()
        self.__dr.set_clear_color_active(True)
        self.__dr.set_clear_color((0.3, 0.3, 0.3, 1.0))
        
        # create the render scene graph, the primary scene graph for
        # rendering 3D geometry.
        self.__render = p3d.NodePath('render')
        self.__render.setAttrib(p3d.RescaleNormalAttrib.makeDefault())
        self.__render.setTwoSided(0)
        
        # constrain primary mouse watcher node to display region for
        # 3D rendering
        self.__mouse_watcher_node.setDisplayRegion(self.__dr)
        
        # create a new scene camera
        self.__scene_cam = SceneCamera()
                                       
        self.__scene_cam.reparent_to(self.__render)
        self.__scene_cam.set_pos(0, -35, 0)
        
        # and set it to display region for 3d rendering 
        self.__dr.set_camera(self.__scene_cam)
        
    def create_2d_render(self):
        # create new 2d display region
        self.__dr2d = self.__win.makeDisplayRegion(0, 1, 0, 1)
        self.__dr2d.setSort(1)
        self.__dr2d.setActive(True)

        # create a new 2d scene graph
        self.__render2d = p3d.NodePath('Render2d')
        self.__render2d.setDepthTest(False)
        self.__render2d.setDepthWrite(False)

        # create an aspect corrected 2d scene graph
        self.__aspect2d = self.__render2d.attachNewNode(p3d.PGTop('Aspect2d'))

        # also inform 2D gui systems of our mouse watcher
        self.__aspect2d.node().setMouseWatcher(self.__mouse_watcher_node)

        # create a 2d camera
        self.__cam2d = p3d.NodePath(p3d.Camera('Camera2d'))
        self.__cam2d.reparentTo(self.__render2d)
        
        lens = p3d.OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        self.__cam2d.node().setLens(lens)
        
        # set this 2d camera to 2d display region        
        self.__dr2d.setCamera(self.__cam2d)
        
        # see https://docs.panda3d.org/1.10/python/reference/panda3d.core.PGMouseWatcherBackground
        # for explaination on this
        self.__mouse_watcher_node.addRegion(p3d.PGMouseWatcherBackground())
        
    def create_default_scene(self):
        pass
        
    def create_axis_grid(self):
        self.__grid_np = ThreeAxisGrid()
        self.__grid_np.create(100, 10, 2)
        self.__grid_np.reparent_to(self.__render)
        
    def create_scene_cam(self):
        self.__scene_cam = SceneCamera(self)
                                       
        self.__scene_cam.reparent_to(self.__render)
        self.__scene_cam.set_pos(0, -35, 0)
               
    def exit(self):
        self.__win.setActive(False)
        self.__engine.remove_window(self.__win)
                
    def on_evt_size(self):        
        props = self.__win.getProperties()

        aspect = props.getXSize() / props.getYSize()

        if aspect == 0:
            return 0
                
        self.__aspect2d.setScale(1.0 / aspect, 1.0, 1.0)
        
        if self.__scene_cam:
            self.__scene_cam.on_resize_event(aspect)
            
        self.__aspect_ratio = aspect
        return self.__aspect_ratio

    def process_events(self, event):
        """
        Extract the actual data from the eventParameter.
        """
        
        """
        Stolen from direct.showbase.EventManager.py script.
        """
        
        if not event.name:
            print("Unnammed event from c++".format())
            return

        if event.name == "window-event":
            self.on_evt_size()
        
        # parse event arguments
        param_list = []
        
        for event_parameter in event.parameters:
            
            if event_parameter.isInt():
                event_param_data = event_parameter.getIntValue()
            elif event_parameter.isDouble():
                event_param_data = event_parameter.getDoubleValue()
            elif event_parameter.isString():
                event_param_data = event_parameter.getStringValue()
            elif event_parameter.isWstring():
                event_param_data = event_parameter.getWstringValue()
            elif event_parameter.isTypedRefCount():
                event_param_data = event_parameter.getTypedRefCountValue()
            elif event_parameter.isEmpty():
                event_param_data = None
            else:
                # Must be some user defined type, return the ptr
                # which will be downcast to that type.
                event_param_data = event_parameter.getPtr()
        
            param_list.append(event_param_data)
                        
        # send this evt to host application as well.
        if self.__evt_hook:
            self.__evt_hook(event, param_list)
                        
        # send the event down into C++ lands.
        if self.__event_handler:
            self.__event_handler.dispatchEvent(event)
        
    def setup_input_handling(self):
        mouse_and_keyboard = p3d.MouseAndKeyboard(self.__win, 0, "MouseAndKeyboard_01")
        mk_node = self.__data_root.attachNewNode(mouse_and_keyboard)
        
        mouse_watcher = p3d.MouseWatcher("MouseWatcher_01")
        mouse_watcher = mk_node.attachNewNode(mouse_watcher)
        mouse_watcher_node = mouse_watcher.node()
                
        button_thrower = p3d.ButtonThrower("Button_Thrower_01")
        button_thrower = mouse_watcher.attachNewNode(button_thrower)
        
        if self.__win.getSideBySideStereo():
            # If the window has side-by-side stereo enabled, then
            # we should constrain the MouseWatcher to the window's
            # DisplayRegion.  This will enable the MouseWatcher to
            # track the left and right halves of the screen
            # individually.
            mouse_watcher_node.setDisplayRegion(self.__win.getOverlayDisplayRegion())
        
        # add modifiers buttons for both mouse watcher node and button thrower
        mb = mouse_watcher_node.getModifierButtons()
        mb.addButton(p3d.KeyboardButton.shift())
        mb.addButton(p3d.KeyboardButton.control())
        mb.addButton(p3d.KeyboardButton.alt())
        mb.addButton(p3d.KeyboardButton.meta())
        mouse_watcher_node.setModifierButtons(mb)
        # 
        mods = p3d.ModifierButtons()
        mods.addButton(p3d.KeyboardButton.shift())
        mods.addButton(p3d.KeyboardButton.control())
        mods.addButton(p3d.KeyboardButton.alt())
        mods.addButton(p3d.KeyboardButton.meta())
        button_thrower.node().setModifierButtons(mods)
        
        # 
        self.__mouse_watchers.append(mouse_watcher)
        self.__mouse_watcher_node = mouse_watcher_node
        
    def set_event_hook(self, hook):
        self.__evt_hook = hook

    def update(self):     
        # keep taskmanager updated
        if self.__mouse_watcher_node.has_mouse():
            p3d.AsyncTaskManager.getGlobalPtr().poll()
           
        # traverse the data graph.  This reads all the control
        # inputs (from the mouse and keyboard, for instance) and also
        # directly acts upon them (for instance, to move the avatar).
        self.__data_graph_trav.traverse(self.__data_root.node())
        
        # process events
        isEmptyFunc = self.__event_queue.isQueueEmpty
        dequeueFunc = self.__event_queue.dequeueEvent
        
        while not isEmptyFunc():
            self.process_events(dequeueFunc())

        # 
        self.__mouse.update()
        self.__scene_cam.update()
        
        for callback in self.__update_callbacks:
            callback()

        # finally, render frame        
        self.__engine.render_frame()

    @property
    def aspect2d(self):
        return self.__aspect2d

    @property
    def cam(self):
        return self.__scene_cam

    @property
    def cam2d(self):
        return self.__cam2d
    
    @property
    def aspect_ratio(self):
        return self.__aspect_ratio
    
    @property
    def dr2d(self):
        return self.__dr2d

    @property
    def dr3d(self):
        return self.__dr

    @property
    def engine(self):
        return self.__engine
    
    @property
    def grid_np(self):
        return self.__grid_np
    
    @property
    def mouse(self):
        return self.__mouse
    
    @property
    def mouse_watcher_node(self):
        return self.__mouse_watcher_node
    
    @property
    def render(self):
        return self.__render
        
    @property
    def render2d(self):
        return self.__render2d

    @property
    def resource_manager(self):
        return self.__resource_handler

    @property
    def win(self):
        return self.__win
