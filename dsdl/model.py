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

        self.last_world_handle = None

        super().__init__(dirs, importer_dict)

    def switch(self, room_handle, reset=False):
        self.last_world_handle = self.current_world_handle

        super().switch(room_handle, reset)
