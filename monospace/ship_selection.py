from collections import deque
import math
import dsdl
import monospace
import desper
import esper


OWNED_SHIPS_QUERY = 'SELECT `name` FROM `ships` WHERE `unlocked`=1'
SELECTOR_Y_FACTOR = 1 / 10
SELECTOR_X_FACTOR = 1 / 5

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

        ships_en = set(field[0] for field in
                       world.get_component(SelectionShip))
        for ship in ships_en - {en}:
            pos = world.component_for_entity(ship, dsdl.Position)
            index = int(math.copysign(1, pos.x - monospace.LOGICAL_WIDTH // 2))
            world.add_component(
                ship,
                res['text']['ships'][owned_ships[index]].get())


# class ShipSelectionProcessor(esper.Processor):
#     """ECS system for the ship selection in the main menu."""

#     def process(self, model):


class SelectionShip:
    """Component that identifies a ship in the selection screen."""

    pass


def select_ship(en, world, model):
    """Action for a Button, when a ship is selected by touching it."""
    selected_pos = world.component_for_entity(en, dsdl.Position)
    selected_vel = world.component_for_entity(en, dsdl.Velocity)
    ships_en = set(field[0] for field in world.get_component(SelectionShip))
    ships_vel = [world.component_for_entity(e, dsdl.Velocity)
                 for e in ships_en]
    ships_pos = [world.component_for_entity(e, dsdl.Position)
                 for e in ships_en]

    # Exit if this ship is already selected
    if int(selected_pos.x) == monospace.LOGICAL_WIDTH // 2:
        return

    if selected_pos.x < monospace.LOGICAL_WIDTH // 2:
        vel_x = 10
    else:
        vel_x = -10

    for vel in ships_vel:
        vel.x = vel_x

    # Rotate and select the new ship(+ update db)
    rotation_index = int(math.copysign(1, vel_x))
    owned_ships.rotate(rotation_index)
    db = model.res['db']['current'].get()
    db.cursor().execute(monospace.OPTION_UPDATE_QUERY,
                        (owned_ships[0], 'selected_ship'))
    db.commit()

    # Create the new ship
    if rotation_index > 0:
        new_x = monospace.LOGICAL_WIDTH * (2 * SELECTOR_X_FACTOR - 1 / 2)
    else:
        new_x = monospace.LOGICAL_WIDTH * (3 / 2 - 2 * SELECTOR_X_FACTOR)

    new_pos = dsdl.Position(new_x,
                            monospace.LOGICAL_HEIGHT * (1 - SELECTOR_Y_FACTOR),
                            dsdl.Offset.CENTER)
    new_vel = dsdl.Velocity(vel_x, 0)
    new_en = world.create_entity(
        new_pos, new_vel, SelectionShip(), monospace.Button(select_ship),
        dsdl.BoundingBox(dsdl.Offset.CENTER, 100, 100),
        model.res['text']['ships'][owned_ships[-rotation_index]].get())

    # Add the new ship to the data structures
    ships_en.add(new_en)
    ships_vel.append(new_vel)
    ships_pos.append(new_pos)

    def coroutine():
        """Animation."""
        for pos in ships_pos:
            pos.alpha = 127

        while int(selected_pos.x) != monospace.LOGICAL_WIDTH // 2:
            if abs(selected_pos.x - monospace.LOGICAL_WIDTH // 2) \
               < abs(selected_vel.x):
                for vel in ships_vel:
                    vel.x = 0
                selected_pos.x = monospace.LOGICAL_WIDTH // 2
            yield

        selected_pos.alpha = 255
        # Stop all the ships and delete the useless ones
        for vel in ships_vel:
            vel.x = 0
        for ship in ships_en:
            ship_pos = world.component_for_entity(ship, dsdl.Position)
            if not 0 < ship_pos.x < monospace.LOGICAL_WIDTH:
                world.delete_entity(ship)

    world.get_processor(desper.CoroutineProcessor).start(coroutine())
