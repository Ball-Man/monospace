import __main__
import os.path as pt
from sdl2 import *
from sdl2.sdlimage import *
import monospace
import desper
import dsdl

internal_storage = '.'
image_file = 'rect.png'

try:
    from android.storage import app_storage_path
    #
except ImportError:
    print('We are not on android(?)')


desper.options['resource_extensions'] = False


def main():
    SDL_Init(SDL_INIT_VIDEO)
    IMG_Init(IMG_INIT_PNG)

    display_mode = SDL_DisplayMode()
    SDL_GetCurrentDisplayMode(0, display_mode)

    window = SDL_CreateWindow(b'Test game', SDL_WINDOWPOS_CENTERED,
                              SDL_WINDOWPOS_CENTERED, display_mode.w,
                              display_mode.h, SDL_WINDOW_FULLSCREEN)
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED
                                              | SDL_RENDERER_PRESENTVSYNC)

    importer_dict = desper.importer_dict_builder \
        .add_rule(dsdl.get_texture_importer(), dsdl.TextureHandle) \
        .build()

    dirs = [pt.join(pt.dirname(pt.abspath(__main__.__file__)), 'res')]
    model = dsdl.SDLGameModel(dirs, importer_dict, window, renderer)

    model.res['game_world'] = monospace.GameWorldHandle(model.res)
    model.switch(model.res['game_world'])

    model.loop()


if __name__ == '__main__':
    main()
