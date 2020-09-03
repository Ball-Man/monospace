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

        text.w = w
        text.h = h

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
