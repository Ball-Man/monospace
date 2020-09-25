import ctypes
import enum
import math
import desper
import esper
import dsdl
import monospace
from sdl2 import *
from sdl2.sdlttf import *


DEFAULT_BULLET_SPEED = 15
DEFAULT_BULLET_DELAY = 30
MIN_BULLET_DELAY = 7


class GameProcessor(esper.Processor):
    """Main game logic(enemy waves, powerup spawns etc.)."""

    WAVE_THRESHOLDS = [50, 150, 300, 600, math.inf]
    score = 0

    def __init__(self):
        self._cur_threshold = 0
        self._cached_texture = None
        self._cached_entity = None
        self.model = None

        self._state = GameState.WAVE
        self._powerup_coroutine = None
        self._rewards_spawned = False
        self._next_wave_coroutine = None

        self.waves = [monospace.FirstWave(), monospace.SecondWave(),
                      monospace.DotsWave(), monospace.DotsWave()]

    def process(self, model):
        if self.model is None:
            self.model = model

        if self._cached_entity is None:
            self.score_up(0)

        coroutines = self.world.get_processor(desper.CoroutineProcessor)

        # State machine
        if self._state == GameState.WAVE:
            self.waves[self._cur_threshold].spawn(self.world)
        elif self._state == GameState.REWARD:
            if self._powerup_coroutine is None:
                # Spawn rewards
                self._powerup_coroutine = coroutines.start(
                    self.spawn_rewards())

            # When there are no rewards left, go to the next wave
            rewards = tuple(self.world.get_component(PowerupBox))
            if (self._rewards_spawned and len(rewards) == 0
                    and self._next_wave_coroutine is None):
                self._next_wave_coroutine = coroutines.start(
                    self.next_wave())

    def spawn_rewards(self):
        yield 120
        self.waves[self._cur_threshold].spawn_rewards(self.world)
        self._rewards_spawned = True

    def next_wave(self):
        yield 120
        self._cur_threshold += 1
        self._state = GameState.WAVE
        self._rewards_spawned = False
        self.score_up(0)

    def score_up(self, value):
        """Add some value to the current score.

        This also invalidates the current cached texture.
        """
        self.score += value

        # Cache texture and create a new entity
        #
        # Remove current entity
        if self._cached_entity is not None:
            # SDL_DestroyTexture(self._cached_texture)
            # Apparently this operation crashes on android. Looks like
            # textures are freed when the entity is deleted.

            self.world.delete_entity(self._cached_entity)

        # Change internal state if necessary
        if self.score >= self.WAVE_THRESHOLDS[self._cur_threshold]:
            self.change_to_reward()

        # Create new texture
        shown_score = max(
            self.WAVE_THRESHOLDS[self._cur_threshold] - self.score, 0)
        text_surface = TTF_RenderText_Blended(
            self.model.res['fonts']['timenspace'].get(),
            str(shown_score).encode(), SDL_Color())
        self._cached_texture = SDL_CreateTextureFromSurface(
            self.model.renderer, text_surface)

        # Add entity
        self._cached_entity = self.world.create_entity(
            self._cached_texture, dsdl.Position(30, 50))

        # Cleanup
        SDL_FreeSurface(text_surface)

    def change_to_reward(self):
        """Change state to REWARD, with consequences."""
        if self._state == GameState.REWARD:
            return

        self._state = GameState.REWARD
        self.clear_screen()

        # Reset bonuses given to the ship
        ship = self.world.get_component(Ship)[0][1]
        ship.revert_bonuses()

    def clear_screen(self):
        """Clear all the unwanted entities from the screen.

        This clears all enemies and powerups.
        """
        # Clear all the enemies
        for en, enemy in self.world.get_component(monospace.Enemy):
            enemy.spawn_particles()
            self.world.delete_entity(en)

        # Clear all the bonuses
        for en, _ in self.world.get_component(PowerupBox):
            self.world.delete_entity(en)


