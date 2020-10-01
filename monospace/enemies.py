import ctypes
import math
import random
import monospace
import dsdl
import desper
from sdl2 import *
from sdl2.sdlmixer import *


class Enemy(desper.Controller):
    """Base component class for enemies."""
    total_life = 1
    reward = 1

    def __init__(self):
        super().__init__()
        self.cur_life = self.total_life
        self.death_sound = \
            monospace.model.res['chunks']['enemies']['death1'].get()
        self.dead = False
        self.res = None

        self.bonuses = monospace.BonusDelay(), None
        self.bonuses_chances = 1, 80

    def update(self, entity, world, model):
        # Check for collision with a bullet
        if self.res is None:
            self.res = model.res

        for en, bullet in world.get_component(monospace.ShipBullet):
            if bullet.hit or self.dead:
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
        self.dead = True

        game = self.world.get_processor(monospace.GameProcessor)
        game.score_up(self.reward)
        self.spawn_particles()

        # Feedback sound
        if self.death_sound is not None:
            Mix_PlayChannel(-1, self.death_sound, 0)

        self.spawn_bonus()

    def spawn_bonus(self):
        """Spawn a bonus for the player, maybe."""
        powerup = random.choices(self.bonuses, self.bonuses_chances)[0]
        if powerup is None:
            return

        pos = self.get(dsdl.Position)
        text = monospace.model.res['text']['powerups']['blank'].get()
        offset = pos.get_offset(text.w, text.h)
        enemy_text = self.get(ctypes.POINTER(SDL_Texture))
        self.world.create_entity(
            monospace.PowerupBox(powerup),
            dsdl.Position(pos.x - offset[0] + enemy_text.w // 2,
                          pos.y - offset[1] + enemy_text.h // 2,
                          dsdl.Offset.CENTER),
            text,
            dsdl.Velocity(0, 2),
            dsdl.BoundingBox(dsdl.Offset.CENTER, text.w, text.h))

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
                monospace.model.res['text']['part']['circle'].get(),
                dsdl.Velocity(x=math.cos(angle) * mag, y=math.sin(angle) * mag)
            )


class RollEnemy(Enemy):
    """Roll enemy controller."""
    hor_speed = 6
    total_life = 1

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
                monospace.model.res['text']['part']['circle'].get(),
                dsdl.Velocity(x=math.cos(angle) * mag, y=math.sin(angle) * mag)
            )


class RocketEnemy(Enemy):
    total_life = 5
    reward = 2

    def __init__(self):
        super().__init__()
        self.death_sound = \
            monospace.model.res['chunks']['enemies']['death2'].get()

    def particles_coroutine(self):
        texture = self.get(ctypes.POINTER(SDL_Texture))
        position = self.get(dsdl.Position)
        offset = position.get_offset(texture.w, texture.h)

        # Spawn particles three times in time
        for _ in range(3):
            for _ in range(random.randrange(6, 9)):
                angle = math.radians(random.randrange(0, 360))
                mag = random.randrange(2, 3)
                size = random.randrange(3, 4)

                self.world.create_entity(
                    dsdl.Particle(60, -0.1 / 40, -0.002),
                    dsdl.Position(position.x - offset[0] + texture.w // 2,
                                  position.y - offset[1] + texture.h // 2,
                                  size_x=1 / size, size_y=1 / size,
                                  offset=dsdl.Offset.CENTER),
                    monospace.model.res['text']['part']['circle'].get(),
                    dsdl.Velocity(x=math.cos(angle) * mag,
                                  y=math.sin(angle) * mag)
                )

            yield 15

    def spawn_particles(self):
        """Spawn death particles for the death."""
        self.processor(desper.CoroutineProcessor).start(
            self.particles_coroutine())


