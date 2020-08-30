import ctypes
import desper
import esper
import dsdl
import monospace
from sdl2 import *


DEFAULT_BULLET_SPEED = 15
DEFAULT_BULLET_DELAY = 15


class GameProcessor(esper.Processor):
    """Main game logic(enemy waves, powerup spawns etc.)."""
    WAVE_THRESHOLDS = [50, 150, 300, 400]
    score = 0

    def process(self, model):
        pass


class Ship(desper.AbstractComponent):
    """Main ship controller."""

    def __init__(self, position, bbox):
        self.position = position
        self.bbox = bbox
        self._old_x = position.x
        self._old_y = position.y
        self._old_pressing = False
        self._drag = False

        self.bullet_delay = DEFAULT_BULLET_DELAY
        self.bullet_speed = DEFAULT_BULLET_SPEED
        self._timer = 0

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

        # Check collisions
        if self.check_collisions(world):
            print('colliding')

        # Shoot
        self._timer += 1
        if self._timer > self.bullet_delay:
            self.shoot(model, world)
            self._timer = 0

    def check_collisions(self, world):
        """Check for collisions with other bounding boxes."""
        # for _, bbox in world.get_component(dsdl.BoundingBox):
        #     if bbox is not self.bbox and self.bbox.overlaps(bbox):
        #         return True
        pass

    def shoot(self, model, world):
        """Create a new bullet."""
        world.create_entity(model.res['text']['ship_bullet'].get(),
                            dsdl.Position(self.position.x, self.position.y,
                                          dsdl.Offset.BOTTOM_CENTER),
                            dsdl.Velocity(0, -self.bullet_speed),
                            ShipBullet(), dsdl.BoundingBox((5, -40), 10, 10)
                            )


class ShipBullet(desper.OnAttachListener):
    """Base component for ship bullets."""
    damage = 1

    def on_attach(self, en, world):
        self.entity = en
        self.world = world

    def die(self):
        """Default method used for bullet destruction.

        Override to change the behaviour of the bullet.
        """
        self.world.delete_entity(self.entity)


class Enemy(desper.AbstractComponent, desper.OnAttachListener):
    """Base component class for enemies."""
    total_life = 1

    def __init__(self, bbox):
        self.cur_life = self.total_life
        self.bbox = bbox

    def on_attach(self, en, world):
        self.entity = en
        self.world = world

    def update(self, entity, world, _):
        # Check for collision with a bullet
        for en, bullet in world.get_component(ShipBullet):
            bbox = world.component_for_entity(en, dsdl.BoundingBox)

            if bbox.overlaps(self.bbox):
                self.cur_life -= bullet.damage
                world.delete_entity(en)

                if self.cur_life <= 0:
                    self.die()

    def die(self):
        """Default method used for enemy destruction.

        Override to change the behaviour of the enemy.
        """
        self.world.delete_entity(self.entity)
