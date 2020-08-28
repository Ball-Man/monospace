import desper
import dsdl
import sdl2.sdlimage as image


def log_importer(root, rel, res):
    print(root, rel, res)


def get_texture_importer():
    return desper.get_resource_importer('text', ('.png'))


class TextureHandle(desper.Handle):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def _load(self):
        return image.IMG_LoadTexture(dsdl.SDLGameModel.default_renderer,
                                     self.filename.encode())
