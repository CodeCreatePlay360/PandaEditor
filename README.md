## An open source level / scene editor for Panda3d

![Image](images//01.png)

**Panda3d is one of best open source game engines out there, but lack of a proper scene editor and tools for artists limits its scope and target audience, this project aims to make Panda3d more intuitive to use for artists and game developers by providing an editor centric workflow**.  
It has all the basic features of a level editor including

* Object manipulation
* Object Inspection
* Console panel
* Project based approach
* Scene graph
* Resources browser
* To extend the editor, there is a complete support for **editor plugins**, the developers can create ( or maybe even sell ) their tools.

> If you found PandaEditor useful in any way, than consider giving it a star on GitHub.

#### Attributions
PandaEditor is using the Gizmos package and InfoPanel from another open source project [link](https://github.com/Derfies/panda3d-editor).

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
* [Tutorials](https://github.com/barbarian77/PandaEditor#tutorials)

### Starting a new project
PandaEditor has a project based workflow, when you first start PandaEditor a default project with some sample programs is setup for you.
Its located in current working directory and should not be deleted. You can use default project for any purpose, to create a new project
**Menubar > Project > Start New Project** and choose a valid name and path.

### Resource management
* To import resources ( models, textures, shaders etc. ) in your project go to **Resource browser > ( select any folder) > Import Resources**.
* You can also append a folder outside of your current working project, **Menubar > Project > AppendLibrary ( and select the folder containing resources you want to append for your project )**, editor will start monitoring changes to any appended directory, the appended resources exists in you project like any other imported resources.

### Hot keys 
* **alt + right mouse button** to rotate
* **alt + middle mouse** to dolly
* **alt + left mouse button drag** to zoom
* **control + D** to duplicate selected objects
* **X** to remove / delete selected objects
* **control + z** to undo

### Runtime modules

![Image](images//02.png)

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

The **RuntimeModule** also defines some base methods and attributes which act as the link between PandaEditor and Panda3D engine. 

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
To extend the editor with custom tools and features PandaEditor has support for editor plugins, unlike **runtime modules** editor plugins are executed only in **EditorState**.
Same as with **runtime modules**, **the editor plugins** are python scripts and for the editor to consider any python script as an **editor plugin**,

* The class name should be exactly same as that of python file.
* Class should inherit from **EditorPlugin** base class.

Basic syntax of an editor plugin.

```
from editor.core.editorPlugin import EditorPlugin


class EdPlugin(EditorPlugin):
    def __init__(self, *args, **kwargs):
        EditorPlugin.__init__(self, *args, **kwargs)

    # on_start method is called once
    def on_start(self):
        pass

    # update method is called every frame
    def on_update(self):
        pass
```
 
And just like **runtime modules** the **EditorPlugin** base class also defines some base attributes and methods and act as a link between **PandaEditor**, **wxPython** and the **Panda3D engine**. 

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
        le = self._le  # level editor
```

To see an example usage of **editor plugins**, see **SampleEdPlugin.py** included with sample programs.

### Other
1. PandaEditor can also load plain text files as a resource, just import or create a new **.txt** file in your project like any other resource.  
Click on any **.txt** files to display their contents in the **InspectorTab**. 
  ![Image](images//03.png)

### Known issues

### Getting started
To get started, there are samples included with the default project, for a more step by step instructions go to tutorials section. 

*****
## Tutorials
