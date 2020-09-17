import ctypes
import random
import math
import desper
import esper
import dsdl
import monospace
from sdl2 import *
from sdl2.sdlttf import *


DEFAULT_BULLET_SPEED = 15
DEFAULT_BULLET_DELAY = 20


class GameProcessor(esper.Processor):
    """Main game logic(enemy waves, powerup spawns etc.)."""
    WAVE_THRESHOLDS = [50, 150, 300, 400]
    score = 0

    def __init__(self):
        self._cur_threshold = 0
        self._cached_texture = None
        self._cached_entity = None
        self.model = None

        self._timer = 0
        self._delay = 120

    def process(self, model):
        if self.model is None:
            self.model = model

        if self._cached_entity is None:
            self.score_up(0)

        # Spawn test enemies
        self._timer += 1
        if self._timer > self._delay:
            self.spawn_dots(random.randint(1, 3), 1)
            self._timer = 0

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

        # Change wave if necessary
        if self.score >= self.WAVE_THRESHOLDS[self._cur_threshold]:
            self._cur_threshold += 1

        # Create new texture
        shown_score = self.WAVE_THRESHOLDS[self._cur_threshold] - self.score
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

    def spawn_dot(self, x, y=-50):
        enemy_bbox = dsdl.BoundingBox(w=50, h=50)
        self.world.create_entity(
            dsdl.Position(x, y),
            enemy_bbox, dsdl.Velocity(0, 5),
            self.model.res['text']['enemies']['dot'].get(),
            dsdl.Animation(2, 60), DotEnemy())

    def spawn_dots(self, columns, rows):
        """Spawn dot enemies in their infamous formation.

        At random location horizontally.
        """
        base_x = (min(random.randrange(0, monospace.LOGICAL_WIDTH // 50),
                      monospace.LOGICAL_WIDTH // 50 - columns) * 50)

        y = -50
        var_y = -50
        var_x = 50
        for i in range(rows):
            x = base_x
            for j in range(columns):
                self.spawn_dot(x, y)
                x += var_x
            y -= var_y


class EntityCleanerProcessor(esper.Processor):
    """Clean bullets and enemies from memory."""

    def process(self, _):
        for en, _ in self.world.get_component(ShipBullet):
            position = self.world.component_for_entity(en, dsdl.Position)
            if position.y <= 50:
                self.world.delete_entity(en)

        for en, _ in self.world.get_component(Enemy):
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

    def on_attach(self, en, world):
        super().on_attach(en, world)

        # Test cicle to circle collisions
        self.circle = dsdl.CollisionCircle(50)
        world.add_component(en, self.circle)

        self.blasters.append(Blaster(
                                (0, 0), ShipBullet,
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

        # Test new collision system
        # for e, circle in self.world.get_component(dsdl.CollisionCircle):
        #     if e != en and dsdl.check_collisions(self.bbox, circle):
        #         self.processor(GameProcessor).score_up(1)
        for e, circle in self.world.get_component(dsdl.CollisionCircle):
            if e != en and dsdl.check_collisions(self.circle, circle):
                self.processor(GameProcessor).score_up(1)

        # Trigger blasters
        for blaster in self.blasters:
            blaster.shoot(self.position.x, self.position.y)

    def check_collisions(self, world):
        """Check for collisions with other bounding boxes."""
        # for _, bbox in world.get_component(dsdl.BoundingBox):
        #     if bbox is not self.bbox and self.bbox.overlaps(bbox):
        #         return True
        pass


class Blaster:
    """Class that represents a bullet blaster."""

    def __init__(self, offset, bullet_type, bullet_text, bullet_delay,
                 bullet_velocity, bullet_bbox, world):
        self.bullet_type = bullet_type
        self.bullet_text = bullet_text
        self.bullet_delay = bullet_delay
        self.bullet_velocity = bullet_velocity
        self.bullet_bbox = bullet_bbox
        self.offset = offset
        self.world = world

        self._timer = bullet_delay

    def shoot(self, x, y):
        """Shoot a bullet of bullet_type, offsetted given x and y.

        Attach to the bullet the given velocity component and buonding
        box.
        """
        self._timer -= 1
        if self._timer > 0:
            return

        # Restart timer and shoot
        self._timer = self.bullet_delay

        self.world.create_entity(dsdl.Position(
                                    self.offset[0] + x, self.offset[1] + y,
                                    offset=dsdl.Offset.BOTTOM_CENTER),
                                 self.bullet_text,
                                 dsdl.Velocity(*self.bullet_velocity),
                                 dsdl.BoundingBox(
                                    w=self.bullet_bbox[0],
                                    h=self.bullet_bbox[1],
                                    offset=self.bullet_bbox[2]),
                                 self.bullet_type()
                                 )


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


class Enemy(desper.Controller):
    """Base component class for enemies."""
    total_life = 1
    reward = 1

    def __init__(self):
        super().__init__()
        self.cur_life = self.total_life
        self.res = None

    def update(self, entity, world, model):
        # Check for collision with a bullet
        if self.res is None:
            self.res = model.res

        for en, bullet in world.get_component(ShipBullet):
            if bullet.hit:
                continue

            bbox = world.component_for_entity(en, dsdl.BoundingBox)

            if bbox.overlaps(self.get(dsdl.BoundingBox)):
                self.cur_life -= bullet.damage
                bullet.die()

                if self.cur_life <= 0:
                    self.die()

    def die(self):
        """Default method used for enemy destruction.

        Override to change the behaviour of the enemy.
        """
        self.world.delete_entity(self.entity)

        game = self.world.get_processor(GameProcessor)
        game.score_up(self.reward)
        self.spawn_particles()

    def spawn_particles(self):
        pass


class DotEnemy(Enemy):
    """Dot enemy controller."""

    def spawn_particles(self):
        """Spawn death particles for the death."""
        texture = self.get(ctypes.POINTER(SDL_Texture))
        position = self.get(dsdl.Position)
        offset = position.get_offset(texture.w, texture.h)
        for _ in range(random.randrange(4, 8)):
            angle = math.radians(random.randrange(0, 360))
            mag = random.randrange(2, 4)

            self.world.create_entity(
                dsdl.Particle(30, -0.1 / 64, -0.002),
                dsdl.Position(position.x - offset[0] + texture.w // 2,
                              position.y - offset[1] + texture.h // 2,
                              size_x=6 / 64, size_y=10 / 64,
                              offset=dsdl.Offset.CENTER),
                self.res['text']['part']['circle'].get(),
                dsdl.Velocity(x=math.cos(angle) * mag, y=math.sin(angle) * mag)
            )


class RollEnemy(Enemy):
    """Roll enemy controller."""
    hor_speed = 6
    total_life = 10000

    def __init__(self):
        super().__init__()

        self.trigger = random.randint(30, 100)
        self.timer = self.trigger
        self.rotation_speed = 0
        self._old_velocity = 0

    def update(self, en, world, model):
        super().update(en, world, model)

        self.timer -= 1

        position = self.get(dsdl.Position)
        texture = self.get(ctypes.POINTER(SDL_Texture))
        velocity = self.get(dsdl.Velocity)
        offset = position.get_offset(texture.w, texture.h)

        # Manage direction changes
        # Change direction if hitting the screen border
        if position.x - offset[0] + velocity.x < 0:
            velocity.x = self.hor_speed
        elif (position.x - offset[0] + velocity.x + texture.w
              > monospace.LOGICAL_WIDTH):
            velocity.x = -self.hor_speed
        elif velocity.x == 0:
            velocity.x = self.hor_speed
        # Change direction if the timer says so
        elif self.timer <= 0:
            velocity.x = -velocity.x

        if self.timer <= 0:
            self.timer = self.trigger

        if velocity.x != self._old_velocity:
            # Rotate. Calculate the traversal width in order to make
            # a complete rotation before changin direction.
            if velocity.x > 0:
                traversal_width = (monospace.LOGICAL_WIDTH - position.x
                                   - offset[0] + texture.w)
            elif velocity.x < 0:
                traversal_width = (position.x - offset[0])

            traversal_width = min(traversal_width, self.timer * self.hor_speed)
            self.rotation_speed = (math.copysign(1, velocity.x) * 180
                                   / (traversal_width / self.hor_speed))
        position.rot += self.rotation_speed

        self._old_velocity = velocity.x
