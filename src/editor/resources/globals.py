EDITOR_RESOURCES_PATH = ""

ICONS_PATH = "src/editor/resources/icons"

FOLDER_ICON = ICONS_PATH + "\\" + "folder16.png"
FILE_ICON = ICONS_PATH + "\\" + "ResourceTiles//file.png"
MODEL_ICON = ICONS_PATH + "\\" + "ResourceTiles//3d-model.png"
IMAGE_ICON = ICONS_PATH + "\\" + "ResourceTiles//image.png"
AUDIO_ICON = ICONS_PATH + "\\" + "ResourceTiles//audio.png"
VIDEO_ICON = ICONS_PATH + "\\" + "ResourceTiles//video.png"
PY_FILE_ICON = ICONS_PATH + "\\" + "ResourceTiles//python.png"
ED_PLUGIN_ICON = ICONS_PATH + "\\" + "ResourceTiles//plugin.png"
TXT_FILE = ICONS_PATH + "\\" + "ResourceTiles//txt.png"

# all supported extensions

EXTENSIONS = {"folder":  FOLDER_ICON,
              "generic": FILE_ICON,

              # model files
              "egg": MODEL_ICON,
              "bam": MODEL_ICON,
              "pz":  MODEL_ICON,
              "fbx": MODEL_ICON,
              "obj": MODEL_ICON,

              # image files
              "tiff": IMAGE_ICON,
              "tga":  IMAGE_ICON,
              "jpg":  IMAGE_ICON,
              "png":  IMAGE_ICON,
              "gif":  IMAGE_ICON,

              # other
              "py":  PY_FILE_ICON,
              "ed_plugin": ED_PLUGIN_ICON,
              "txt": TXT_FILE,

              # audio
              "mp3": AUDIO_ICON,
              "wav": AUDIO_ICON,

              # video
              ".mp4": VIDEO_ICON,
              }