class GameState(enum.Enum):
    """Enumeration for the GameProcessor internal state machine."""
    WAVE = 0
    REWARD = 1


class EntityCleanerProcessor(esper.Processor):
    """Clean bullets and enemies from memory."""

    def process(self, _):
        for en, _ in self.world.get_component(ShipBullet):
            position = self.world.component_for_entity(en, dsdl.Position)
            if position.y <= 50:
                self.world.delete_entity(en)

        for en, _ in self.world.get_component(monospace.Enemy):
            position = self.world.component_for_entity(en, dsdl.Position)
            if position.y > monospace.LOGICAL_HEIGHT + 50:
                self.world.delete_entity(en)


class Ship(desper.Controller):
    """Main ship controller."""

    def __init__(self, position, bbox):
        super().__init__()

        self.position = position
        self.bbox = bbox
        self._old_x = position.x
        self._old_y = position.y
        self._old_pressing = False
        self._drag = False

        self._timer = 0

        self.blasters = []

        self.texture = None

        self.bonuses = set()

    def on_attach(self, en, world):
        super().on_attach(en, world)

        self.texture = self.get(ctypes.POINTER(SDL_Texture))

        self.blasters.append(
            Blaster((0, 0), ShipBullet,
                    monospace.model.res['text']['ship_bullet'].get(),
                    DEFAULT_BULLET_DELAY,
                    (0, -DEFAULT_BULLET_SPEED),
                    (10, 10, (5, 40)), world))

    def update(self, en, world, model):
        mouse_x, mouse_y = ctypes.c_int(), ctypes.c_int()
        pressing = (SDL_GetMouseState(ctypes.byref(mouse_x),
                                      ctypes.byref(mouse_y))
                    & SDL_BUTTON(SDL_BUTTON_LEFT))

        # Start drag
        if pressing and not self._old_pressing:
            self._drag = True
            self._old_x, self._old_y = mouse_x.value, mouse_y.value
        elif not pressing and self._old_pressing:   # Stop drag
            self._drag = False

        if self._drag:
            self.position.x += ((mouse_x.value - self._old_x)
                                * monospace.LOGICAL_WIDTH_RATIO)
            self.position.y += ((mouse_y.value - self._old_y)
                                * monospace.LOGICAL_WIDTH_RATIO)
            self._old_x, self._old_y = mouse_x.value, mouse_y.value

        self._old_pressing = pressing

        # Don't move outside borders
        self.position.x = max(min(self.position.x, monospace.LOGICAL_WIDTH), 0)
        self.position.y = max(min(self.position.y, monospace.LOGICAL_HEIGHT),
                              0)

        # Trigger blasters
        for blaster in self.blasters:
            blaster.shoot(self.position.x, self.position.y)

        # Check collisions with powerups
        powerup = self.check_collisions(PowerupBox)
        if powerup is not None:
            powerup.apply(self)

        # Check collisions with enemy bullets
        enemy_bullet = self.check_collisions(EnemyBullet)
        if enemy_bullet is not None:
            try:
                # If has shield, protect
                self.get(PowerShield)
            except KeyError:
                # If no shield, defeat
                die()

    def check_collisions(self, component_type):
        """Check for collisions with a component_type(bbox).

        Return None if no collision is detected, return an instance of
        component_type instead(the one colliding).
        """
        for en, comp in self.world.get_component(component_type):
            bbox = self.world.try_component(en, dsdl.BoundingBox)

            if bbox.overlaps(self.bbox):
                return comp

        return None

    def revert_bonuses(self):
        """Revert the effect of all bonuses."""
        bonuses = list(self.bonuses)
        for bonus in bonuses:
            bonus.revert(self)

    def die(self):
        pass


