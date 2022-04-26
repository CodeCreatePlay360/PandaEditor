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

#### Currently PandaEditor is still in early alpha, a lot of important features are still missing including
* Action manager ( undo / redo system )
* Project management and scene save / reload system
* Some parts of code needs refactoring
* Making editor workflow more intuitive
* Currently GUI for inspector panel can only be automatically generated, this needs improvement so users can create custom inspectors using wxPython. 

#### Dependencies
1. WxPython
2. Python Watch dog

#### Install
1. clone / download this repo
2. run main.py

#### Attributions
PandaEditor is using the Gizmos package and InfoPanel from another open source panda3d project [link](https://github.com/Derfies/panda3d-editor).

### Support
PandaEditor is being developed and maintained by only one person, including writing documentation, if you found **PandaEditor** useful... help me buy some grapes and drinks for this summer, this matters a lot to me when I am coding or fixing bugs.

## Manual
* [Starting a new project](https://github.com/barbarian77/PandaEditor#starting-a-new-project "")
* [Assets management](https://github.com/barbarian77/PandaEditor#assets-management)
* [Object manipulation](https://github.com/barbarian77/PandaEditor#object-manipulation)
* [Runtime modules](https://github.com/barbarian77/PandaEditor#runtime-user-modules)
* [Editor plugins](https://github.com/barbarian77/PandaEditor#editor-plugins)
* [Other](https://github.com/barbarian77/PandaEditor#other)
* [Known issues](https://github.com/barbarian77/PandaEditor#known-issues)
* [Getting started](https://github.com/rehmanx/PandaEditor/blob/main/README.md#getting-started)

### Starting a new project
When you start PandaEditor a default project with some samples is setup for you.
Its located in current working directory and should not be deleted. You can use default project for any purpose, however to create a new project go to
**_Menubar > Project > Start New Project_** and choose a valid name and path.

### Assets management
* To import assets in your project go to **_Resource browser > ( select any folder) > Import Assets_**.
* In PandaEditor you can also append a folder outside of your current working project, to append an external folder go to **_Menubar > Project > AppendLibrary_**, editor will start monitoring changes to any appended directory, the appended assets exists in you project like any other imported assets.

### Object manipulation 
* alt + right mouse button to rotate
* alt + middle mouse to dolly
* alt + left mouse button drag to zoom

### Runtime user modules

![Image](images//module.png)

PandaEditor has two states, Editor and Game state. Editor state is for level design, object manipulation, creating user modules and defining behaviors etc. and game state is what you would expect as final game view.  
**Runtime user modules** are only executed in game state and are used to define behaviors of objects or nodepaths while in game state, any changes made to scene graph via user modules in game state are reverted as soon as game state is exited, . 
A user module in PandaEditor is basically a python file which the editor loads as an asset, however for the editor to consider this python file as PandaEditor's user module,
* The python file should contain a class with same name as of python file.
* Class should inherit from PModBase.

Basic syntax of a **PandaEditor** user module

```
from editor.core.pModBase import PModBase


class CharacterController(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)
        # __init__ should not contain anything except for variable declaration...!

    def on_start(self):
        # this method is called only once
        pass

    def on_update(self):
        # this method is called every frame
        pass
```

To create a new user module **_Resource Browser > Project > ( select a folder, left click to open context menu ) > Add > UserModule_**.  
To see some example usages of user modules, see samples included with default project.  

### Editor plugins
Editor plugins are executed both in editor and game state. They also inherit from **PModBase**, can be used to create tools and extend editor.  
To see some example usages of editor plugins, see samples included with default project.  

### Other
1. PandaEditor can also load and display **.txt** files, just import **.txt** files in your project like any other asset. 
  ![Image](images//text_file.png)

### Known issues
### Getting started
To get started, there are samples included with the default project, a more comprehensive getting started section will soon be created.  

( **_currently PandaEditor is in early alpha, you cannot save a scene, so for each sample you will have to create the scene, it's as simple as loading one or two models, instructions to setup a scene are included as a readme.txt file in each sample folder_**  ).  
( **_By default the python modules in each samples are set to not execute automatically in GameMode, to enable them select a module and from inspector panel check shouldStart variable_**  )