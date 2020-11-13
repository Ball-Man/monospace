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
        w.add_processor(desper.AbstractProcessor())
        w.add_processor(dsdl.BoundingBoxProcessor())
        w.add_processor(dsdl.VelocityProcessor())
        w.add_processor(monospace.ButtonProcessor())
        w.add_processor(desper.CoroutineProcessor())
        w.add_processor(monospace.MainQuitProcessor())

        #w.add_processor(dsdl.BoundingBoxRendererProcessor())

        # Create entities
        w.create_entity(monospace.EventChecker())

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

        w.create_entity(
            monospace.Button(lambda e, w, m: m.switch(m.res['options_world'],
                                                      True)),
            dsdl.BoundingBox(dsdl.Offset.CENTER, w=start_width,
                             h=start_height),
            dsdl.Position(monospace.LOGICAL_WIDTH // 2, 400,
                          dsdl.Offset.CENTER),
            monospace.model.res['str'][monospace.current_lang] \
                .get_texture('options')
            )

        # Ship selection
        ship_pos = dsdl.Position(monospace.LOGICAL_WIDTH // 5 * 4,
                                 monospace.LOGICAL_HEIGHT / 10 * 9,
                                 offset=dsdl.Offset.CENTER, alpha=127)
        w.create_entity(ship_pos,
                        monospace.SelectionShip(),
                        monospace.Button(monospace.SelectShipAction()),
                        dsdl.Velocity(),
                        dsdl.BoundingBox(dsdl.Offset.CENTER, 100, 100))

        ship_pos = dsdl.Position(monospace.LOGICAL_WIDTH // 5,
                                 monospace.LOGICAL_HEIGHT / 10 * 9,
                                 offset=dsdl.Offset.CENTER, alpha=127)
        w.create_entity(ship_pos,
                        monospace.SelectionShip(),
                        monospace.Button(monospace.SelectShipAction()),
                        dsdl.Velocity(),
                        dsdl.BoundingBox(dsdl.Offset.CENTER, 100, 100))

        ship_pos = dsdl.Position(monospace.LOGICAL_WIDTH // 2,
                                 monospace.LOGICAL_HEIGHT / 10 * 9,
                                 offset=dsdl.Offset.CENTER)
        w.create_entity(ship_pos, self.res['text']['ships']['default'].get(),
                        monospace.ShipSelector(), monospace.SelectionShip(),
                        monospace.Button(monospace.SelectShipAction()),
                        dsdl.Velocity(),
                        dsdl.BoundingBox(dsdl.Offset.CENTER, 100, 100))

        # Apply options
        w.create_entity(monospace.HaltMusic())
        monospace.apply_options(self.res['db']['current'].get())

        # My name
        name = self.res['str'][monospace.current_lang].get_texture('ballman')
        w.create_entity(
            name,
            dsdl.Position(30, monospace.LOGICAL_HEIGHT - name.h))

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
        w.add_processor(monospace.EnemyProcessor())
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
                        ship_bbox, self.res['text']['ships']['default'].get())

        # Pause button
        pause_text = self.res['text']['pause'].get()
        w.create_entity(pause_text,
                        dsdl.Position(
                            monospace.LOGICAL_WIDTH - 30 - pause_text.w,
                            30),
                        dsdl.BoundingBox(w=pause_text.w, h=pause_text.h),
                        monospace.Button(monospace.pause_game)
                        )

        # w.create_entity(dsdl.Position(-25, 100, dsdl.Offset.CENTER),
        #                 dsdl.Velocity(),
        #                 monospace.ShooterEnemy(),
        #                 self.res['text']['enemies']['shooter'].get(),
        #                 dsdl.BoundingBox(dsdl.Offset.CENTER, w=50, h=50),
        #                 dsdl.Animation(7, 2, oneshot=True, run=False))

        # w.create_entity(dsdl.Position(300, -25, dsdl.Offset.CENTER),
        #                 dsdl.Velocity(0, 4),
        #                 monospace.SphereEnemy(),
        #                 self.res['text']['enemies']['sphere'].get(),
        #                 dsdl.BoundingBox(dsdl.Offset.CENTER, w=50, h=50),
        #                 )

        # w.create_entity(dsdl.Position(200, -25, dsdl.Offset.CENTER),
        #                 dsdl.Velocity(0, 4),
        #                 monospace.RocketEnemy(),
        #                 self.res['text']['enemies']['rocket'].get(),
        #                 dsdl.BoundingBox(dsdl.Offset.CENTER, w=50, h=50),
        #                 )

        w.create_entity(monospace.PlayMusic())

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
        w.add_processor(monospace.PauseBackProcessor())

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

        # Options button
        w.create_entity(
            monospace.Button(lambda e, w, m: m.switch(m.res['options_world'],
                                                      True)),
            dsdl.BoundingBox(dsdl.Offset.CENTER, w=400,
                             h=100),
            dsdl.Position(monospace.LOGICAL_WIDTH // 2,
                          monospace.LOGICAL_HEIGHT - 100,
                          dsdl.Offset.CENTER),
            monospace.model.res['str'][monospace.current_lang] \
                .get_texture('options')
            )

        w.create_entity(monospace.PauseMusic())

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
        w.add_processor(monospace.BackWorldProcessor())

        offset_x = 30
        off_text = \
            self.res['str'][monospace.current_lang].get_texture('off')

        # Entities
        # Music setting
        w.create_entity(
            dsdl.Position(offset_x, 100),
            self.res['str'][monospace.current_lang].get_texture('music'))

        w.create_entity(
            dsdl.Position(monospace.LOGICAL_WIDTH - offset_x - off_text.w / 2,
                          100 + off_text.h / 2, dsdl.Offset.CENTER),
            dsdl.BoundingBox(dsdl.Offset.CENTER, w=off_text.w, h=off_text.h),
            monospace.Button(monospace.OptionToggler('music')),
            monospace.Option('music'))

        # Sfx setting
        w.create_entity(
            dsdl.Position(offset_x, 200),
            self.res['str'][monospace.current_lang].get_texture('sfx'))

        w.create_entity(
            dsdl.Position(monospace.LOGICAL_WIDTH - offset_x - off_text.w / 2,
                          200 + off_text.h / 2, dsdl.Offset.CENTER),
            dsdl.BoundingBox(dsdl.Offset.CENTER, w=off_text.w, h=off_text.h),
            monospace.Button(monospace.OptionToggler('sfx')),
            monospace.Option('sfx'))

        # Movement ratio setting
        w.create_entity(
            dsdl.Position(offset_x, 300),
            self.res['str'][monospace.current_lang].get_texture('ratio'))

        w.create_entity(
            dsdl.Position(monospace.LOGICAL_WIDTH - offset_x - off_text.w / 2,
                          300 + off_text.h / 2, dsdl.Offset.CENTER),
            dsdl.BoundingBox(dsdl.Offset.CENTER, w=off_text.w, h=off_text.h),
            monospace.Button(monospace.OptionSequencer('movement_ratio',
                                                       0, 3)),
            monospace.SequencedOption('movement_ratio'))

        save_text = self.res['str'][monospace.current_lang].get_texture('save')
        save_width = save_text.w + 30
        save_height = save_text.h + 30
        w.create_entity(
            monospace.Button(
                monospace.split_button_action(None, wait=0)),
            dsdl.Position(offset_x + save_width / 2, 400 + save_height / 2,
                          offset=dsdl.Offset.CENTER),
            save_text,
            dsdl.FillRectangle(offset_x, 400, save_width, save_height,
                               SDL_Color()),
            dsdl.BoundingBox(dsdl.Offset.CENTER, save_width, save_height)
            )

        return w