class ShooterEnemy(Enemy):
    """An enemy that takes aim and shoots you."""
    total_life = 2
    HORIZONTAL_SPEED = 3

    def __init__(self):
        super().__init__()
        self.death_sound = \
            monospace.model.res['chunks']['enemies']['death2'].get()
        self._shooting = False
        self._shot = False
        self.target_x = 0

    def on_attach(self, en, world):
        super().on_attach(en, world)

        try:
            self.target_x = \
                self.world.get_component(monospace.Ship)[0][1].position.x
        except IndexError:
            self.target_x = random.randrange(0, monospace.LOGICAL_WIDTH)

        self._shooting = False
        self._shot = False
        self.set_speed()

        self.blaster = monospace.Blaster(
            (0, 0), monospace.EnemyBullet,
            monospace.model.res['text']['enemies']['bullet'].get(),
            30, (0, 5), (10, 10, dsdl.Offset.BOTTOM_CENTER), world,
            animation=(2, 5))

    def update(self, *args):
        super().update(*args)

        # If aligned with the ship horizontally, stop and start shooting
        if (not self._shooting
            and abs(self.get(dsdl.Position).x - self.target_x)
                < self.HORIZONTAL_SPEED):
            self.get(dsdl.Position).x = self.target_x
            self.get(dsdl.Velocity).x = 0
            self._shooting = True

            anim = self.get(dsdl.Animation)
            if anim.cur_frame == 0:
                anim.run = True

        if self._shooting and not self._shot:
            pos = self.get(dsdl.Position)
            self._shot = self.blaster.shoot(pos.x, pos.y)
            if self._shot:
                self.processor(desper.CoroutineProcessor).start(self.target())
                # Feedback sound
                Mix_PlayChannel(
                    -1, monospace.model.res['chunks']['enemies']['shot'].get(),
                    0)

    def target(self):
        """Coroutine that chooses a new target."""
        yield 60

        try:
            self.target_x = \
                self.world.get_component(monospace.Ship)[0][1].position.x
        except IndexError:
            self.target_x = random.randrange(0, monospace.LOGICAL_WIDTH)

        self._shooting = False
        self._shot = False
        self.set_speed()

    def set_speed(self):
        try:
            self.get(dsdl.Velocity).x = math.copysign(
                self.HORIZONTAL_SPEED,
                self.target_x - self.get(dsdl.Position).x)
        except Exception:
            pass

    def spawn_particles(self):
        """Spawn death particles for the death."""
        texture = self.get(ctypes.POINTER(SDL_Texture))
        position = self.get(dsdl.Position)
        offset = position.get_offset(texture.w, texture.h)
        for _ in range(random.randrange(4, 8)):
            angle = math.radians(
                random.randint(0, 1) * 180 - random.randint(-10, 10))
            mag = random.randrange(2, 4)

            self.world.create_entity(
                dsdl.Particle(30, -0.1 / 64, -0.002),
                dsdl.Position(position.x - offset[0] + texture.w // 2,
                              position.y - offset[1] + texture.h // 2,
                              size_x=6 / 64, size_y=10 / 64,
                              offset=dsdl.Offset.CENTER),
                monospace.model.res['text']['part']['circle'].get(),
                dsdl.Velocity(x=math.cos(angle) * mag, y=math.sin(angle) * mag)
            )


class SphereEnemy(Enemy):
    """Stealth enemy that is hard to spot."""
    total_life = 4
    reward = 2

    BASE_ALPHA = 40
    ALPHA_WIGGLE = 30

    def on_attach(self, en, world):
        super().on_attach(en, world)
        self.death_sound = \
            monospace.model.res['chunks']['enemies']['death3'].get()

        self.get(dsdl.Position).alpha = self.BASE_ALPHA
        self._sin_time = 0

    def update(self, *args):
        super().update(*args)

        pos = self.get(dsdl.Position)

        # Rotate
        pos.rot = (pos.rot + 1) % 360

        # Alpha oscillator
        self._sin_time += 1
        pos.alpha = (self.BASE_ALPHA + self.ALPHA_WIGGLE
                     * math.sin(self._sin_time * 1 / 50))

    def spawn_particles(self):
        pos = self.get(dsdl.Position)

        sides = 5
        mag = 3
        base_angle = random.randrange(0, 360)
        for i in range(sides):
            angle = math.radians(base_angle + i * 360 // sides)

            self.world.create_entity(
                dsdl.Particle(60, -1 / 30, -mag / 60),
                dsdl.Position(pos.x, pos.y),
                monospace.model.res['text']['part']['circle'].get(),
                dsdl.Velocity(math.cos(angle) * mag, math.sin(angle) * mag))


# Spawn functions
def spawn_shooter(world):
    """Spawn a shooter enemy."""
    text = monospace.model.res['text']['enemies']['shooter'].get()
    pos_x = random.choice((-60, monospace.LOGICAL_WIDTH + 60))
    pos_y = random.randint(text.h, monospace.LOGICAL_HEIGHT // 3)
    world.create_entity(
        dsdl.Position(pos_x, pos_y, offset=dsdl.Offset.CENTER),
        dsdl.BoundingBox(w=50, h=50, offset=dsdl.Offset.CENTER),
        dsdl.Velocity(),
        text, monospace.ShooterEnemy(),
        dsdl.Animation(7, 2, oneshot=True, run=False))


def spawn_roll(world, speed):
    """Spawn a roll enemy with the given vertical speed."""
    text = monospace.model.res['text']['enemies']['roll'].get()
    pos_x = random.randint(text.w, monospace.LOGICAL_WIDTH - text.w)
    world.create_entity(
        dsdl.Position(pos_x, -text.h, offset=dsdl.Offset.CENTER),
        dsdl.BoundingBox(w=50, h=50, offset=dsdl.Offset.CENTER),
        dsdl.Velocity(0, speed),
        text, monospace.RollEnemy())


def spawn_rocket(world, speed):
    """Spawn a rocket enemy with the given vertical speed."""
    text = monospace.model.res['text']['enemies']['rocket'].get()
    pos_x = random.randint(text.w, monospace.LOGICAL_WIDTH - text.w)
    world.create_entity(
        dsdl.Position(pos_x, -text.h, offset=dsdl.Offset.CENTER),
        dsdl.BoundingBox(w=50, h=50, offset=dsdl.Offset.CENTER),
        dsdl.Velocity(0, speed),
        text, monospace.RocketEnemy())
