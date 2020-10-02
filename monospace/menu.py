import ctypes
import functools
import copy
import dsdl
import monospace
import desper
import esper
from sdl2 import *
from sdl2.sdlmixer import *


OPTIONS_GET_ALL_QUERY = 'SELECT * FROM `options`'
OPTION_GET_QUERY = 'SELECT `value` FROM `options` WHERE `option_name`=?'
OPTION_UPDATE_QUERY = 'UPDATE `options` SET `value`=? WHERE `option_name`=?'


class HaltMusic(desper.OnAttachListener):
    """Halt music on attach."""

    def on_attach(self, *args):
        Mix_HaltMusic()


class PlayMusic(desper.OnAttachListener):
    """Play music on attach, if not playing already. Resumes if paused."""

    def on_attach(self, *args):
        if Mix_PausedMusic():
            Mix_ResumeMusic()
        elif not Mix_PlayingMusic():
            Mix_PlayMusic(monospace.model.res['mus']['too_much'].get(), -1)


class FadeOutMusic(desper.OnAttachListener):
    """Fade out music on attach."""

    def __init__(self, ms=300):
        self.ms = ms

    def on_attach(self, *args):
        Mix_FadeOutMusic(int(self.ms))


class PauseMusic(desper.OnAttachListener):
    """Pause music on attach."""

    def on_attach(self, *args):
        Mix_PauseMusic()


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

        win_w, win_h = ctypes.c_int(0), ctypes.c_int(0)
        SDL_GetWindowSize(monospace.model.window, win_w, win_h)

        mouse_x = mouse_x.value * monospace.LOGICAL_WIDTH_RATIO
        mouse_y = mouse_y.value * monospace.LOGICAL_HEIGHT / win_h.value

        # print('window', win_w, win_h)
        # print('display mode', monospace.DISPLAY_MODE)

        # print('ratio', monospace.LOGICAL_WIDTH_RATIO,
        #       'width', monospace.LOGICAL_WIDTH, 'height',
        #       monospace.LOGICAL_HEIGHT, 'mouse', mouse_x, mouse_y)
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


def split_button_action(world_handle, speed=30, wait=30):
    """Split button animation and change world with the given world."""

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

        # Sound feedback
        Mix_PlayChannel(-1, model.res['chunks']['button'].get(), 0)

        def coroutine():
            """Animation."""
            while True:
                rec1.x -= speed
                rec2.x += speed

                if rec2.x > monospace.LOGICAL_WIDTH:
                    yield wait
                    model.switch(world_handle, reset=True)

                yield

        world.get_processor(desper.CoroutineProcessor).start(coroutine())

    return start_action


def pause_game(en, world: esper.World, model: desper.GameModel):
    """Action for the game pause button."""
    try:
        world.get_component(monospace.Ship)[0][1]._drag = False
        # Sound feedback
        Mix_PlayChannel(-1, model.res['chunks']['button'].get(), 0)
        model.switch(model.res['pause_world'])
    except IndexError:
        pass


def resume_game(en, world: esper.World, model: desper.GameModel):
    """Action for the game resumed button."""
    world.delete_entity(en)

    # Sound feedback
    Mix_PlayChannel(-1, model.res['chunks']['button'].get(), 0)

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

        # Unpause music
        if Mix_PausedMusic():
            Mix_ResumeMusic()

        # Sound feedback
        Mix_PlayChannel(-1, model.res['chunks']['button'].get(), 0)
        model.switch(model.res['game_world'], True)

    world.get_processor(desper.CoroutineProcessor).start(
        coroutine()
        )


class Option(desper.OnAttachListener):
    """Set the option initial state, queried from the db."""

    def __init__(self, option_name):
        self.option_name = option_name

    def on_attach(self, en, world):
        res = monospace.model.res
        c = res['db']['current'].get().cursor()

        c.execute(OPTION_GET_QUERY, (self.option_name,))
        value = next(c)[0]

        comps = []
        if value:
            bbox = world.try_component(en, dsdl.BoundingBox)
            pos = world.try_component(en, dsdl.Position)
            offset = pos.get_offset(bbox.w, bbox.h)
            comps.append(res['str'][monospace.current_lang].get_texture('on'))
            comps.append(dsdl.FillRectangle(pos.x - offset[0],
                                            pos.y - offset[1], bbox.w, bbox.h,
                                            SDL_Color()))
        else:
            comps.append(res['str'][monospace.current_lang].get_texture('off'))

        for comp in comps:
            world.add_component(en, comp)

        # Actually apply option
        OPTIONS_SETTERS[self.option_name](value)


class OptionToggler:
    """Callable instances used as actions for Buttons."""

    def __init__(self, option_name):
        self.option_name = option_name
        self._coroutine = None

    def __call__(self, en, world: esper.World, model: desper.GameModel):
        # Do nothing if something is an operation is already in progress
        if self._coroutine is not None:
            return

        db = model.res['db']['current'].get()
        c = db.cursor()
        c.execute(OPTION_GET_QUERY, (self.option_name,))

        value = not next(c)[0]
        c.execute(OPTION_UPDATE_QUERY, (value, self.option_name))
        db.commit()

        # Used by coroutines
        res = model.res
        speed = 10
        bbox = world.try_component(en, dsdl.BoundingBox)
        pos = world.try_component(en, dsdl.Position)
        offset = pos.get_offset(bbox.w, bbox.h)

        # Actually apply option
        OPTIONS_SETTERS[self.option_name](value)

        # Feedback sound
        Mix_PlayChannel(-1, res['chunks']['toggle'].get(), 0)

        def coroutine_toggle_on():
            """Create the rectangle."""
            world.add_component(
                en, res['str'][monospace.current_lang].get_texture('on'))
            rect = dsdl.FillRectangle(pos.x - offset[0],
                                      pos.y - offset[1] + bbox.h, bbox.w, 0,
                                      SDL_Color())
            world.add_component(en, rect)

            while rect.h < bbox.h:
                rect.h += min(bbox.h - rect.h, speed)
                rect.y = pos.y - offset[1] + bbox.h - rect.h
                yield

            self._coroutine = None

        def coroutine_toggle_off():
            """Collapse the rectangle."""
            world.add_component(
                en, res['str'][monospace.current_lang].get_texture('off'))
            rect = world.try_component(en, dsdl.FillRectangle)

            while rect.h > 0:
                rect.h -= min(rect.h, speed)
                rect.y = pos.y - offset[1] + bbox.h - rect.h
                yield

            world.remove_component(en, dsdl.FillRectangle)
            self._coroutine = None

        proc = world.get_processor(desper.CoroutineProcessor)
        if value:
            self._coroutine = proc.start(coroutine_toggle_on())
        else:
            self._coroutine = proc.start(coroutine_toggle_off())


def apply_options(db):
    """Apply all options from the db. Useful at startup."""
    c = db.cursor()
    for name, value in c.execute(OPTIONS_GET_ALL_QUERY):
        OPTIONS_SETTERS[name](value)


def set_music(val):
    """Toggle music, val is a boolean."""
    Mix_VolumeMusic(0 * (1 - val) + MIX_MAX_VOLUME * val)


def set_sfx(val):
    """Toggle sfx, val is a boolean."""
    Mix_Volume(-1, 0 * (1 - val) + MIX_MAX_VOLUME * val)


OPTIONS_SETTERS = {'music': set_music, 'sfx': set_sfx}
