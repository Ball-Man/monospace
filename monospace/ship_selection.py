from collections import deque
import monospace
import desper


OWNED_SHIPS_QUERY = 'SELECT `name` FROM `ships` WHERE `unlocked`=1'

# Names, from the db
# The index 0 represent the selected one
owned_ships = deque()


def get_selected_ship_texture():
    """Retrieve the SDL_Texture for the currently selected ship."""
    selected = owned_ships[0] if len(owned_ships) > 0 else 'default'
    return monospace.model.res['text']['ships'][selected].get()


class ShipSelector(desper.OnAttachListener):
    def on_attach(self, en, world):
        """Query from the db the owned ships."""
        global owned_ships
        owned_ships = deque()

        res = monospace.model.res
        cursor = res['db']['current'].get().cursor()

        owned_ships.extend(field[0] for field in
                           cursor.execute(OWNED_SHIPS_QUERY))
        owned_ships.append('default')

        # Get selected ship
        selected_ship = next(cursor.execute(
            monospace.OPTION_GET_QUERY, ('selected_ship',)))[0]

        # Rotate until the selected ship is found
        if selected_ship in owned_ships:
            while owned_ships[0] != selected_ship:
                owned_ships.rotate()

        # Apply texture
        world.add_component(en, res['text']['ships'][owned_ships[0]].get())
