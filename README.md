<h1 align="center">🍁 PandaEditor</h1>

<h3> PandaEditor is an open-source level editor for the Panda3D game engine, it is designed to be easy to use and extend and provides end users with a convenient interface and tools to quickly prototype and create 2D or 3D scenes.</h3> 

<h3 align="center">Features</h3>

* Easy object manipulation 
* Object inspection
* Console panel
* Scene graph browser
* Resources browser
* Project based approach
* Complete scripting support that exposes full underlying Panda3D API, scripts can be attached to NodePaths (entity component system) in scene graph defining per object behaviors or you can program in a more traditional way using P3DUserModules.
* To extend the editor, there is a complete support for editor plugins, the developers can create (or maybe even sell) their tools.

***

> 💎 **It takes a considerable amount of time and effort to maintain PandaEditor and keeping it bugfree, not to mention adding new features, writing documentation and tutorials for new users; you can support all this effort by subscribing to any tier of your choice on this patreon page, visit the tiers section to see list of all tiers and their subscription benefits.**  
>
> ⭐ **If you have found PandaEditor useful in your projects then consider giving it a star on GitHub, it will help PandaEditor reach more audience.**

<h3 align="center">Support</h3>

<p align="center">
If you face any issues, please report them on GitHub or post them in the #help channel of our discord server or you can also post them in Panda3D forum post, links are given below.
</p>

<h3 align="center">Community</h3>

<p align="center">
<a href='https://github.com/CodeCreatePlay360/Massive-Designer#tutorials' target="_blank"><img alt='Unity' src='https://img.shields.io/badge/Panda3D forum post-100000?style=plastic&logo=Unity&logoColor=white&labelColor=323232&color=323232'/></a>
<a href='https://discord.gg/WZ3GZCvVtg' target="_blank"><img alt='Discord' src='https://img.shields.io/badge/Discord-5865F2?style=plastic&logo=discord&logoColor=white'/></a>
<a href='https://www.patreon.com/MassiveDesigner' target="_blank"><img alt='Patreon' src='https://img.shields.io/badge/Support on patreon-F96854?style=plastic&logo=patreon&logoColor=white'/></a>
</p>

<p align="center">
<a href='https://github.com/CodeCreatePlay360/Massive-Designer' target="_blank"><img alt='Unity' src='https://img.shields.io/badge/Reddit-FF4500?style=plastic&logo=reddit&logoColor=white'/></a>
<a href='https://github.com/CodeCreatePlay360/Massive-Designer' target="_blank"><img alt='Unity' src='https://img.shields.io/badge/YouTube-FF0000?style=plastic&logo=youtube&logoColor=white'/></a>
</p>

### 🔹Requirements
  1. Panda3D game engine.
  2. WxPython (this is optional, Wx is only needed if you are ever going to use the editor UI)

### 🔹Getting Started

For now there is no executable to start PandaEditor, you will have to manually start it by running "main.py" python script, located in the root of PandaEditor directory. 

```
python main.py
```

### 🔹Viewport Navigation

Use the following keyboard / mouse controls to move around the scene.

* Alt + right mouse button + mouse drag to rotate.
* Alt + middle mouse button + mouse drag to dolly.
* Alt + left mouse button + mouse drag to zoom.
* Control + D to duplicate selected objects.
* X to remove / delete selected objects.
* Control + Z to undo.

### 🔹Running Demo Projects
PandaEditor comes with some demo projects to demonstrate various aspects and capabilities of Panda3D and PandaEditor, most of the code is fully commented out so you can use it for your projects as a reference. All demo projects are located in "demo" folder in the root of this repository, to start any demo project, simply run "main.py" python script with an optional command line argument "-demo" followed by name of demo project from your python console, for example.

```
python main.py -demo NameOfDemoProject
```

For example to run the _AnimatedCharacter_ demo project, use the following command.

```
python main.py -demo AnimatedCharacter
```


~~To see more information on a particular demo there is a "readme file" along with each demo in "src/demos" folder; here is a list of all demos.~~
1. ~~AnimatedCharacter~~
2. ~~ThirdPersonCamera~~
3. ~~ThirdPersonCharacterController~~



<h2 align="center"> <a href="">Programmers Section</a> | <a href="">Artists Section</a> </h2>

<h3 align="center"> ⚙️ Programmers section </h3>

### ▪️ Programming Basics
- Starting the editor
- Accessing systems
  - Using the Systems utility class
- Event handling
  - Handling default events
  - Creating new events
- Input handling
- Managing continuously updating tasks

***

<h2 align="center"> Programming Basics </h2>

### 🔹Starting the editor

The recommended way to start PandaEditor is using the included "Demon framework" which will setup the the python side event handing, level editor, editor UI and other useful systems for you. All example code, demos and sample projects are also built using the "Demon framework", so its in best interest to use "Demon" instead of manually setting things up, to use the demon framework, create an instance of Demon class (or subclass it directly) and invoke its "run" method.

