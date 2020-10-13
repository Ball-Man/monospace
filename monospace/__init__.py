"""Subpackage containing specific features for the Monospace game."""

from .res import *
from .game import *
from .locale import *
from .globals import *
from .waves import *
from .powerups import *
from .enemies import *
from .menu import *
from .score import *
from .migration import *

import sdl2 as _sdl

# Define logical size based on real screen size
DISPLAY_MODE = _sdl.SDL_DisplayMode()

LOGICAL_WIDTH = 800
LOGICAL_WIDTH_RATIO = 0
LOGICAL_HEIGHT = 0


def init_screen_resolution():
    global DISPLAY_MODE, LOGICAL_WIDTH_RATIO, LOGICAL_HEIGHT

    if on_android:
        _sdl.SDL_GetCurrentDisplayMode(0, DISPLAY_MODE)
    else:
        DISPLAY_MODE = SDL_DisplayMode(0, 600, 1000)

    LOGICAL_WIDTH_RATIO = LOGICAL_WIDTH / DISPLAY_MODE.w
    LOGICAL_HEIGHT = int(LOGICAL_WIDTH_RATIO * DISPLAY_MODE.h)
