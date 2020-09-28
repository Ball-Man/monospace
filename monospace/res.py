import sqlite3
import desper
import dsdl
import monospace
from sdl2 import *


class MenuWorldHandle(desper.Handle):
    """Handle class that creates the main menu world."""

    def __init__(self, res):
        super().__init__()
        self.res = res

    def _load(self):
        w = desper.AbstractWorld()

        # Add processors
        w.add_processor(dsdl.EventHandlerProcessor(), 10)
        w.add_processor(dsdl.FillRectangleRenderProcessor(), -0.5)
        w.add_processor(dsdl.TextureRendererProcessor(), -1)
        w.add_processor(dsdl.ScreenClearerProcessor(), -2)
        w.add_processor(dsdl.BoundingBoxProcessor())
        w.add_processor(monospace.ButtonProcessor())
        w.add_processor(desper.CoroutineProcessor())

        #w.add_processor(dsdl.BoundingBoxRendererProcessor())

        # Create entities
        start_width = 400
        start_height = 100
        pos_y = 300
        w.create_entity(
            monospace.Button(
                monospace.split_button_action(self.res['game_world'])),
            dsdl.BoundingBox(dsdl.Offset.CENTER, w=start_width,
                             h=start_height),
            dsdl.Position(monospace.LOGICAL_WIDTH // 2, pos_y,
                          dsdl.Offset.CENTER),
            dsdl.FillRectangle(monospace.LOGICAL_WIDTH // 2 - start_width / 2,
                               pos_y - start_height / 2, start_width,
                               start_height, SDL_Color()),
            monospace.model.res['str'][monospace.current_lang] \
                .get_texture('start')
            )

        # Ship
        ship_pos = dsdl.Position(monospace.LOGICAL_WIDTH // 2,
                                 monospace.LOGICAL_HEIGHT / 10 * 9,
                                 offset=dsdl.Offset.CENTER)
        w.create_entity(ship_pos, self.res['text']['ship'].get())

        return w


class GameWorldHandle(desper.Handle):
    """Handle class that creates the main game world."""

    def __init__(self, res):
        super().__init__()
        self.res = res

    def _load(self):
        w = desper.AbstractWorld()

        # Add processors
        w.add_processor(dsdl.EventHandlerProcessor(), 10)
        w.add_processor(dsdl.TextureRendererProcessor(), -1)
        w.add_processor(dsdl.ScreenClearerProcessor(), -2)
        w.add_processor(monospace.GameProcessor())
        w.add_processor(desper.AbstractProcessor())
        w.add_processor(dsdl.VelocityProcessor())
        w.add_processor(dsdl.BoundingBoxProcessor())
        w.add_processor(dsdl.CollisionCircleProcessor())
        w.add_processor(monospace.EntityCleanerProcessor())
        w.add_processor(dsdl.ParticleProcessor())
        w.add_processor(desper.CoroutineProcessor())
        w.add_processor(monospace.ButtonProcessor())

        #w.add_processor(dsdl.FPSLoggerProcessor())
        #w.add_processor(dsdl.BoundingBoxRendererProcessor(), -1.5)

        # Create entities
        # Ship
        ship_pos = dsdl.Position(monospace.LOGICAL_WIDTH // 2,
                                 monospace.LOGICAL_HEIGHT / 10 * 9,
                                 offset=dsdl.Offset.CENTER)
        ship_bbox = dsdl.BoundingBox(dsdl.Offset.CENTER, 64, 64)
        w.create_entity(monospace.Ship(ship_pos, ship_bbox), ship_pos,
                        ship_bbox, self.res['text']['ship'].get())

        # Pause button
        pause_text = self.res['text']['pause'].get()
        w.create_entity(pause_text,
                        dsdl.Position(
                            monospace.LOGICAL_WIDTH - 30 - pause_text.w,
                            30),
                        dsdl.BoundingBox(w=pause_text.w, h=pause_text.h),
                        monospace.Button(monospace.pause_game)
                        )

        return w


class PauseWorldHandle(desper.Handle):
    """Handle for the pause menu world."""

    def __init__(self, res):
        super().__init__()
        self.res = res

    def _load(self):
        w = desper.AbstractWorld()

        # Processors
        w.add_processor(dsdl.EventHandlerProcessor(), 10)
        w.add_processor(dsdl.TextureRendererProcessor(), -1)
        w.add_processor(dsdl.ScreenClearerProcessor(), -2)
        w.add_processor(dsdl.BoundingBoxProcessor())
        w.add_processor(monospace.ButtonProcessor())
        w.add_processor(desper.CoroutineProcessor())

        # Entities
        resume_text = self.res['text']['resume'].get()
        w.create_entity(resume_text,
                        monospace.Button(monospace.resume_game),
                        dsdl.BoundingBox(dsdl.Offset.CENTER,
                                         w=resume_text.w * 1.5,
                                         h=resume_text.h * 1.5),
                        dsdl.Position(monospace.LOGICAL_WIDTH / 2,
                                      monospace.LOGICAL_HEIGHT / 2,
                                      dsdl.Offset.CENTER)
                        )
        return w


class OptionsWorldHandle(desper.Handle):
    """Handle for the options world."""

    def __init__(self, res):
        super().__init__()
        self.res = res

    def _load(self):
        w = desper.AbstractWorld()

        # Processors
        w.add_processor(dsdl.EventHandlerProcessor(), 10)
        w.add_processor(dsdl.FillRectangleRenderProcessor(), -0.5)
        w.add_processor(dsdl.TextureRendererProcessor(), -1)
        w.add_processor(dsdl.ScreenClearerProcessor(), -2)
        w.add_processor(dsdl.BoundingBoxProcessor())
        w.add_processor(monospace.ButtonProcessor())
        w.add_processor(desper.CoroutineProcessor())

        offset_x = 30

        # Entities
        # Music setting
        w.create_entity(
            dsdl.Position(offset_x, 100),
            self.res['str'][monospace.current_lang].get_texture('music'))

        w.create_entity(
            dsdl.Position(0, 0),
            dsdl.BoundingBox(w=200, h=200),
            dsdl.FillRectangle(0, 0, 200, 200, SDL_Color()),
            monospace.Button(monospace.toggle_option('music')))

        # Sfx setting
        w.create_entity(
            dsdl.Position(offset_x, 200),
            self.res['str'][monospace.current_lang].get_texture('sfx'))

        save_text = self.res['str'][monospace.current_lang].get_texture('save')
        save_width = save_text.w + 30
        save_height = save_text.h + 30
        w.create_entity(
            monospace.Button(
                monospace.split_button_action(self.res['menu_world'])),
            dsdl.Position(offset_x + save_width / 2, 300 + save_height / 2,
                          offset=dsdl.Offset.CENTER),
            save_text,
            dsdl.FillRectangle(offset_x, 300, save_width, save_height,
                               SDL_Color()),
            dsdl.BoundingBox(dsdl.Offset.CENTER, save_width, save_height)
            )

        return w


def get_db_importer():
    return desper.get_resource_importer('db', ('.db'))


class DBHandle(desper.Handle):

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def _load(self):
        return sqlite3.connect(self.filename)