class Blaster:
    """Class that represents a bullet blaster."""

    def __init__(self, offset, bullet_type, bullet_text, bullet_delay,
                 bullet_velocity, bullet_bbox, world, animation=None):
        self.bullet_type = bullet_type
        self.bullet_text = bullet_text
        self.bullet_delay = bullet_delay
        self.bullet_velocity = bullet_velocity
        self.bullet_bbox = bullet_bbox
        self.offset = offset
        self.world = world
        self.animation = animation

        self._timer = bullet_delay

    def shoot(self, x, y):
        """Shoot a bullet of bullet_type, offsetted given x and y.

        Attach to the bullet the given velocity component and buonding
        box.
        """
        self._timer -= 1
        if self._timer > 0:
            return False

        # Restart timer and shoot
        self._timer = self.bullet_delay
        components = [
            dsdl.Position(self.offset[0] + x, self.offset[1] + y,
                          offset=dsdl.Offset.BOTTOM_CENTER),
            self.bullet_text,
            dsdl.Velocity(*self.bullet_velocity),
            dsdl.BoundingBox(w=self.bullet_bbox[0], h=self.bullet_bbox[1],
                             offset=self.bullet_bbox[2]),
            self.bullet_type()]

        if self.animation is not None:
            components.append(dsdl.Animation(*self.animation))

        self.world.create_entity(*components)

        return True


class EnemyBullet(desper.Controller):
    """Class representing an opponent's bullet."""

    def update(self, en, world, model):
        # If a shield is found, self-destruct
        for _, (circle, shield) \
                in world.get_components(dsdl.CollisionCircle,
                                        monospace.PowerShield):
            if dsdl.check_collisions(circle, self.get(dsdl.BoundingBox)):
                world.delete_entity(en)


class ShipBullet(desper.OnAttachListener):
    """Base component for ship bullets."""
    damage = 1

    def __init__(self):
        self.hit = False    # Ignore multiple hits by setting hit to 1

    def on_attach(self, en, world):
        self.entity = en
        self.world = world

    def die(self):
        """Default method used for bullet destruction.

        Override to change the behaviour of the bullet.
        """
        self.world.delete_entity(self.entity)
        self.hit = True


class DriftingShipBullet(ShipBullet, desper.AbstractComponent):
    """Special type of bullet for the ship.

    This is actually a bit of code smell that could be sanitized with
    an adpater/decorator/bridge like pattern. For the simplicity of this
    small game, the smell is kept.
    """

    def on_attach(self, en, world):
        super().on_attach(en, world)
        self.position = world.try_component(en, dsdl.Position)
        self.starting_x = self.position.x
        self._drift_time = 0

    def update(self, *args):
        self._drift_time += 1
        self.position.x = (self.starting_x + 40
                           * math.sin(self._drift_time / 10))


class PowerShield(desper.Controller):
    """Component that shields a hit from an enemy.

    All the bullets from enemies are shielded without the shield
    being destroyed.
    """

    def on_attach(self, en, world):
        super().on_attach(en, world)

        self.ship_pos = world.get_components(Ship, dsdl.Position)[0][1][1]

    def update(self, en, world, _):
        # Check collision with enemies
        pos = self.get(dsdl.Position)
        circle = self.get(dsdl.CollisionCircle)

        # Follow player
        pos.x = self.ship_pos.x
        pos.y = self.ship_pos.y

        # Check collision
        for entity, enemy in world.get_component(monospace.Enemy):
            bbox = world.try_component(entity, dsdl.BoundingBox)

            if dsdl.check_collisions(circle, bbox):
                enemy.die()
                world.delete_entity(en)


class PowerupBox(desper.OnAttachListener):
    """Proxy component for a power function."""

    def __init__(self, powerup_applier):
        self.powerup_applier = powerup_applier
        self.applied = False

    def on_attach(self, en, world):
        self.world = world
        self.en = en

    def apply(self, ship):
        """Apply the incapsulated powerup to the given ship.

        After being applied, destroy it
        """
        if self.applied:
            return

        self.applied = True
        self.powerup_applier(ship)

        # Particles?

        # Delete all powerup boxes on screen
        for en, powerup in self.world.get_component(PowerupBox):
            powerup.applied = True      # Prevent anomalies
            self.world.delete_entity(en)