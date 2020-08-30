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
        w.add_processor(dsdl.BoundingBoxProcessor(), 1)
        w.add_processor(dsdl.TextureRendererProcessor(), -1)
        w.add_processor(dsdl.ScreenClearerProcessor(), -2)
        w.add_processor(monospace.GameProcessor())
        w.add_processor(desper.AbstractProcessor())
        w.add_processor(dsdl.VelocityProcessor())

        # w.add_processor(dsdl.FPSLoggerProcessor())
        w.add_processor(dsdl.BoundingBoxRendererProcessor(), -1.5)

        # Create entities
        ship_pos = dsdl.Position(offset=dsdl.Offset.CENTER)
        ship_bbox = dsdl.BoundingBox(dsdl.Offset.CENTER, 64, 64)
        w.create_entity(monospace.Ship(ship_pos, ship_bbox), ship_pos,
                        ship_bbox, self.res['text']['ship'].get())

        enemy_bbox = dsdl.BoundingBox(w=50, h=50)
        w.create_entity(dsdl.Position(100, 100), enemy_bbox,
                        self.res['text']['enemies']['dot'].get(),
                        dsdl.Animation(2, 60), monospace.Enemy(enemy_bbox))

        return w
