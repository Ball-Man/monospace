"""Powerup functions, used inside PowerupBox instances."""
import copy
import weakref
import dsdl
import desper
import monospace
from functools import reduce


# Rewards

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

    # Increase the delay for all the blasters
    for blaster in ship.blasters:
        blaster.bullet_delay = int(blaster.bullet_delay * 4 / 3)


def powerup_add_blaster(ship: monospace.Ship):
    """Add a blaster to the ship."""
    tot_width = ship.texture.w
    tot_blasters = len(ship.blasters) + 1

    ship.blasters.append(copy.copy(ship.default_blaster))

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
        min_blaster = reduce(
            lambda m, b: max(m, b, key=lambda bl: bl.bullet_delay),
            ship.blasters)
        min_blaster.bullet_delay = max(
            monospace.MIN_BULLET_DELAY, min_blaster.bullet_delay // 3 * 2)


# Random bonus during the game
class Bonus:
    """Base class for real time bonuses.

    A bonus is added to the ship when instantiated(in a specific set)
    and removed when reverted.

    The bonus is applied thanks to the __call__ method so that it can
    blend with the other powerups(which often are simply functions).
    """

    def __call__(self, ship: monospace.Ship):
        ship.bonuses.add(self)

    def revert(self, ship: monospace.Ship):
        ship.bonuses.remove(self)


class BonusDelay(Bonus):
    """Bonus that speeds up fire rate for a limited time."""
    FACTOR = 2 / 3
    DURATION = 360

    def __init__(self):
        self.charges = 1        # Add 1 for each stacked delay bonus
        self._original_delays = []
        self._coroutine = None

    def __call__(self, ship: monospace.Ship):
        # If there's already a delay bonus on the ship, stack the charge
        for bonus in ship.bonuses:
            if type(bonus) is BonusDelay:
                bonus.charges += 1
                return

        super().__call__(ship)

        def bonus_coroutine(ship_ref):
            # Save current speeds in order to revert
            self._original_delays = [blaster.bullet_delay for blaster in
                                     ship_ref().blasters]

            # Increase speed
            for blaster in ship_ref().blasters:
                blaster.bullet_delay = max(
                    monospace.MIN_BULLET_DELAY,
                    int(blaster.bullet_delay * self.FACTOR))

            # Wait, based on how many charges
            charge = 0
            while charge < self.charges:
                yield self.DURATION
                charge += 1

            self.revert(ship_ref(), False)

        self._coroutine = ship.processor(desper.CoroutineProcessor).start(
            bonus_coroutine(weakref.ref(ship)))

    def revert(self, ship: monospace.Ship, remove_coroutine=True):
        """Revert the effect of this bonus on the given ship."""
        super().revert(ship)

        if ship is None:
            return

        # Kill coroutine manually if still alive, in order to stop it
        # from reverting again
        if self._coroutine is not None and remove_coroutine:
            ship.processor(desper.CoroutineProcessor).kill(self._coroutine)
            self._coroutine = None

        for blaster, or_delay in zip(ship.blasters, self._original_delays):
            blaster.bullet_delay = or_delay
