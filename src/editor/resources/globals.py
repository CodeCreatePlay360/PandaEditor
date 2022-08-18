EDITOR_RESOURCES_PATH = ""

ICONS_PATH = "src/editor/resources/icons"

FOLDER_ICON_BLUE = ICONS_PATH + "\\" + "folder16.png"
LIB_FOLDER_ICON = ICONS_PATH + "\\" + "libFolderIcon.png"

Music_icon = ICONS_PATH + "\\" + "ResourceTiles//music.png"
Video_icon = ICONS_PATH + "\\" + "ResourceTiles//video.png"

# all supported extensions
EXTENSIONS = {"generic": Music_icon,

              # model files
              "egg":  Music_icon,
              "bam":  Music_icon,
              "pz":   Music_icon,
              # "fbx":  MODEL_ICON,
              "obj":  Music_icon,
              # "gltf": MODEL_ICON,

              # image files
              "tiff": Music_icon,
              "tga":  Music_icon,
              "jpg":  Music_icon,
              "png":  Music_icon,

              # other
              "py":  Music_icon,
              "ed_plugin": Music_icon,
              "txt": Music_icon,

              # audio
              "mp3": Music_icon,
              "wav": Music_icon,

              # video
              ".mp4": Music_icon,
              }
