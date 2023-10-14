import panda3d.core as p3d_core

EDITOR_STATE = 0
GAME_STATE = 1

Viewport_Mode_Editor = 0
Viewport_Mode_Game = 1

MAX_COMMANDS_COUNT = 20  # maximum number of undo redo commands

ED_GEO_MASK = p3d_core.BitMask32.bit(0)
GAME_GEO_MASK = p3d_core.BitMask32.bit(1)

# -----------------------------------------------------------------------------------------------
# PATHS
DEFAULT_PROJECT_PATH = ""
EDITOR_PATH = ""

FILE_EXTENSIONS_ICONS_PATH = "src/editor/resources/icons/fileExtensions"  # icons path for resource browser file extensions
ICONS_PATH = "src/editor/resources/icons"  # icons path for editor icons
MODELS_PATH = "src/editor/resources/models"  # directory to look for default models (editor lights, camera, default objects etc.)

CUBE_PATH = MODELS_PATH + "/Cube.egg"
CYLINDER_PATH = MODELS_PATH + "/Cylinder.egg"
CAPSULE_PATH = MODELS_PATH + "/Capsule.egg"
SPHERE_PATH = MODELS_PATH + "/Sphere.egg"
PLANE_PATH = MODELS_PATH + "/Plane.egg"

# -----------------------------------------------------------------------------------------------
# all supported extensions
ALL_SUPPORTED_FORMATS = ["egg", "bam", "pz", "obj", "glb", "gltf",
                         "tiff", "tga", "jpg", "png",
                         "py", "txt",
                         "mp3", "wav", "mp4"]

MODEL_FORMATS = ["egg", "bam", "pz", "obj", "glb", "gltf"]
IMAGE_FORMATS = ["tiff", "tga", "jpg", "png"]
MUSIC_FORMATS = ["mp3", "wav"]
VIDEO_FORMATS = ["mp4"]

# -----------------------------------------------------------------------------------------------
EDITOR_RELOAD_DELAY = 2
