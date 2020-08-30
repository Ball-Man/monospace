"""Subpackage containing specific features for the Monospace game."""

from .res import *
from .ecs import *
from .locale import *

import sdl2 as _sdl

# Define logical size based on real screen size
DISPLAY_MODE = _sdl.SDL_DisplayMode()

LOGICAL_WIDTH = 800
LOGICAL_WIDTH_RATIO = 0
LOGICAL_HEIGHT = 0


def init_screen_resolution():
    global DISPLAY_MODE, LOGICAL_WIDTH_RATIO, LOGICAL_HEIGHT

    _sdl.SDL_GetCurrentDisplayMode(0, DISPLAY_MODE)

    LOGICAL_WIDTH_RATIO = LOGICAL_WIDTH / DISPLAY_MODE.w
    LOGICAL_HEIGHT = int(LOGICAL_WIDTH_RATIO * DISPLAY_MODE.h)