class DeathWorldHandle(desper.Handle):
    """Handle for the death screen."""

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
        w.add_processor(monospace.MainMenuBackProcessor())

        # Entities
        # Create entities

        # Retry button
        retry_width = 400
        retry_height = 100
        pos_y = monospace.LOGICAL_HEIGHT - retry_height - 150
        w.create_entity(
            monospace.Button(
                monospace.split_button_action(self.res['game_world'])),
            dsdl.BoundingBox(dsdl.Offset.CENTER, w=retry_width,
                             h=retry_height),
            dsdl.Position(monospace.LOGICAL_WIDTH // 2, pos_y,
                          dsdl.Offset.CENTER),
            dsdl.FillRectangle(monospace.LOGICAL_WIDTH // 2 - retry_width / 2,
                               pos_y - retry_height / 2, retry_width,
                               retry_height, SDL_Color()),
            monospace.model.res['str'][monospace.current_lang] \
                .get_texture('retry')
            )

        # Menu button
        menu_width = 400
        menu_height = 100
        pos_y = monospace.LOGICAL_HEIGHT - menu_height - 30
        w.create_entity(
            monospace.Button(
                monospace.split_button_action(self.res['menu_world'])),
            dsdl.BoundingBox(dsdl.Offset.CENTER, w=menu_width,
                             h=menu_height),
            dsdl.Position(monospace.LOGICAL_WIDTH // 2, pos_y,
                          dsdl.Offset.CENTER),
            dsdl.FillRectangle(monospace.LOGICAL_WIDTH // 2 - menu_width / 2,
                               pos_y - menu_height / 2, menu_width,
                               menu_height, SDL_Color()),
            monospace.model.res['str'][monospace.current_lang] \
                .get_texture('menu')
            )

        w.create_entity(monospace.FadeOutMusic())
        w.create_entity(monospace.DeathScoreManager())

        return w


