import json
import ctypes
import os.path as pt
import desper
import dsdl
import sdl2
import sdl2.sdlimage as image
import sdl2.sdlttf as ttf


def log_importer(root, rel, res):
    print(root, rel, res)


def get_texture_importer():
    return desper.get_resource_importer('text', ('.png'))


def get_font_importer():
    return desper.get_resource_importer('fonts', ('.json'))


def get_fontcache_importer():
    lambd = desper.get_resource_importer('str', ('.json'))

    def decorated_lambda(root, rel, res):
        ret = lambd(root, rel, res)
        if ret is None:
            return None

        ret = list(ret)
        ret.append(res)

        return ret

    return decorated_lambda


class TextureHandle(desper.Handle):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def _load(self):
        text = image.IMG_LoadTexture(dsdl.SDLGameModel.default_renderer,
                                     self.filename.encode())

        w, h = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_QueryTexture(text, None, None, ctypes.byref(w),
                              ctypes.byref(h))

        text.w = w.value
        text.h = h.value

        return text


class FontHandle(desper.Handle):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def _load(self):
        with open(self.filename) as file:
            font_dict = json.load(file)

        filename = pt.join(pt.dirname(self.filename), font_dict['filename'])
        return ttf.TTF_OpenFont(filename.encode(), font_dict['size'])


class FontCacheHandle(desper.Handle):
    """Caches rendered text on textures, and serves them on request."""

    def __init__(self, filename, res):
        super().__init__()
        self.filename = filename
        self.res = res
        self._fallback = None   # Relative path to the handler to be
                                # used when a key isn't found in this
                                # one.

    def _load(self):
        with open(self.filename) as file:
            tot_dict = json.load(file)

        self._fallback = tot_dict.get('fallback')
        string_dict = tot_dict['strings']

        for key, dic in string_dict.items():
            if dic.get('color') is not None:
                color = [int(dic['color'][i:i + 2], 16)
                         for i in range(0, len(dic['color']), 2)]
            else:
                color = 0xFF, 0xFF, 0xFF, 0xFF
            surface = ttf.TTF_RenderText_Blended(
                self.res['fonts'][dic['font']].get(),
                str(dic['text']).encode(), sdl2.SDL_Color(*color))
            dic['texture'] = sdl2.SDL_CreateTextureFromSurface(
                dsdl.SDLGameModel.default_renderer, surface)

            w, h = ctypes.c_int(), ctypes.c_int()
            sdl2.SDL_QueryTexture(dic['texture'], None, None, w, h)
            dic['texture'].w = w.value
            dic['texture'].h = h.value

            sdl2.SDL_FreeSurface(surface)

        return string_dict

    def get_texture(self, key):
        """Get a cached texture, given the key."""
        value = self.get()

        # Fallback
        if value.get(key) is None and self._fallback is not None:
            fallback = _res_from_path(self.res, self._fallback)
            return fallback.get_texture(key)

        # This will raise a KeyError if both the fallback
        # is None and the key doesn't exist
        return value[key]['texture']


def _res_from_path(res, path):
    """Get a resource from the given dict and path(/ divided)."""
    if not desper.options['resource_extensions']:
        path = pt.splitext(path)[0]

    dic = res
    for part in path.split('/'):
        dic = dic[part]

    return dic