```
import sys, pathlib

editor_path = ".../DemonEngine/src"
path = str(pathlib.Path(editor_path))
sys.path.append(editor_path)

from demon import Demon


class DemonApp(Demon):
    def __init__(self, *args, **kwargs):
        Demon.__init__(self, *args, **kwargs)
        
        // your code here...


app = DemonApp()
app.run()
```

Demon class provides references to all the most common systems.

```
class DemonApp(Demon):
    def __init__(self, *args, **kwargs):
        Demon.__init__(self, *args, **kwargs)
        
        _ = self.engine            # panda3d engine
        _ = self.resource_manager  # resources handler
        _ = self.event_manager     # event manager
```

### 🔹Accessing systems
"Engine" class is the actual panda3D engine, it sets up and starts the underlying Panda3D systems including graphics window, input handling, events etc.

```
# -------------------------------------------------------------
# Engine class also provides reference to all the most common systems
# for example.

win = engine.win            # current graphics output window.

mouse_watcher_node = engine.mouse_watcher_node

dr3d = engine.dr3d          # 3d display region.
camera = engine.cam
render = engine.render

dr2d = engine.dr2d          # 2d display region.
cam2d = engine.cam2d
render2d = engine.render2d
aspect2d = engine.aspect2d  # aspect corrected 2d scene graph.

input_handler = engine.input_handler
resource_handler = engine.resource_handler
axis_grid = engine.axis_grid

# visit panda3d manual for explanation on these or
# visit the tutorials section or take a look at the sample
# programs.
# -------------------------------------------------------------
```

- ### Globals
   PandaEditor provides a utility class "Editor" to easily access various systems without the need to pass references around and this is also the recommended way to get access to various systems when programming in PandaEditor. 
   
   ```
	from editor import Editor


	class TestClass(object):
	    def __init__(self, *args, **kwargs):
	        object.__init__(self)
	        
	        demon = Editor.demon
	        engine = Editor.engine
	        resource_manager = Editor.resource_manager
	        event_manager = Editor.event_manager
   ```

### 🔹Event handling
- ### Handling default events

	To catch or listen to events sent from Panda3D or PandaEditor, set the event hook callback defined in engine class.
	
	```
	class DemonApp(Demon):
	    def __init__(self, *args, **kwargs):
	        Demon.__init__(self, *args, **kwargs)
	
	        self.engine.set_event_hook(self.event_handler)
	        
	     def event_handler(self, event, *args):
	        // make sure to call "on_any_event" base method first 
	        self.on_any_event(event, *args)
	```
	
	For most cases you will not need to manually set the event hook callback, the demon class already sets-up one and you only need to override it, make sure to also invoke the base method first.
	
	```
	class DemonApp(Demon):
	    def __init__(self, *args, **kwargs):
	        Demon.__init__(self, *args, **kwargs)
	        
	    def on_any_event(self, event, *args):
	       """event sent from c++ side can be handled here"""
	    
	       super().on_any_evt(evt, args)
	       
	       if event.name == "window_event":
	           // do something
	           pass
	```
	
	However, even in the case where you are manually setting the event hook callback, make sure to invoke the "on_any_event" base method first, this is necessary to handle events from PandaEditor side.

- ### Creating new events
	Creating new events is a simple two step process which involving, creating an event handler callback and registering it with the event manager object. The following code sample, registers an event "HandleMouseClick" and binds it to callback "on_mouse_click".
	
	```
	class DemonApp(Demon):
	    def __init__(self, *args, **kwargs):
	        Demon.__init__(self, *args, **kwargs)

	        self.event_manager.register("EventName", callback)
	        
	    def event_handler(self, *args):
	        pass
	```
		
	Once an event has been registered, it can be triggered by invoking "trigger" method of event_manager object, "trigger" function can also take an optional list of args and kwargs. 
	
	```
	self.event_manager.trigger("EventName")
	```


### 🔹Input handling
- ### Mouse utility class
  PandaEditor has a nice simple utility class "Mouse" to handle mouse's movement and some other related stuff, the code below lists most of its functions, see comments along the code for details.
  
  ```
  from demon import Demon
  from commons import Mouse
  
  
  class DemonApp(Demon):
      def __init__(self, *args, **kwargs):
	      Demon.__init__(self, *args, **kwargs)
	      
	      self.mouse = Mouse(self.engine)


	      # for mouse movement
          self.mouse.x  = 0   # mouse pos x
          self.mouse.y  = 0   # mouse pos y
          self.mouse.dx = 0   # mouse displacement x since last frame
          self.mouse.dy = 0   # mouse displacement y since last frame
  ```
   
