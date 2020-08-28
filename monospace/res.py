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
        w.add_processor(desper.AbstractProcessor(), 2)
        w.add_processor(dsdl.VelocityProcessor(), 2)
        w.add_processor(dsdl.TextureRendererProcessor(), 1)
        w.add_processor(dsdl.ScreenClearerProcessor())

        # Create entities
        ship_pos = dsdl.Position()
        w.create_entity(monospace.Ship(ship_pos), ship_pos,
                        self.res['text']['ship'].get())

        return w
