<h1 align="center">Panda3DEditor</h1>

<p align="center"><b> PandaEditor is an open-source level editor for the Panda3D game engine, it is designed to be easy to use and extend and provides end users with a convenient interface and tools to quickly prototype and create 2D or 3D scenes.</b></p> 

<h3 align="center">Features</h3>

* Easy object manipulation 
* Object inspection
* Console panel
* Scene graph browser
* Resources browser
* Project based approach
* Complete scripting support that exposes full underlying engine's API, scripts can be attached directly to nodes in scene graph (entity component system) defining per object behaviors or you can also program in a more traditional way in which you usually have one main function as the entry point to the rest of your program.
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
<a href='https://discord.gg/WZBFcpW3Mf' target="_blank"><img alt='Discord' src='https://img.shields.io/badge/Discord-5865F2?style=plastic&logo=discord&logoColor=white'/></a>
<a href='https://www.patreon.com/panda3deditor' target="_blank"><img alt='Patreon' src='https://img.shields.io/badge/Sponsor-F96854?style=plastic&logo=patreon&logoColor=white'/></a>
<a href='https://github.com/CodeCreatePlay360/PandaEditor' target="_blank"><img alt='Unity' src='https://img.shields.io/badge/Reddit-FF4500?style=plastic&logo=reddit&logoColor=white'/></a>
<a href='https://github.com/CodeCreatePlay360/PandaEditor' target="_blank"><img alt='Unity' src='https://img.shields.io/badge/YouTube-FF0000?style=plastic&logo=youtube&logoColor=white'/></a>
</p>

### 🔹Requirements
  1. Panda3D game engine.

### 🔹Getting Started

For now there is no executable to start PandaEditor, you will have to manually start it by running 'main.py' python script, located in the root of PandaEditor directory.

```
ppython main.py
```

Additionally, you can provide optional project path command line argument (projpath), the path should be a valid 'PandaEditor project folder or empty folder, other a default project is used.

```
ppython main.py projpath 'Path to your project'
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
To showcase the diverse functionalities of Panda3D and PandaEditor, there are demo projects included in 'demos' folder. These projects are extensively commented, serving as valuable references for your own endeavors. Starting any project is straightforward, simply start the 'main.py' Python script with optional '-d' flag followed by the name of the desired demo project.

```
python main.py -d NameOfDemoProject
```

For example to run the 'AnimatedCharacter' demo project, use the following command.

```
python main.py -d AnimatedCharacter
```

~~To see more information on a particular demo there is a "readme file" along with each demo in "src/demos" folder; here is a list of all demos.~~
1. ~~RoamingRalph~~
2. ~~AnimatedCharacter~~
3. ~~ThirdPersonCamera~~
4. ~~ThirdPersonCharacterController~~



<h2 align="center"> <a href="https://github.com/CodeCreatePlay360/PandaEditor/tree/main?tab=readme-ov-file#-%EF%B8%8F-programmers-section-">Programmers Section</a> | <a href="">Artists Section</a> </h2>

### ▪️ Programming Basics
- Starting the editor
- Accessing systems
- Event handling
  - Handling default events
  - Creating new events
- Input handling
- Managing continuously updating tasks

***

### 🔹Starting the editor

The recommended way to start PandaEditor is through the 'main.py' script, see [Getting started]() section. However if you want to manually set things up, you can use the builtin 'Demon' framework which automatically initializes and sets up the Panda3D engine, Python-side event handling, scripting, level editor, editor UI, and other systems for you. This sample code below shows a basic initialization of 'Demon' framework.

```
import sys, pathlib

editor_path = ".../PandaEditor/src"
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

See the included 'main.py, demon.py and engine.py' scripts located in 'src' folder, for more info on this.

### 🔹Scripting
While manually setting things up can offer more flexibility for advanced users, it is often overkill for most projects. The built-in 'Scripting' framework usually suffices and provides a much simpler interface and workflow, making it the recommended approach for programming in PandaEditor. Moreover, almost all the documentation and most of the sample projects are also built around the 'Scripting' framework.

