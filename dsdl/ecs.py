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
        for en, (tex, pos) in self.world.get_components(
                ctypes.POINTER(SDL_Texture), Position):
            w, h = ctypes.c_int(), ctypes.c_int()
            SDL_QueryTexture(tex, None, None, w, h)

            offset_x = 0
            offset_y = 0
            if pos.offset == Offset.CENTER:
                offset_x = w.value // 2
                offset_y = h.value // 2
            if pos.offset == Offset.BOTTOM_CENTER:
                offset_x = w.value // 2
                offset_y = h.value - 1
            elif isinstance(pos.offset, (list, tuple)):
                offset_x, offset_y = pos.offset

            src = None
            dest = SDL_Rect(round(pos.x - offset_x), round(pos.y - offset_y),
                            w.value, h.value)

            animation = self.world.try_component(en, Animation)
            if animation is not None:
                animation.update()
                src = SDL_Rect(
                    animation.cur_frame * w.value // animation.frames, 0,
                    w.value // animation.frames, h)
                dest.w = w.value // animation.frames

            SDL_RenderCopy(model.renderer, tex, src, dest)


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
            elif bbox.offset == Offset.BOTTOM_CENTER:
                offset_x = bbox.w // 2
                offset_y = bbox.h - 1
            elif isinstance(bbox.offset, (list, tuple)):
                offset_x, offset_y = bbox.offset

            # Update position of bbox
            bbox.x = pos.x - offset_x
            bbox.y = pos.y - offset_y


class FPSLoggerProcessor(esper.Processor):
    """Log to stdout the current FPS."""

    def __init__(self):
        self._time = SDL_GetTicks()

    def process(self, *args):
        cur_time = SDL_GetTicks()
        delta = cur_time - self._time
        fps = 1000 / max(0.1, delta)
        print('FPS', fps)

        self._time = cur_time


class BoundingBoxRendererProcessor(esper.Processor):
    """Show bounding boxes on screen."""

    def process(self, model):
        for _, bbox in self.world.get_component(BoundingBox):
            SDL_SetRenderDrawColor(model.renderer, 255, 0, 0, 255)
            if bbox.x is not None and bbox.y is not None:
                rect = SDL_Rect(round(bbox.x), round(bbox.y), round(bbox.w),
                                round(bbox.h))
                SDL_RenderDrawRect(model.renderer, rect)


class Offset(Enum):
    CENTER = 'center'
    ORIGIN = 'origin'
    BOTTOM_CENTER = 'bottom_center'


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

    def __init__(self, offset=Offset.ORIGIN, w=0, h=0):
        self.x = None
        self.y = None
        self.w = w
        self.h = h

        if isinstance(offset, (list, tuple)) and len(offset) != 2:
            raise TypeError('Please provide two values for an offset(x, y)')
        elif not isinstance(offset, (list, tuple)) and not isinstance(offset,
                                                                      Offset):
            raise TypeError('The given offset should be of type dsdl.Offset, \
                             or of type list/tuple providing two values(x, y)')

        self.offset = offset

    def overlaps(self, bbox):
        """Check for the collision between this box and a given one."""
        if (self.x is None or self.y is None or bbox.x is None
                or bbox.y is None):
            return False

        if (bbox.x >= self.x + self.w or self.x >= bbox.x + bbox.w
                or bbox.y >= self.y + self.h or self.y >= bbox.y + bbox.h):
            return False
        return True


class Animation:
    """Component that describes an animation.

    This has to be coupled with an SDL_Texture that represents an
    animation(horizontal spritesheet, borders/offsets in the sheet
    aren't supported).
    """

    def __init__(self, frames=1, delay=1, start_frame=0):
        self.frames = frames
        self.delay = delay

        self.cur_frame = start_frame
        self._counter = delay

    def update(self):
        self._counter -= 1
        if self._counter <= 0:
            self._counter = self.delay
            self.cur_frame = (self.cur_frame + 1) % self.frames
