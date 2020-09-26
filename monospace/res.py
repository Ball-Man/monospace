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

        w.add_processor(dsdl.BoundingBoxRendererProcessor())

        # Create entities
        w.create_entity(
            monospace.Button(lambda: print('OK')),
            dsdl.BoundingBox(dsdl.Offset.CENTER, w=100, h=100),
            dsdl.Position(monospace.LOGICAL_WIDTH // 2, 100,
                          dsdl.Offset.CENTER),
            dsdl.FillRectangle(monospace.LOGICAL_WIDTH // 2 - 50,
                               50, 100, 100, SDL_Color()))

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

        #w.add_processor(dsdl.FPSLoggerProcessor())
        w.add_processor(dsdl.BoundingBoxRendererProcessor(), -1.5)

        # Create entities
        # Ship
        ship_pos = dsdl.Position(monospace.LOGICAL_WIDTH // 2,
                                 monospace.LOGICAL_HEIGHT / 10 * 9,
                                 offset=dsdl.Offset.CENTER)
        ship_bbox = dsdl.BoundingBox(dsdl.Offset.CENTER, 64, 64)
        w.create_entity(monospace.Ship(ship_pos, ship_bbox), ship_pos,
                        ship_bbox, self.res['text']['ship'].get())

        w.create_entity(dsdl.Position(-25, 100, dsdl.Offset.CENTER),
                        dsdl.Velocity(),
                        monospace.ShooterEnemy(),
                        self.res['text']['enemies']['shooter'].get(),
                        dsdl.BoundingBox(dsdl.Offset.CENTER, w=50, h=50),
                        dsdl.Animation(7, 2, oneshot=True, run=False))

        w.create_entity(dsdl.Position(300, -25, dsdl.Offset.CENTER),
                        dsdl.Velocity(0, 4),
                        monospace.SphereEnemy(),
                        self.res['text']['enemies']['sphere'].get(),
                        dsdl.BoundingBox(dsdl.Offset.CENTER, w=50, h=50),
                        )

        return w
