from enum import Enum, unique
from panda3d.core import BitMask32


ED_CAMERA_MASK = BitMask32.bit(0)
GAME_CAMERA_MASK = BitMask32.bit(1)


@unique
class LightType(Enum):
    Point = 0
    Directional = 1
    Spot = 2
    Ambient = 3
