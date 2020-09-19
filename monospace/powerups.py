"""Powerup functions, used inside PowerupBox instances."""
import copy
import monospace


def powerup_double_blasters(ship: monospace.Ship):
    """Double blasters for the ship."""
    tot_width = ship.texture.w
    num_blasters = len(ship.blasters)

    # Relocate current blasters
    for i, blaster in enumerate(ship.blasters):
        blaster.offset = (tot_width // 2 // (num_blasters + 1) * (i + 1),
                          blaster.offset[1])

    # Generate new blasters
    new_blasters = [copy.copy(blaster) for blaster in ship.blasters]
    for blaster in new_blasters:
        blaster.offset = -blaster.offset[0], blaster.offset[1]

    ship.blasters += new_blasters


def powerup_add_blaster(ship: monospace.Ship):
    """Add a blaster to the ship."""
    tot_width = ship.texture.w
    tot_blasters = len(ship.blasters) + 1

    ship.blasters.append(copy.copy(ship.blasters[0]))

    # Relocate blasters
    for i, blaster in enumerate(ship.blasters):
        blaster.offset = ((i + 1) * tot_width // (tot_blasters + 1)
                          - tot_width // 2,
                          blaster.offset[1])