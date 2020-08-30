import __main__
import os.path as pt
from sdl2 import *
from sdl2.sdlimage import *
import monospace
import desper
import dsdl

try:
    window_style = SDL_WINDOW_FULLSCREEN

    from android import loadingscreen
    loadingscreen.hide_loading_screen()

    print('Android language:', monospace.current_lang)
except ImportError:
    window_style = SDL_WINDOW_FULLSCREEN
    print('We are not on android(?)')


desper.options['resource_extensions'] = False


def main():
    SDL_Init(SDL_INIT_VIDEO)
    IMG_Init(IMG_INIT_PNG)

    monospace.init_screen_resolution()

    SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b'1')

    window = SDL_CreateWindow(b'monospace', SDL_WINDOWPOS_CENTERED,
                              SDL_WINDOWPOS_CENTERED, monospace.DISPLAY_MODE.w,
                              monospace.DISPLAY_MODE.h, window_style)
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED
                                              | SDL_RENDERER_PRESENTVSYNC)

    SDL_RenderSetLogicalSize(renderer, monospace.LOGICAL_WIDTH,
                             monospace.LOGICAL_HEIGHT)

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