- ### Keyboard and mouse
  Whenever a mouse or keyboard button is pressed, Panda3D generates events which can be handled using the event hook callback (see event handling section); whenever a button is pressed or released the following events are generated.
  1. An event object identified by the name of the button.
  2. An event object identified by the name of the button post-fixed by "-repeat" keyword as long as button is held down.
  3. An event object identified by the name of button post-fixed by "-up" keyword when the button is released.
  4. Raw key and raw key up events.
  
    To see which events are being generated whenever a keyboard or mouse button is pressed or released just override the "on_any_event" base method and print the name of the event.

    ```
    from demon import Demon


	class DemonApp(Demon):
	    def __init__(self, *args, **kwargs):
	        Demon.__init__(self, *args, **kwargs)
	
	    def on_any_evt(self, evt, *args):
	        """event sent from c++ side can be handled here"""
	        super().on_any_evt(evt, args)
	        print(evt.name)
    ```

	In should be noted that regardless of the status of caps lock event names are always lowercase. As an example, the following events are generated when "a" key is pressed, held for a second and released.
	
	  a, a-repeat....,a-up,

  Some physical keys are distinguished by their location on the keyboard, for example in addition to the regular "shift" event, pressing shift key generates separate "lshift" and "rshift" events for left and right shift keys respectively, as an example the following events are generated when shift key on left side of keyboard is pressed and released.

      shift, lshift   shift-up, lshift-up


  This however is not true for all keys, the best way to understand is by overriding the base "on_any_event" method and studying the events generated whenever an event is generated.

  Whenever a key is pressed while a modifier key _shift, control, alt, meta_ is held down the name of the modifier is prefixed to the name of the key for example the following events are generated when key "a" is pressed while modifier key "shift" is pressed,
 
 	  shift, shift-a, shift-a-repeat.......
 	  
 	 as soon as "a" or "shift" key is released regular up events will be generated.
 	 
 	 While an event based system is good for trigger based systems __for example lights on or off or play, pause or stop an animation or events generated upon collision detection__, however sometimes it is more desirable to ask Panda3D every frame for a particular event for example as in the case of character controllers or camera controllers etc. or any other system that require constant updates from user, as for the later case Panda3D provides mechanism through the [mouse watcher](https://docs.panda3d.org/1.10/cpp/reference/panda3d.core.MouseWatcher) to continuously detect user input. 
 	 
    ```
    from demon import Demon
    from panda3d.core import import KeyboardButton


	class DemonApp(Demon):
	    def __init__(self, *args, **kwargs):
	        Demon.__init__(self, *args, **kwargs)
	
 	    def on_update(self):
 	        is_down = __mouse_watcher_node.is_button_down
 	        
 	        if is_down(KeyboardButton.asciiKey("a")):
 	           // do something
    ```
 	 

~~To see some example usages of input handling see "AnimatedCharacter" and "ThirdPersonCamera" demo projects, the former is using events to change character animation and later is using the mouse watcher node's polling interface to update camera position.~~
	
### 🔹Managing continuously updating tasks
Managing tasks that needs continuous updating can be be done using Panda3D's _AsyncTaskanager_, creating a new task involves creating a new _AsyncTask_ object and registering it with _AsyncTaskManager_, the _AsyncTask_ encapsulates a unit of work, essentially a user defined callback method, which is then invoked continuously depending on its properties, various parameters for a task can be defined for example,

1. **Task Name:** A unique identifier for the task.
2. **Task Function:** The function or method that defines the task's behavior.
3. **Priority:** A numerical value determining the task's priority in the execution order.
4. **Execution Interval:** The time interval between successive updates of the task.
5. **Task Type:** Specifies whether the task should run once or loop continuously.

Each task or the callback method accepts _AsyncTask_ or _PythonTask_ as a compulsory first parameter, the _AsyncTask_ defines a _DoneStatus_ enumeration, the _DoneStatus_ enumeration allows a task to communicate its completion status to the _AsyncTaskManager_, the most common used status are;

- **DS_cont**: This status indicates that the task wishes to continue running and be scheduled for the next frame. It's suitable for tasks that loop continuously, such as ongoing animations or real-time updates.

- **DS_done:** The task signals that it has completed its execution and should be removed from the task manager. This is useful for tasks with a specific, one-time operation.

- **DS_again**: This status is employed when the task wants to be rescheduled for the next frame, even if it's a looping task. It's a way of explicitly indicating that the task needs to run again in the next frame.

Visit the [_AsyncTaskanager_](https://docs.panda3d.org/1.10/python/reference/panda3d.core.AsyncTaskManager#panda3d.core.AsyncTaskManager "_AsyncTaskanager_") API reference for more info on creating and using tasks. The code below shows some of the basics of creating and using tasks.

```
from panda3d.core import AsyncTaskManager, PythonTask


class DemonApp(Demon):
    def __init__(self, *args, **kwargs):
        Demon.__init__(self, *args, **kwargs)
        
        # create a task object
        task = PythonTask(self.task_callback, "TaskName")

        task.setSort(1)             # task with lower sort values are guaranteed
                                    # to be executed before tasks with higher
                                    # sort values

        task.setDelay(0.5)          # delay the task execution by specified time
                                    # after it has been added to task manager,
                                    # if this value is not
                                    # specified and by default task will be
                                    # executed in next frame following the one
                                    # in which it was added

        task.setUponDeath(callback) # callback function to be invoked when
                                    # this task finishes.

        # add it to the global task manager object
        AsyncTaskManager.getGlobalPtr().add(task)

     def task_callback(self, task):
     	if some_condition:
     	    # return task status as done, 
     	    # this task will not be called again next frame
     	    return task.DS_done 
     
        # continue running this task next frame
        return task.DS_cont
```


	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	