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

        if SDLGameModel.default_renderer is None:
            SDLGameModel.default_renderer = self.renderer

        super().__init__(dirs, importer_dict)
