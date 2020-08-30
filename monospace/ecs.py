import ctypes
import desper
import esper
import dsdl
import monospace
from sdl2 import *


DEFAULT_BULLET_SPEED = 15
DEFAULT_BULLET_DELAY = 15


class Ship(desper.AbstractComponent):
    """Main ship controller."""

    def __init__(self, position, bbox):
        self.position = position
        self.bbox = bbox
        self._old_x = position.x
        self._old_y = position.y
        self._old_pressing = False
        self._drag = False

        self.bullet_delay = DEFAULT_BULLET_DELAY
        self.bullet_speed = DEFAULT_BULLET_SPEED
        self._timer = 0

    def update(self, en, world, model):
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
            self.position.x += ((mouse_x.value - self._old_x)
                                * monospace.LOGICAL_WIDTH_RATIO)
            self.position.y += ((mouse_y.value - self._old_y)
                                * monospace.LOGICAL_WIDTH_RATIO)
            self._old_x, self._old_y = mouse_x.value, mouse_y.value

        self._old_pressing = pressing

        # Check collisions
        if self.check_collisions(world):
            print('colliding')

        # Shoot
        self._timer += 1
        if self._timer > self.bullet_delay:
            self.shoot(model, world)
            self._timer = 0

    def check_collisions(self, world):
        """Check for collisions with other bounding boxes."""
        for _, bbox in world.get_component(dsdl.BoundingBox):
            if bbox is not self.bbox and self.bbox.overlaps(bbox):
                return True

    def shoot(self, model, world):
        """Create a new bullet."""
        world.create_entity(model.res['text']['ship_bullet'].get(),
                            dsdl.Position(self.position.x, self.position.y,
                                          dsdl.Offset.BOTTOM_CENTER),
                            dsdl.Velocity(0, -self.bullet_speed))
