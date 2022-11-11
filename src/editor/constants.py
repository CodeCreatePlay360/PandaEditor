import panda3d.core as p3d_core

# -----------------------------------------------------------------------------------------------
EDITOR_STATE = 0
GAME_STATE = 1

Viewport_Mode_Editor = 0
Viewport_Mode_Game = 1

EditorPlugin = "__EditorPlugin__"
RuntimeModule = "__RuntimeModule__"
Component = "__Component__"
TAG_GAME_OBJECT = "__TAG_GAME_OBJECT__"

MAX_COMMANDS_COUNT = 20  # maximum number of undo redo commands

ED_GEO_MASK = p3d_core.BitMask32.bit(0)
GAME_GEO_MASK = p3d_core.BitMask32.bit(1)
# **********************************************************************************************


# -----------------------------------------------------------------------------------------------
# PATHS
DEFAULT_PROJECT_PATH = "src/Default Project"  # default project path

FILE_EXTENSIONS_ICONS_PATH = "src/editor/resources/icons/fileExtensions"  # icons path for resource browser file extensions
ICONS_PATH = "src/editor/resources/icons"  # icons path for editor icons

MODELS_PATH = "src/editor/resources"  # directory to look for default models (editor lights, camera, default objects etc.)

POINT_LIGHT_MODEL = MODELS_PATH + "/" + "models/Pointlight.egg.pz"
DIR_LIGHT_MODEL = MODELS_PATH + "/" + "models/Dirlight.egg"
SPOT_LIGHT_MODEL = MODELS_PATH + "/" + "models/Spotlight.egg.pz"
AMBIENT_LIGHT_MODEL = MODELS_PATH + "/" + "models/AmbientLight.obj"
CAMERA_MODEL = MODELS_PATH + "/" + "models/camera.egg.pz"

CUBE_PATH = MODELS_PATH + "/" + "models/cube.fbx"
CAPSULE_PATH = MODELS_PATH + "/" + "models/capsule.fbx"
CONE_PATH = MODELS_PATH + "/" + "models/cone.fbx"
PLANE_PATH = MODELS_PATH + "/" + "models/plane.fbx"
# **********************************************************************************************


# -----------------------------------------------------------------------------------------------
# NodePath IDS
NODEPATH = "__NodePath__"
ACTOR_NODEPATH = "__ActorNodePath__"
POINT_LIGHT = "__PointLight__"
DIRECTIONAL_LIGHT = "__DirectionalLight__"
SPOT_LIGHT = "__SpotLight__"
AMBIENT_LIGHT = "__AmbientLight__"
CAMERA_NODEPATH = "__CameraNodePath__"
# **********************************************************************************************


# -----------------------------------------------------------------------------------------------
# All Supported file types
MODEL_EXTENSIONS = ["egg", "bam", "pz", "glb", "gltf"]
TEXTURE_EXTENSIONS = ["tiff", "tga", "jpg", "png"]
OTHER_EXTENSIONS = []
# **********************************************************************************************
