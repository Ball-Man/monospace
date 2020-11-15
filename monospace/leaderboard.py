"""Name selection and leaderboard management."""
import math
import json
import copy
import threading
import ctypes
import dsdl
import monospace
import pygmiscores
import desper
import esper
import requests
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


class UsernameChecker(desper.AbstractComponent):
    """Check if the username has been selected.

    If it's not, ask the user for the username input.
    """

    def update(self, en, world, model):
        res = model.res
        db = res['db']['current'].get()
        user_added = next(db.cursor().execute(monospace.OPTION_GET_QUERY,
                                              ('username_added',)))[0]
        if not user_added:
            # Set username
            model.switch(res['name_world'], reset=True, stack=True)

        world.delete_entity(en)


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


def leaderboard_action(en, world, model: dsdl.SDLGameModel):
    """Action for the Leaderboard button.

    Change world to the leaderboard one.
    Make the leaderboard request on a separate thread and render it
    on screen.
    """
    model.switch(model.res['lead_world'], stack=True)
    world = model.current_world

    scores: pygmiscores.Scores = model.res['sc_hooks']['main'].get()

    def coroutine():
        result = None

        def list_thread():
            nonlocal result
            try:
                result = scores.list_parsed(perpage=5,
                                            include_username=''.join(username))
            except requests.ConnectionError:
                result = {'status': 'Error'}

        list_thread = threading.Thread(target=list_thread)
        list_thread.start()

        # Wait for the thread
        while list_thread.is_alive():
            yield

        # Generate leaderboard
        x = 50
        if result['status'] == 200:
            y = 150
            inc_y = 80
            for i, score in enumerate(result['scores']):
                # Names
                surf = TTF_RenderUTF8_Blended(
                    model.res['fonts']['timenspace_sm'].get(),
                    score['username'].encode(),
                    SDL_Color())
                text = SDL_CreateTextureFromSurface(model.renderer, surf)
                world.create_entity(dsdl.Position(x, y), text)

                # Points
                surf = TTF_RenderUTF8_Blended(
                    model.res['fonts']['timenspace_sm'].get(),
                    str(score['score']).encode(),
                    SDL_Color())
                text = SDL_CreateTextureFromSurface(model.renderer, surf)
                world.create_entity(
                    dsdl.Position(monospace.LOGICAL_WIDTH - x
                                  - surf.contents.w, y),
                    text)

                y += inc_y

            if result['playerScore'] is not None:
                # Your name
                surf = TTF_RenderUTF8_Blended(
                        model.res['fonts']['timenspace_sm'].get(),
                        result['playerScore']['username'].encode(),
                        SDL_Color())
                text = SDL_CreateTextureFromSurface(model.renderer, surf)
                world.create_entity(
                    dsdl.Position(x, monospace.LOGICAL_HEIGHT - 100), text)

                # Your score
                surf = TTF_RenderUTF8_Blended(
                        model.res['fonts']['timenspace_sm'].get(),
                        str(result['playerScore']['score']).encode(),
                        SDL_Color())
                text = SDL_CreateTextureFromSurface(model.renderer, surf)
                world.create_entity(
                    dsdl.Position(monospace.LOGICAL_WIDTH - x
                                  - surf.contents.w,
                                  monospace.LOGICAL_HEIGHT - 100), text)

        else:       # If an error occurred
            world.create_entity(
                model.res['str'][monospace.current_lang] \
                    .get_texture('error'),
                dsdl.Position(x, 150))

    world.get_processor(desper.CoroutineProcessor).start(coroutine())


# Resource
def get_score_importer():
    return desper.get_resource_importer('sc_hooks', ('.json'))


class ScoresHandle(desper.Handle):
    """Handle for pygmiscores.Scores."""

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def _load(self):
        with open(self.filename) as file:
            dic = json.load(file)

        return pygmiscores.Scores(game_id=dic['game_id'], secret=dic['secret'])
