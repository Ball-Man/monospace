import desper
import dsdl
import monospace


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

        # Test roll enemy
        w.create_entity(dsdl.Position(100, -50, offset=dsdl.Offset.CENTER),
                        self.res['text']['enemies']['roll'].get(),
                        monospace.RollEnemy(), dsdl.Velocity(0, 2),
                        dsdl.BoundingBox(w=50, h=50,
                                         offset=dsdl.Offset.CENTER))

        return w
