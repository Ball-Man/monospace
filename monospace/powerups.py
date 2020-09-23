"""Powerup functions, used inside PowerupBox instances."""
import copy
import dsdl
import desper
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


def powerup_shield(ship: monospace.Ship):
    """Add a shield."""
    shield_rad = 70

    position = dsdl.Position(ship.position.x,
                             ship.position.y,
                             offset=dsdl.Offset.CENTER)

    ship.world.create_entity(position,
                             dsdl.CollisionCircle(shield_rad),
                             monospace.PowerShield(),
        monospace.model.res['text']['powerups']['shield'].get())

    def shield_coroutine(position):
        # Fill the circle over time
        for size in range(30):
            position.size_x = size / 30
            position.size_y = size / 30

            yield

    ship.processor(desper.CoroutineProcessor).start(shield_coroutine(position))


def powerup_drift(ship: monospace.Ship):
    """Make all the bullets shifty."""

    for blaster in ship.blasters:
        blaster.bullet_type = monospace.DriftingShipBullet


def powerup_delay1(ship: monospace.Ship):
    """Powerup that speeds up the fire rate but only for one blaster."""

    if len(ship.blasters) > 0:
        ship.blasters[0].bullet_delay = max(
            monospace.MIN_BULLET_DELAY, ship.blasters[0].bullet_delay // 3 * 2)
