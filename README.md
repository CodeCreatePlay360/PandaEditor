## A level editor for Panda3d game engine with bare minimum features to provide an editor centric workflow.

![Image](images//00.gif)
![Image](images//01.png)

#### Current features include
1. Object manipulation
2. Support for runtime user modules 
3. Editor plugin support
4. Properties panel 
5. File browser
6. Console panel

#### Attributions
PandaEditor is using the Gizmos package and InfoPanel from another open source panda3d project [link](https://github.com/Derfies/panda3d-editor).

## Support
**Maintaining PandaEditor and keeping it bug free takes a lot of time and effort, not to mention writing documentation and creating sample programs, so if you found PandaEditor useful in any way than consider supporting it on [Patreon](https://www.patreon.com/PandaEditor_?fan_landing=true) page.**

#### Dependencies
1. Panda3d
2. WxPython
3. Python WatchDog

#### Install
1. Clone / download this repository
2. Run main.py

## Manual
* [Starting a new project](https://github.com/barbarian77/PandaEditor#starting-a-new-project "")
* [Assets management](https://github.com/barbarian77/PandaEditor#assets-management)
* [Object manipulation](https://github.com/barbarian77/PandaEditor#object-manipulation)
* [Runtime modules](https://github.com/barbarian77/PandaEditor#runtime-user-modules)
* [Editor plugins](https://github.com/barbarian77/PandaEditor#editor-plugins)
* [Other](https://github.com/barbarian77/PandaEditor#other)
* [Known issues](https://github.com/barbarian77/PandaEditor#known-issues)
* [Getting started](https://github.com/barbarian77/PandaEditor#getting-started)
* [Tutorials]

### Starting a new project
PandaEditor has a project based workflow, when you first start PandaEditor a default project with some sample programs is setup for you.
Its located in current working directory and should not be deleted. You can use default project for any purpose, however to create a new project
**Menubar > Project > Start New Project** and choose a valid name and path.

### Resource management
* To import resources in your project go to **Resource browser > ( select any folder) > Import Resources**.
* In PandaEditor you can also append a folder outside of your current working project, to append an external folder go to **Menubar > Project > AppendLibrary ( and select the folder containing resources you want to append for your project )**, editor will start monitoring changes to any appended directory, the appended resources exists in you project like any other imported resources.

### Hot keys 
* **alt + right mouse button** to rotate
* **alt + middle mouse** to dolly
* **alt + left mouse button drag** to zoom
* **control + D** to duplicate selected objects
* **X key** to remove / delete selected objects
* **control + z** to undo

### Runtime modules

![Image](images//module.png)

PandaEditor has two states **EditorState** and **GameState**.  
The **EditorState** is your scene creation state, this is where you would set up your 2D or 3D scenes, write **runtime modules** and define object behaviors.  
The object behaviors defined using **runtime modules** during editor state are executed in **GameState**, the game state is also what you would expect as final game view.  
**Runtime modules** are simple python scripts, they are automatically loaded as resources, however for editor to consider any python script as a **runtime module**,

* The class name should be exactly same as that of python file.
* Class should inherit from **RuntimeModule** base class.

Basic syntax of a **PandaEditor's runtime module**.

```
from editor.core.runtimeModule import RuntimeModule


class CharacterController(RuntimeModule):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)
        # __init__ should not contain anything except for variable declaration...!

    def on_start(self):
        # this method is called only once
        pass

    def on_update(self):
        # this method is called every frame
        pass
```

The **RuntimeModule** base class also extends any user defined **runtime modules** with some base methods and attributes, the base attributes act as a link between PandaEditor and Panda3D engine. 

```
from editor.core.runtimeModule import RuntimeModule


class CharacterController(RuntimeModule):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)
        # __init__ should not contain anything except for variable declaration...!
        
        win = self._win                                # the window we are rendering into currently
        mouse_watcher_node = self._mouse_watcher_node  # mouse watcher node
        render = self._render                          # this is the current scene's parent node-path
        game = self._game                              # instance of current running game
        self.accept("x", self.on_x)                    # basic Panda3d event handling
        
    def on_start(self):
        # this method is called only once
        pass

    def on_update(self):
        # this method is called every frame
        pass
        
```

To get a complete listing of all base methods and attributes see **Basics.py** in sample programs included with default project.  
To create a new user module **Resource Browser > Add > RuntimeModule**.  
To see some example usages of user modules, see samples programs also included with the default project.  

### Editor plugins
To extend the editor with custom tools and features PandaEditor has support for editor plugins, unlike **runtime modules** editor plugins are only executed in in **EditorState**, their execution is paused in **GameState**, the execution is resumed as soon as **EditorState** is enabled again.  
Same as **runtime modules**, **the editor plugins** are python scripts, for the editor to consider any python script as an **editor plugin**,

* The class name should be exactly same as that of python file.
* Class should inherit from **EditorPlugin** base class.

Basic syntax of an editor plugin.

```
from editor.core.editorPlugin import EditorPlugin


class EdPlugin(EditorPlugin):
    def __init__(self, *args, **kwargs):
        EditorPlugin.__init__(self, *args, **kwargs)
        
        # request a separate wxPython panel for this 
        # plugin instead of default inspector.
        # However is this case you are responsible ofr
        # create editor UI yourself.
        self.request_unique_panel("MyFirstPanel")

    # on_start method is called once
    def on_start(self):
        pass

    # update method is called every frame
    def on_update(self):
        pass
```
 
And just like **runtime modules** the **EditorPlugin** base class also extends any user defined **editor plugins** with some base methods and attributes, the base attributes act as a link between **PandaEditor**, **wxPython** and the **Panda3D engine**. 

```
from editor.core.editorPlugin import EditorPlugin


class EdPlugin(EditorPlugin):
    def __init__(self, *args, **kwargs):
        EditorPlugin.__init__(self, *args, **kwargs)

    # on_start method is called once
    def on_start(self):
        win = self._win
        mouse_watcher_node = self._mouse_watcher_node
        render = self._render
        le = self._le              # level editor
        wx_panel = self._wx_panel  # the top most parent "Panel" of wxPython, if request to unique panel is
                                   # successful, otherwise return value of self._wx_panel is None.
                                   # All wx UI elements should be child of this.
```

To see an example usage of **editor plugins**, see **SampleEdPlugin.py** included with sample programs.

### Other
1. PandaEditor can also load plain text files as a resource, just import or create a new **.txt** file in your project like any other resource.  
Click on any **.txt** files to display their contents in the **InspectorTab**. 
  ![Image](images//text_file.png)

### Known issues

### Getting started
To get started, there are samples included with the default project, for a more step by step instructions go to tutorials section. 

*****
## Tutorials
### @ Part 01 HelloWorld
1. In this very first intoduction, we will create a basic rotating cube.
2. Open PandaEditor & create a new runtime module **ResourceBrowser > Add > Runtime module** name it **_RotatingCube_**, open this file in explorer **ResourceBrowser > ShowInExplorer** and open it up in any python editor.
3. We need two things **A reference to the cube and a rotation speed** so add them first

```
import math
import panda3d.core as p3dCore
from editor.core.runtimeModule import RuntimeModule


class RotatingCube(RuntimeModule):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)

        self.cube = None  # reference to cube
        self.rotateSpeed = 10
``` 

The public attributes of a script can be inspected and modified via **InspectorPanel**

  ![Image](images//Tut_HelloWorld/01.png)

4. From the **SceneGraphPanel** rename the default cube to **RotatingCube**, and update the **on_start** method to get a reference to it

  ![Image](images//Tut_HelloWorld/02.png)

```
class RotatingCube(RuntimeModule):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)

        self.cube = None  # reference to cube
        self.rotateSpeed = 10

    def on_start(self):
        self.cube = self._render.find("**/RotatingCube")  # find the cube in scene graph
```

5. To rotate this cube we will change its heading ( rotation around z-axis ) every frame, this can be done in **on_update** method, this method is called every frame as long as editor is in **GameState**.

```
    def on_update(self):
        if self.cube:
            h = self.cube.getH()
            h += self.rotateSpeed * globalClock.getDt()
            if h > 360:
                h = 0
            self.cube.setH(h)
```

**globalClock.getDt()** is a Panda3d global, it is the time elapsed since last frame.

6. Enter **GameState** to see cube rotating in action.
  ![Image](images//Tut_HelloWorld/03.gif) 