"""Desper module for SDL2(pysdl2)."""

from .res import *
from .model import *
from .ecs import *
from .collisions import *
from .finger import *
from .akeyboard import *

try:
    import android
    SCANCODE_BACK = 270     # Android backbutton
except ImportError:
    import sdl2
    SCANCODE_BACK = sdl2.SDL_SCANCODE_ESCAPE
