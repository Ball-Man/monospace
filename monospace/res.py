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
        w.add_processor(dsdl.BoundingBoxProcessor(), 3)
        w.add_processor(desper.AbstractProcessor(), 2)
        w.add_processor(dsdl.VelocityProcessor(), 2)
        w.add_processor(dsdl.TextureRendererProcessor(), 1)
        w.add_processor(dsdl.ScreenClearerProcessor())

        # Create entities
        ship_pos = dsdl.Position(offset=dsdl.Offset.CENTER)
        ship_bbox = dsdl.BoundingBox(dsdl.Offset.CENTER, 64, 64)
        w.create_entity(monospace.Ship(ship_pos, ship_bbox), ship_pos,
                        ship_bbox, self.res['text']['ship'].get())

        w.create_entity(dsdl.Position(100, 100), dsdl.BoundingBox(w=50, h=50),
                        self.res['text']['ship'].get())

        return w
