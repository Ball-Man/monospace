import ctypes
from enum import Enum
import esper
from sdl2 import *


class EventHandlerProcessor(esper.Processor):
    """Processor for events from SDL(quit on SDL_Quit)."""

    def process(self, model, *args):
        event = SDL_Event()
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                model.quit = True
                break


class TextureRendererProcessor(esper.Processor):
    """Processor that renders SDL_Textures(in pair with Position)."""

    def process(self, model, *args):
        for _, (tex, pos) in self.world.get_components(
                ctypes.POINTER(SDL_Texture), Position):
            w, h = ctypes.c_int(), ctypes.c_int()
            SDL_QueryTexture(tex, None, None, w, h)

            offset_x = 0
            offset_y = 0
            if pos.offset == Offset.CENTER:
                offset_x = w.value // 2
                offset_y = h.value // 2
            elif isinstance(pos.offset, (list, tuple)):
                offset_x, offset_y = pos.offset

            dest = SDL_Rect(pos.x - offset_x, pos.y - offset_y,
                            w.value, h.value)

            SDL_RenderCopy(model.renderer, tex, None, dest)


class ScreenClearerProcessor(esper.Processor):
    """Processor that cleans the screen and renders the backbuffer."""

    def process(self, model, *args):
        SDL_RenderPresent(model.renderer)

        SDL_SetRenderDrawColor(model.renderer, 0, 0, 0, 255)
        SDL_RenderClear(model.renderer)


class VelocityProcessor(esper.Processor):
    """Processor that updates position according to velocity."""

    def process(self, *args):
        for _, (pos, vel) in self.world.get_components(Position, Velocity):
            pos.x += vel.x
            pos.y += vel.y


class BoundingBoxProcessor(esper.Processor):
    """Processor that updates BoundingBox x and y, based on Position."""

    def process(self, *args):
        for _, (pos, bbox) in self.world.get_components(Position, BoundingBox):

            # Calculate offset
            offset_x = 0
            offset_y = 0
            if bbox.offset == Offset.CENTER:
                offset_x = bbox.w // 2
                offset_y = bbox.h // 2
            elif isinstance(bbox.offset, (list, tuple)):
                offset_x, offset_y = bbox.offset

            # Update position of bbox
            bbox.x = pos.x - offset_x
            bbox.y = pos.y - offset_y


class Offset(Enum):
    CENTER = 'center'
    ORIGIN = 'origin'


class Position:
    """Positional component(used for rendering/collisions).

    Possible values for 'offset' come from
    """

    def __init__(self, x=0, y=0, offset=Offset.ORIGIN):
        self.x = x
        self.y = y

        if isinstance(offset, (list, tuple)) and len(offset) != 2:
            raise TypeError('Please provide two values for an offset(x, y)')
        elif not isinstance(offset, Offset):
            raise TypeError('The given offset should be of type dsdl.Offset, \
                             or of type list/tuple providing two values(x, y)')

        self.offset = offset


class Velocity:
    """Velocity vector.

    This vector will update the position vector(if present) by the
    VelocityProcessor.
    """

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class BoundingBox:
    """Rectangle representing a collision bounding box."""

    def __init__(self, offset, w=0, h=0):
        self.x = 0
        self.y = 0
        self.w = w
        self.h = h

        if isinstance(offset, (list, tuple)) and len(offset) != 2:
            raise TypeError('Please provide two values for an offset(x, y)')
        elif not isinstance(offset, Offset):
            raise TypeError('The given offset should be of type dsdl.Offset, \
                             or of type list/tuple providing two values(x, y)')

        self.offset = offset

    def overlaps(self, bbox):
        """Check for the collision between this box and a given one."""
        if (bbox.x >= self.x + self.w or self.x >= bbox.x + bbox.w
                or bbox.y >= self.y + self.h or self.y >= bbox.y + bbox.h):
            return False
        return True
