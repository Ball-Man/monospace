import ctypes
import desper
from sdl2 import *


class SDLGameModel(desper.GameModel):
    default_renderer = None

    def __init__(self, dirs, importer_dict, window, renderer=None):
        self.window = window

        if renderer is None:
            renderer = SDL_CreateRenderer(window, -1,
                                          SDL_RENDERER_ACCELERATED
                                          | SDL_RENDERER_PRESENTVSYNC)
        self.renderer = renderer

        w, h = ctypes.c_int(), ctypes.c_int()
        SDL_RenderGetLogicalSize(renderer, w, h)

        # Setup buffer texture
        self.window_texture = SDL_CreateTexture(
            renderer, SDL_PIXELFORMAT_RGBA8888,
            SDL_TEXTUREACCESS_TARGET, w, h)
        SDL_SetRenderTarget(renderer, self.window_texture)

        if SDLGameModel.default_renderer is None:
            SDLGameModel.default_renderer = self.renderer

        super().__init__(dirs, importer_dict)
