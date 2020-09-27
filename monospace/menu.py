import ctypes
import copy
import dsdl
import monospace
import desper
import esper
from sdl2 import *


class ButtonProcessor(esper.Processor):
    """Processor that manages button presses."""

    def __init__(self):
        self._old_pressed = False

    def process(self, model):
        mouse_x, mouse_y = ctypes.c_int(0), ctypes.c_int(0)
        if (SDL_GetMouseState(mouse_x, mouse_y)
                & SDL_BUTTON(SDL_BUTTON_LEFT)):
            pressed = True
        else:
            pressed = False

        mouse_x = mouse_x.value * monospace.LOGICAL_WIDTH_RATIO
        mouse_y = mouse_y.value * monospace.LOGICAL_WIDTH_RATIO

        for en, (bbox, button) in self.world.get_components(
                dsdl.BoundingBox, Button):

            # Check if the the bounding box is hit
            if (bbox.x <= mouse_x <= (bbox.x + bbox.w)
                and bbox.y <= mouse_y <= (bbox.y + bbox.h)
                    and pressed and not self._old_pressed):

                button.action(en, self.world, model)

        self._old_pressed = pressed


class Button:
    """Component that incapsulates the behaviour of a button.

    It's designed to be used with BoundingBoxes. When the BoundingBox
    is pressed, the command contained in the button is fired.

    action accepts 3 arguments, entity, world and model(similar to
    desper.AbstractComponent).
    """

    def __init__(self, action):
        self.action = action


def start_action(en, world: esper.World, model: desper.GameModel):
    """Action for the game start Button."""
    # Disable button
    world.remove_component(en, Button)

    # Remove rectangle, substitute with two split rectangles
    rectangle = world.try_component(en, dsdl.FillRectangle)
    # Setup splits
    rec1 = copy.copy(rectangle)
    rec1.h /= 2
    rec2 = copy.copy(rectangle)
    rec2.h /= 2
    rec2.y += rec1.h
    world.create_entity(rec1)
    world.create_entity(rec2)
    # Remove original
    world.remove_component(en, dsdl.FillRectangle)

    rec_speed = 20

    def coroutine():
        """Animation."""
        while True:
            rec1.x -= rec_speed
            rec2.x += rec_speed

            if rec2.x > monospace.LOGICAL_WIDTH:
                yield 30
                model.switch(model.res['game_world'], reset=True)

            yield

    world.get_processor(desper.CoroutineProcessor).start(coroutine())


def pause_game(en, world: esper.World, model: desper.GameModel):
    """Action for the game pause button."""
    try:
        world.get_component(monospace.Ship)[0][1]._drag = False
        model.switch(model.res['pause_world'])
    except IndexError:
        pass


def resume_game(en, world: esper.World, model: desper.GameModel):
    """Action for the game resumed button."""
    world.delete_entity(en)

    def coroutine():
        """Countdown."""
        count_en = world.create_entity(
            dsdl.Position(monospace.LOGICAL_WIDTH / 2,
                          monospace.LOGICAL_HEIGHT / 2,
                          dsdl.Offset.CENTER))

        for i in range(3, 0, -1):
            try:
                world.remove_component(count_en, ctypes.POINTER(SDL_Texture))
            except KeyError:
                pass

            world.add_component(
                count_en,
                model.res['str'][monospace.current_lang].get_texture(str(i)))

            yield 60

        model.switch(model.res['game_world'], True)

    world.get_processor(desper.CoroutineProcessor).start(
        coroutine()
        )
