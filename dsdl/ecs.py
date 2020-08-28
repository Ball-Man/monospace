import ctypes
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
            dest = SDL_Rect(pos.x - pos.offset_x, pos.y - pos.offset_y,
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


class Position:
    """Positional component(used for rendering/collisions)."""

    def __init__(self, x=0, y=0, offset_x=0, offset_y=0):
        self.x = x
        self.y = y
        self.offset_x = offset_x
        self.offset_y = offset_y


class Velocity:
    """Velocity vector.

    This vector will update the position vector(if present) by the
    VelocityProcessor.
    """

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