class UnlockedWorldHandle(desper.Handle):
    """Handle that generates a world with a message for unlockables."""

    def __init__(self, res, unlocked_item, event=None):
        super().__init__()

        self.unlocked_item = unlocked_item
        self.event = event
        self.res = res

    def _load(self):
        w = desper.AbstractWorld()

        # Processors
        w.add_processor(dsdl.EventHandlerProcessor(), 10)
        w.add_processor(dsdl.FillRectangleRenderProcessor(), -0.5)
        w.add_processor(dsdl.TextureRendererProcessor(), -1)
        w.add_processor(dsdl.ScreenClearerProcessor(), -2)
        w.add_processor(desper.CoroutineProcessor())
        w.add_processor(dsdl.BoundingBoxProcessor())
        w.add_processor(monospace.ButtonProcessor())
        w.add_processor(monospace.MainMenuBackProcessor())

        # Entities
        base_y = 50
        base_x = 50

        w.create_entity(
            dsdl.Position(base_x, base_y),
            self.res['str'][monospace.current_lang].get_texture('unlocked'))

        w.create_entity(
            dsdl.Position(base_x, base_y + 100),
            self.res['str'][monospace.current_lang]
                .get_texture(self.unlocked_item))

        if self.event is not None:
            w.create_entity(
                dsdl.Position(base_x, base_y + 200),
                self.res['str'][monospace.current_lang]
                    .get_texture(self.event))

        button_width = 250
        button_height = 100
        button_y = monospace.LOGICAL_HEIGHT - 150 + button_height / 2
        w.create_entity(
            monospace.Button(
                monospace.split_button_action(self.res['menu_world'], wait=0)),
            dsdl.BoundingBox(dsdl.Offset.CENTER, w=button_width,
                             h=button_height),
            dsdl.Position(base_x + button_width / 2, button_y,
                          dsdl.Offset.CENTER),
            dsdl.FillRectangle(base_x,
                               button_y - button_height / 2, button_width,
                               button_height, SDL_Color()),
            monospace.model.res['str'][monospace.current_lang]
                .get_texture('ok')
            )

        return w


class NameSelectionWorldHandle(desper.Handle):
    """Handle that generates a world for the name selection."""

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
        w.add_processor(desper.CoroutineProcessor())
        w.add_processor(dsdl.BoundingBoxProcessor())
        w.add_processor(monospace.ButtonProcessor())
        w.add_processor(monospace.NameSelectorProcessor())
        #w.add_processor(monospace.BackWorldProcessor())

        #w.add_processor(dsdl.BoundingBoxRendererProcessor(), -1.5)

        # Text
        pos_y = 60
        w.create_entity(
            dsdl.Position(monospace.LOGICAL_WIDTH / 2, pos_y,
                          dsdl.Offset.CENTER),
            self.res['str'][monospace.current_lang] \
                .get_texture('username'))

        # Username text
        pos_y += 300
        x_dist = 150
        pos_x = monospace.LOGICAL_WIDTH / 2 - x_dist
        for i in range(3):
            w.create_entity(dsdl.Position(pos_x, pos_y, dsdl.Offset.CENTER),
                            monospace.CharSelector(i))

            pos_x += x_dist

        # Ok button
        pos_y += 300
        ok_text = monospace.model.res['str'][monospace.current_lang] \
            .get_texture('ok')
        ok_width = ok_text.w + 20
        ok_height = ok_text.h + 20

        w.create_entity(
            monospace.Button(monospace.ok_name_action),
            dsdl.BoundingBox(dsdl.Offset.CENTER, w=ok_width,
                             h=ok_height),
            dsdl.Position(monospace.LOGICAL_WIDTH // 2, pos_y,
                          dsdl.Offset.CENTER),
            dsdl.FillRectangle(monospace.LOGICAL_WIDTH // 2 - ok_width / 2,
                               pos_y - ok_height / 2, ok_width,
                               ok_height, SDL_Color()),
            ok_text)

        return w


def get_db_importer():
    return desper.get_resource_importer('db', ('.db'))


class DBHandle(desper.Handle):

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def _load(self):
        return sqlite3.connect(self.filename)
