"""Name selection and leaderboard management."""
import math
import copy
import dsdl
import monospace
import desper
import esper
from sdl2 import *
from sdl2.sdlttf import *

username = ['A', 'A', 'A']

MAX_USERNAME_LENGTH = 8


class NameSelectorProcessor(esper.Processor):
    """Render username during selection."""

    def __init__(self):
        self.char_map = {}
        self.username = [' ', ' ', ' ']

    def process(self, *args):
        if self.username != username:
            for en, sel in self.world.get_component(CharSelector):
                self.world.add_component(
                    en, self.get_char_texture(username[sel.index]))

            self.username = copy.copy(username)

    def get_char_texture(self, ch):
        """Retrieve the texture for a specific character.

        Generate and cache it if it isn't found.
        """
        if self.char_map.get(ch) is not None:
            return self.char_map[ch]

        # Generate
        res = monospace.model.res
        surf = TTF_RenderUTF8_Blended(res['fonts']['timenspace'].get(),
                                      ch.encode(), SDL_Color())
        text = SDL_CreateTextureFromSurface(monospace.model.renderer, surf)
        self.char_map[ch] = text

        return text


class CharSelector(desper.OnAttachListener):
    """Component used for username selection.

    Enable selection of one character.
    """
    ARROW_SIZE = 100

    def __init__(self, index):
        self.index = index

    def on_attach(self, en, world):
        # Create buttons
        pos = world.component_for_entity(en, dsdl.Position)
        res = monospace.model.res

        btns = -1, 1
        for sign in btns:
            y = pos.y + -sign * 100
            rot = 0 if sign > 0 else 180
            world.create_entity(
                monospace.Button(character_button(self.index, sign)),
                dsdl.Position(pos.x, y, dsdl.Offset.CENTER, rot=rot),
                dsdl.BoundingBox(dsdl.Offset.CENTER, self.ARROW_SIZE,
                                 self.ARROW_SIZE),
                res['text']['arrow_up'].get())


def character_button(index, add=1):
    """Getter for an action, based on index.

    The index is based on the username global list.
    A positive add value will increment the value of the character,
    a negative will decrement(from a to b, from b to a).
    """
    def action(en, world, model):
        global username
        zero = ord('A')
        end = ord('Z') + 1
        username[index] = chr(zero + (ord(username[index]) - zero
            + int(math.copysign(1, add))) % (end - zero))

        # Sound feedback?

    return action


def ok_name_action(en, world, model: dsdl.SDLGameModel):
    """Action for the username acceptance button.

    Hide keyboard(eventually) and set internal username(and switch
    world ofc).
    """
    # Update db
    db = model.res['db']['current'].get()
    cur = db.cursor()
    cur.execute(monospace.OPTION_UPDATE_QUERY, (True, 'username_added'))
    cur.execute(monospace.OPTION_UPDATE_QUERY, (''.join(username), 'username'))
    db.commit()

    monospace.split_button_action(None, wait=0)(en, world, model)
