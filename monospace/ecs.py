import ctypes
import desper
import esper
from sdl2 import *


class Ship(desper.AbstractComponent):
    """Main ship controller."""

    def __init__(self, position):
        self.position = position
        self._old_x = position.x
        self._old_y = position.y
        self._old_pressing = False
        self._drag = False

    def update(self, model, world, en):
        mouse_x, mouse_y = ctypes.c_int(), ctypes.c_int()
        pressing = (SDL_GetMouseState(ctypes.byref(mouse_x),
                                     ctypes.byref(mouse_y))
                    & SDL_BUTTON(SDL_BUTTON_LEFT))

        # Start drag
        if pressing and not self._old_pressing:
            self._drag = True
            self._old_x, self._old_y = mouse_x.value, mouse_y.value
        elif not pressing and self._old_pressing:   # Stop drag
            self._drag = False

        if self._drag:
            self.position.x += mouse_x.value - self._old_x
            self.position.y += mouse_y.value - self._old_y
            self._old_x, self._old_y = mouse_x.value, mouse_y.value

        self._old_pressing = pressing
