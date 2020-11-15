import __main__
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

    from android import loadingscreen
    loadingscreen.hide_loading_screen()

    print('Android language:', monospace.current_lang)
except ImportError:
    window_style = SDL_WINDOW_SHOWN
    print('We are not on android(?)')


desper.options['resource_extensions'] = False


CURRENT_DB_NAME = 'current.db'
CURRENT_DB_RES = 'current'


def main():
    SDL_Init(SDL_INIT_VIDEO)
    IMG_Init(IMG_INIT_PNG)
    Mix_Init(MIX_INIT_OGG)
    TTF_Init()

    chunk_size = 256 if monospace.on_android else 1024
    Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, chunk_size)

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
        .add_rule(monospace.get_score_importer(), monospace.ScoresHandle) \
        .build()

    dirs = [pt.join(pt.dirname(pt.abspath(__main__.__file__)), 'res')]
    model = dsdl.SDLGameModel(dirs, importer_dict, window, renderer)
    monospace.model = model

    model.res['game_world'] = monospace.GameWorldHandle(model.res)
    model.res['menu_world'] = monospace.MenuWorldHandle(model.res)
    model.res['pause_world'] = monospace.PauseWorldHandle(model.res)
    model.res['options_world'] = monospace.OptionsWorldHandle(model.res)
    model.res['death_world'] = monospace.DeathWorldHandle(model.res)
    model.res['name_world'] = monospace.NameSelectionWorldHandle(model.res)

    # Initialize migration module
    monospace.migration.main_db_path = model.res['db']['main'].filename

    # Create new db if necessary
    cur_db_filename = monospace.dump_main_db()
    model.res['db'][CURRENT_DB_RES] = monospace.DBHandle(cur_db_filename)

    # Migrate db if necessary
    monospace.upgrade_db(model.res['db'][CURRENT_DB_RES].get())

    # Apply options
    monospace.apply_options(model.res['db'][CURRENT_DB_RES].get())
    model.switch(model.res['menu_world'], stack=True)

    model.loop()


if __name__ == '__main__':
    main()