### 🔹Accessing systems
PandaEditor provides a utility class 'Systems' to easily access various systems without the need to pass references around and this is also the recommended way to get access to various systems when programming in PandaEditor. 
   
   ```
	from game.system import Systems
	
	
	demon     = Systems.demon
    win       = Systems.win
    mwn       = Systems.mwn  # mouse watcher node

    dr        = Systems.dr3d
    render    = Systems.render
    cam       = Systems.cam

    dr2d      = Systems.dr2d
    render2d  = Systems.render2d
    aspect2d  = Systems.aspect2d
    cam2d     = Systems.cam2d

    evt_mgr   = Systems.event_manager
    resources = Systems.resource_manager
   ```

'Engine' class is the actual Panda3D engine, it sets up and starts the underlying Panda3D systems including graphics window, input handling, C++ side of events etc.

```
# -------------------------------------------------------------
# Engine class provides reference to all the engine related systems

win = engine.win            # current graphics output window.

mwn = engine.mwn            # mouse watcher node

dr3d = engine.dr3d          # 3d display region.
camera = engine.cam         #
render = engine.render      #

dr2d = engine.dr2d          # 2d display region.
cam2d = engine.cam2d        # 2d camera
render2d = engine.render2d  # 2d render
aspect2d = engine.aspect2d  # aspect corrected 2d scene graph.

input_handler = engine.input_handler
resource_handler = engine.resource_manager
axis_grid = engine.axis_grid

# visit panda3d manual for explanation on these or
# visit the tutorials section or take a look at the sample
# programs.
# -------------------------------------------------------------
```

### 🔹Event handling
- ### Handling default events

	To catch or listen to events sent from Panda3D or PandaEditor, override the
	
	```
    def on_any_event(self, event, *args):
       """event sent from c++ side can be handled here"""

       if event.name == "window-event":
           print('Window resized or re-positioned.')
	```

- ### Creating new events
	Creating new events is a simple two step process which involves creating an event handler method and registering it with the event manager object. The following code sample, registers an event 'HandleMouseClick' and binds it to callback 'on_mouse_click'.
	
	```
    event_manager.register("HandleMouseClick", handle_mouse_click)


    def handle_mouse_click(self, *args):
        pass
	```
		
	Once an event has been registered, it can be triggered using the 'trigger' method of 'event_manager' object, optionally, this function can also take a list of arguments and keyword arguments.
	
	```
	event_manager.trigger("EventName")
	```


### 🔹Input handling
- ### Mouse utility class
  PandaEditor provides a simple utility class 'Mouse' to handle mouse's movement and some other related stuff, the code below lists some of its functions, see comments along the code for details.
  
  ```
  from commons import Mouse


  self.mouse = Mouse(self.engine)

  # for mouse movement
  self.mouse.x   # mouse pos x
  self.mouse.y   # mouse pos y
  self.mouse.dx  # mouse displacement x since last frame
  self.mouse.dy  # mouse displacement y since last frame
  ```
   
