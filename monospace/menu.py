import ctypes
import dsdl
import monospace
import esper
from sdl2 import *


class ButtonProcessor(esper.Processor):
    """Processor that manages button presses."""

    def __init__(self):
        self._old_pressed = False

    def process(self, _):
        mouse_x, mouse_y = ctypes.c_int(0), ctypes.c_int(0)
        if (SDL_GetMouseState(mouse_x, mouse_y)
                & SDL_BUTTON(SDL_BUTTON_LEFT)):
            pressed = True
        else:
            pressed = False

        mouse_x = mouse_x.value * monospace.LOGICAL_WIDTH_RATIO
        mouse_y = mouse_y.value * monospace.LOGICAL_WIDTH_RATIO

        for _, (bbox, button) in self.world.get_components(
                dsdl.BoundingBox, Button):

            # Check if the the bounding box is hit
            if (bbox.x <= mouse_x <= (bbox.x + bbox.w)
                and bbox.y <= mouse_y <= (bbox.y + bbox.h)
                    and pressed and not self._old_pressed):

                button.action()

        self._old_pressed = pressed


class Button:
    """Component that incapsulates the behaviour of a button.

    It's designed to be used with BoundingBoxes. When the BoundingBox
    is pressed, the command contained in the button is fired.
    """

    def __init__(self, action):
        self.action = action
