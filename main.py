import __main__
import shutil
import os.path as pt
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *
from sdl2.sdlmixer import *
import monospace
import desper
import dsdl

try:
    window_style = SDL_WINDOW_FULLSCREEN

    from android.storage import app_storage_path
    from android import loadingscreen
    loadingscreen.hide_loading_screen()

    print('Android language:', monospace.current_lang)
except ImportError:
    window_style = SDL_WINDOW_SHOWN
    print('We are not on android(?)')


desper.options['resource_extensions'] = False


CURRENT_DB_NAME = 'current.db'
CURRENT_DB_RES = 'current'

APP_DB_PATH = app_storage_path() if monospace.on_android else None


def main():
    SDL_Init(SDL_INIT_VIDEO)
    IMG_Init(IMG_INIT_PNG)
    Mix_Init(MIX_INIT_OGG)
    TTF_Init()

    Mix_OpenAudio(MIX_DEFAULT_FREQUENCY, MIX_DEFAULT_FORMAT, 2, 2048)

    monospace.init_screen_resolution()

    SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b'1')

    if monospace.on_android:
        window = SDL_CreateWindow(b'monospace', SDL_WINDOWPOS_UNDEFINED,
                                  SDL_WINDOWPOS_UNDEFINED,
                                  monospace.DISPLAY_MODE.w,
                                  monospace.DISPLAY_MODE.h, window_style)
    else:
        window = SDL_CreateWindow(b'monospace', SDL_WINDOWPOS_CENTERED,
                                  SDL_WINDOWPOS_CENTERED,
                                  monospace.DISPLAY_MODE.w,
                                  monospace.DISPLAY_MODE.h, window_style)

    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED
                                              | SDL_RENDERER_PRESENTVSYNC)

    SDL_RenderSetLogicalSize(renderer, monospace.LOGICAL_WIDTH,
                             monospace.LOGICAL_HEIGHT)

    importer_dict = desper.importer_dict_builder \
        .add_rule(dsdl.get_texture_importer(), dsdl.TextureHandle) \
        .add_rule(dsdl.get_font_importer(), dsdl.FontHandle) \
        .add_rule(dsdl.get_fontcache_importer(), dsdl.FontCacheHandle) \
        .add_rule(monospace.get_db_importer(), monospace.DBHandle) \
        .add_rule(dsdl.get_chunk_importer(), dsdl.ChunkHandle) \
        .add_rule(dsdl.get_mus_importer(), dsdl.MusicHandle) \
        .build()

    dirs = [pt.join(pt.dirname(pt.abspath(__main__.__file__)), 'res')]
    model = dsdl.SDLGameModel(dirs, importer_dict, window, renderer)
    monospace.model = model

    model.res['game_world'] = monospace.GameWorldHandle(model.res)
    model.res['menu_world'] = monospace.MenuWorldHandle(model.res)
    model.res['pause_world'] = monospace.PauseWorldHandle(model.res)
    model.res['options_world'] = monospace.OptionsWorldHandle(model.res)
    model.res['death_world'] = monospace.DeathWorldHandle(model.res)
    model.switch(model.res['menu_world'])

    Mix_PlayMusic(model.res['mus']['too_much'].get(), -1)

    # Generate db if empty or version is obsolete
    if monospace.on_android:
        new_db_filename = pt.join(APP_DB_PATH, CURRENT_DB_NAME)
    else:
        db_filename = model.res['db']['main'].filename
        db_dirname = pt.dirname(db_filename)
        new_db_filename = pt.join(db_dirname, CURRENT_DB_NAME)

    if not pt.isfile(new_db_filename):
        print('Current db not found, instantiating')
        shutil.copy2(db_filename, new_db_filename)

    model.res['db'][CURRENT_DB_RES] = monospace.DBHandle(new_db_filename)

    # Apply options
    monospace.apply_options(model.res['db'][CURRENT_DB_RES].get())

    model.loop()


if __name__ == '__main__':
    main()
