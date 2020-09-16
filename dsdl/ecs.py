import ctypes
import math
from enum import Enum
import dsdl
import esper
from sdl2.sdlgfx import *
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

            offset_x, offset_y = pos.get_offset(w.value * pos.size_x,
                                                h.value * pos.size_y)
            offset_x, offset_y = int(offset_x), int(offset_y)

            src = None
            dest = SDL_Rect(round(pos.x - offset_x), round(pos.y - offset_y),
                            int(w.value * pos.size_x),
                            int(h.value * pos.size_y))

            animation = self.world.try_component(en, Animation)
            if animation is not None:
                animation.update()
                src = SDL_Rect(
                    animation.cur_frame * w.value // animation.frames, 0,
                    w.value // animation.frames, h)
                dest.w = w.value // animation.frames

            if pos.rot == 0:
                SDL_RenderCopy(model.renderer, tex, src, dest)
            else:
                center = SDL_Point(offset_x, offset_y)
                SDL_RenderCopyEx(model.renderer, tex, src, dest, pos.rot,
                                 center, SDL_FLIP_NONE)


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
        for _, (pos, bbox) in self.world.get_components(dsdl.Position,
                                                        dsdl.BoundingBox):

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


class CollisionCircleProcessor(esper.Processor):
    """Processor that updates CollisionCircle x and y, based on Position."""

    def process(self, *args):
        for _, (pos, circle) in self.world.get_components(
                dsdl.Position, dsdl.CollisionCircle):
            # Update position of bbox
            circle.x = pos.x
            circle.y = pos.y


class ParticleProcessor(esper.Processor):
    """Processor that manages Particle components.

    A particle will be recognized as such if the following components
    are found: Particle, Position.

    Optionally a Velocity component may be defined(will be updated
    accordingly to the Particle component).
    """

    def process(self, *args):
        for en, (part, pos) in self.world.get_components(
                Particle, Position):

            # Check for the particle's lifetime, destroy if dead
            part.life_left -= 1
            if part.life_left <= 0:
                self.world.delete_entity(en)

            # Apply size changes to the position
            pos.size_x = max(0, pos.size_x + part.size_inc)
            pos.size_y = max(0, pos.size_y + part.size_inc)

            # Apply rotation changes to the position
            pos.rot = (pos.rot + part.rot_inc) % 360

            # Optionally update the velocity component
            velocity = self.world.try_component(en, Velocity)
            if velocity is not None:
                angle = math.atan2(velocity.y, velocity.x)
                velocity.x += math.cos(angle) * part.vel_inc
                velocity.y += math.sin(angle) * part.vel_inc


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
        for _, bbox in self.world.get_component(dsdl.BoundingBox):
            SDL_SetRenderDrawColor(model.renderer, 255, 0, 0, 255)
            if bbox.x is not None and bbox.y is not None:
                rect = SDL_Rect(round(bbox.x), round(bbox.y), round(bbox.w),
                                round(bbox.h))
                SDL_RenderDrawRect(model.renderer, rect)

        for _, circle in self.world.get_component(dsdl.CollisionCircle):
            if circle.x is not None and circle.y is not None:
                aacircleRGBA(model.renderer, int(circle.x), int(circle.y), int(circle.rad),
                             255, 0, 0, 255)


class Offset(Enum):
    CENTER = 'center'
    ORIGIN = 'origin'
    BOTTOM_CENTER = 'bottom_center'


class Position:
    """Positional component(used for rendering/collisions).

    Possible values for 'offset' come from the Offset enum. Also a tuple
    or list representing a couple of values is accepted.

    size_x and size_y are multipliers for the texture dimensions(
    relative to the offset).

    rot is in degrees(clockwise).
    """

    def __init__(self, x=0, y=0, offset=Offset.ORIGIN, size_x=1, size_y=1,
                 rot=0):
        self.x = x
        self.y = y
        self.size_x = size_x
        self.size_y = size_y
        self.rot = rot

        if isinstance(offset, (list, tuple)) and len(offset) != 2:
            raise TypeError('Please provide two values for an offset(x, y)')
        elif not isinstance(offset, (list, tuple)) and not isinstance(offset,
                                                                      Offset):
            raise TypeError('The given offset should be of type dsdl.Offset, \
                             or of type list/tuple providing two values(x, y)')

        self.offset = offset

    def get_offset(self, w, h):
        """Get a couple of values representing the punctual offset.

        This method is designed to be used when Position.offset is
        an Offset instance. This will transform the given Offset type in
        actual values, dynamically calculating them given the w and h.
        """
        if self.offset == Offset.ORIGIN:
            return 0, 0
        elif self.offset == Offset.CENTER:
            return w // 2, h // 2
        elif self.offset == Offset.BOTTOM_CENTER:
            return w // 2, h - 1
        elif isinstance(self.offset, (tuple, list)):
            return self.offset


class Velocity:
    """Velocity vector.

    This vector will update the position vector(if present) by the
    VelocityProcessor.
    """

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


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


class Particle:
    """Particle component, defining particle ranges(size, rot, etc)."""

    def __init__(self, lifetime, size_inc=0, vel_inc=0, rot_inc=0):
        self.lifetime = lifetime
        self.size_inc = size_inc
        self.vel_inc = vel_inc
        self. rot_inc = rot_inc

        self.life_left = lifetime