- ### Keyboard and mouse
  Whenever a keyboard or mouse button is pressed, held down for more than one frame or released the following events are generated.
  1. An event object identified by the name of the button.
  2. An event object identified by the name of the button post-fixed by "-repeat" keyword as long as the button is held down.
  3. An event object identified by the name of button post-fixed by "-up" keyword when the button is released.
  4. Raw key and raw key up events.
  
    These events are to be handled in 'on_any_event' base method of P3D modules; To see which events are being generated by Panda3D, override the 'on_any_event' base method and print the name of the event.

    ```
    def on_any_event(self, event, *args):
        """event sent from c++ side can be handled here"""

        if event.name == "a":
        	print("Keyboard button 'a' pressed.")
    ```

	In should be noted that regardless of the status of caps lock, event names are always lowercase. As an example, the following events are generated when _a_ key is pressed, held for a second and released.
	
	  a, a-repeat...., a-up,

  Some physical keys are distinguished by their location on the keyboard, for example in addition to the regular 'shift' event, holding down 'shift' key generates separate 'lshift' and 'rshift' events for left and right shift keys respectively, as an example the following events are generated when shift key on left side of keyboard is pressed and released.

      shift, lshift   shift-up, lshift-up


  This however is not true for all keys, the best way to understand is by overriding the base 'on_any_event' method and studying the events generated whenever an event is generated.

  Whenever a key is pressed while a modifier key 'shift, control, alt, meta' is held down, the name of the modifier key is prefixed to the name of the key for example the following events are generated when key 'a' is pressed while modifier key 'shift' is pressed,
 
 	  shift-a, shift-a-repeat.......
 	  
 	 as soon as 'a' or 'shift' key is released regular up events will be generated.
 	 
 	 While an event based system is good for trigger based logic. for example 'lights on or off or play, pause or stop an animation or events generated upon collision detection', however sometimes it is more convenient to ask Panda3D every frame for a particular event for example as in the case of character controllers or camera controllers etc. or any other system that require constant updates from user, as for the later case Panda3D provides mechanism through the [mouse watcher](https://docs.panda3d.org/1.10/cpp/reference/panda3d.core.MouseWatcher) data node to continuously detect user input. 
 	 
    ```	
    from panda3d.core import KeyboardButton


    def on_update(self):
        is_down = mouse_watcher_node.is_button_down

        if is_down(KeyboardButton.asciiKey("a")):
        	print("Keyboard button 'a' is pressed.")
    ```
 	 

~~To see some example usages of input handling see "AnimatedCharacter" and "ThirdPersonCamera" demo projects, the former is using events to change character animation and later is using the mouse watcher node's polling interface to update camera position.~~
	
### 🔹Managing continuously updating tasks
Managing tasks that needs continuous updating can be be done using Panda3D's [AsyncTaskanager](https://docs.panda3d.org/1.10/python/reference/panda3d.core.AsyncTaskManager), creating a new task involves creating a new [AsyncTask](https://docs.panda3d.org/1.10/python/reference/panda3d.core.AsyncTask#panda3d.core.AsyncTask) object and registering it with 'AsyncTaskManager', the 'AsyncTask' encapsulates a unit of work, essentially a user defined method, which is then invoked continuously depending on its properties, various parameters for a task can be defined for example.

1. **Task Name:** A unique identifier for the task.
2. **Task Function:** The function or method that defines the task's behavior.
3. **Priority:** A numerical value determining the task's priority in the execution order.
4. **Execution Interval:** The time interval between successive updates of the task.
5. **Task Type:** Specifies whether the task should run once or loop continuously.

Each task or the callback method accepts 'AsyncTask' or 'PythonTask' as a compulsory first parameter, the 'AsyncTask' defines a 'DoneStatus' enumeration, the 'DoneStatus' enumeration allows a task to communicate its completion status to the 'AsyncTaskManager', the most common used status are;

- **DS_cont**: This status indicates that the task wishes to continue running and be scheduled for the next frame. It's suitable for tasks that loop continuously, such as ongoing animations or real-time updates.

- **DS_done:** The task signals that it has completed its execution and should be removed from the task manager. This is useful for tasks with a specific, one-time operation.

- **DS_again**: This status is employed when the task wants to be rescheduled for the next frame, even if it's a looping task. It's a way of explicitly indicating that the task needs to run again in the next frame.

Visit the [AsyncTaskanager](https://docs.panda3d.org/1.10/python/reference/panda3d.core.AsyncTaskManager#panda3d.core.AsyncTaskManager "AsyncTaskanager") API reference for more info on creating and using tasks. The code below shows some of the basics of creating and using tasks.

```
from panda3d.core import AsyncTaskManager, PythonTask


# create a task object
task = PythonTask(self.task, "TaskName")

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

def task(task):
   if some_condition:
      # return task status as done, 
      # this task will not be called again next frame
      return task.DS_done 

   # continue running this task next frame
   return task.DS_cont
```