import random
import itertools
import monospace
import dsdl
from sdl2 import SDL_Color


class Wave:
    """A class representing a game's wave metadata.

    It defines which enemies and with what probability can be spawned
    during a specific wave(and which rewards can be assigned).

    It also defines which rewards are spawned at the end of the wave
    (a pool, and a quantity of extracted elements from that pool).

    It's a base class and should be implemented to define the lists
    containing the possible spawn function and probabilities.
    """
    bg_color = SDL_Color(0, 0, 0, 255)

    def __init__(self):
        self.enemies = [None]
        # Functions that accept a single paramenter of type World, and
        # spawn a designed enemy when invoked.
        self.enemy_chances = [1]

        self.rewards = []
        # Powerup functions to be incapsulated into PowerupBox.
        self.reward_chances = []
        self.num_rewards = 0

        self.enemy_threshold_range = 200, 300
        self._enemy_timer = 0
        self._enemy_threshold = random.randint(*self.enemy_threshold_range)

    def spawn(self, world):
        """Main method that spawns enemies from this wave.

        If the extracted spawn function is None, spawn nothing.
        """
        self._enemy_timer += 1
        if self._enemy_timer > self._enemy_threshold:
            spawn_fun = random.choices(self.enemies, self.enemy_chances)[0]
            if spawn_fun is not None:
                spawn_fun(world)

            # Reset timer
            self._enemy_threshold = random.randint(*self.enemy_threshold_range)
            self._enemy_timer = 0

    def spawn_rewards(self, world):
        """Method that spawns rewards for the cleared wave(powerups)."""
        if self.num_rewards > 0:
            rewards = random.sample(self.rewards, self.num_rewards)
            for i, reward in enumerate(rewards):
                x = monospace.LOGICAL_WIDTH // (self.num_rewards + 1) * (i + 1)
                y = monospace.LOGICAL_HEIGHT // 2

                world.create_entity(
                    monospace.PowerupBox(reward),
                    dsdl.Position(x, y, dsdl.Offset.CENTER),
                    dsdl.BoundingBox(dsdl.Offset.CENTER, w=50, h=50),
                    monospace.model.res['text']['powerups']['blank'].get())


class DotsWave(Wave):
    """A wave that adds the chance for spawning dots.

    The chance for spawning dots is completely separated from the
    standard spawning probabilities, so that the spawned enemies are
    simply spawned additionally to the dots.
    """

    def __init__(self):
        super().__init__()

        self.dots_threshold_range = 100, 200   # In frames
        self._dots_threshold = random.randint(*self.dots_threshold_range)
        self.dots_rows = 1
        self.dots_columns_range = 1, 3
        self._dots_timer = 0
        self.dots_speed = 5

    def spawn_dot(self, world, x, y=-50):
        """Spawn a dot enemy at given position."""
        world.create_entity(
            dsdl.Position(x, y),
            dsdl.BoundingBox(w=50, h=50), dsdl.Velocity(0, self.dots_speed),
            monospace.model.res['text']['enemies']['dot'].get(),
            dsdl.Animation(2, 60), monospace.DotEnemy())

    def spawn_dots(self, world, columns, rows):
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
                self.spawn_dot(world, x, y)
                x += var_x
            y -= var_y

    def spawn(self, world):
        super().spawn(world)

        # Spawn a dots every x frames
        self._dots_timer += 1
        if self._dots_timer > self._dots_threshold:
            # By default, columns are random from 1 to 3
            self.spawn_dots(world, random.randint(*self.dots_columns_range),
                            self.dots_rows)

            self._dots_threshold = random.randint(*self.dots_threshold_range)
            self._dots_timer = 0


class FirstWave(DotsWave):
    """Custom wave for the first one of the game."""

    def __init__(self):
        super().__init__()

        self.rewards = [monospace.powerup_shield, monospace.powerup_drift]
        self.num_rewards = 1


class SecondWaveRoll(DotsWave):
    """Custom wave for the second one of the game."""
    bg_color = SDL_Color(0, 13, 45, 255)

    def __init__(self):
        super().__init__()

        self.enemy_threshold_range = 100, 350
        self._enemy_threshold = random.randint(*self.enemy_threshold_range)
        self.dots_threshold_range = 70, 160
        self.dots_columns_range = 1, 4
        self.dots_speed = 7

        self.enemies = [
            lambda world: monospace.spawn_roll(world, 3)]
        self.enemy_chances = [1]

        self.rewards = [monospace.powerup_add_blaster,
                        monospace.powerup_delay1,
                        monospace.powerup_double_blasters]
        self.num_rewards = 1


class SecondWaveShooter(DotsWave):
    """Custom wave for the second one of the game."""
    bg_color = SDL_Color(0, 35, 13, 255)

    def __init__(self):
        super().__init__()

        self.enemy_threshold_range = 100, 350
        self._enemy_threshold = random.randint(*self.enemy_threshold_range)
        self.dots_threshold_range = 70, 160
        self.dots_columns_range = 1, 4
        self.dots_speed = 7

        self.enemies = [
            monospace.spawn_shooter]
        self.enemy_chances = [1]

        self.rewards = [monospace.powerup_add_blaster,
                        monospace.powerup_delay1,
                        monospace.powerup_quick,
                        monospace.powerup_help]
        self.num_rewards = 2


class ThirdWave(DotsWave):
    """Custom wave for the second one of the game."""
    bg_color = SDL_Color(0, 0, 0, 255)

    def __init__(self):
        super().__init__()

        self.enemy_threshold_range = 100, 300
        self._enemy_threshold = random.randint(*self.enemy_threshold_range)
        self.dots_threshold_range = 50, 150
        self.dots_rows = 2
        self.dots_columns_range = 1, 4
        self.dots_speed = 8

        self.enemies = [
            lambda world: monospace.spawn_roll(world, 3),
            monospace.spawn_shooter,
            lambda world: monospace.spawn_rocket(world, 4)]
        self.enemy_chances = [10, 10, 1]

        self.rewards = [monospace.powerup_add_blaster,
                        monospace.powerup_delay1]
        self.num_rewards = 2


class ThirdWaveRocket(DotsWave):
    """Custom wave for the second one of the game."""
    bg_color = SDL_Color(45, 0, 0, 255)

    def __init__(self):
        super().__init__()

        self.enemy_threshold_range = 50, 200
        self._enemy_threshold = random.randint(*self.enemy_threshold_range)
        self.dots_threshold_range = 50, 150
        self.dots_rows = 2
        self.dots_columns_range = 1, 4
        self.dots_speed = 7

        self.enemies = [self.spawn_rocket]
        self.enemy_chances = [1]

        self.rewards = [monospace.powerup_add_blaster,
                        monospace.powerup_delay1,
                        monospace.powerup_shield]
        self.num_rewards = 3

    def spawn_rocket(self, world):
        """Spawn special rockets."""
        num = random.choice((1, 2))

        for _ in range(num):
            speed = random.choices((3, 6, 10), (3, 1, 1))[0]
            monospace.spawn_rocket(world, speed)


class FourthWave(DotsWave):
    """Custom wave for the second one of the game."""
    bg_color = SDL_Color(45, 0, 45, 255)

    def __init__(self):
        super().__init__()

        self.enemy_threshold_range = 80, 200
        self._enemy_threshold = random.randint(*self.enemy_threshold_range)
        self.dots_threshold_range = 50, 150
        self.dots_rows = 2
        self.dots_columns_range = 2, 4
        self.dots_speed = 8

        self.enemies = [
            lambda world: monospace.spawn_roll(world, 3),
            lambda world: monospace.spawn_shooter(world, 7),
            lambda world: monospace.spawn_rocket(world, 4),
            lambda world: monospace.spawn_sphere(world, 4)]
        self.enemy_chances = [3, 3, 2, 4]

        self.rewards = [monospace.powerup_add_blaster,
                        monospace.powerup_delay1,
                        monospace.powerup_double_blasters]
        self.num_rewards = 2


class FifthWave(DotsWave):
    """Custom wave for the second one of the game."""
    bg_color = SDL_Color(0, 0, 0, 255)

    def __init__(self):
        super().__init__()

        self.enemy_threshold_range = 80, 120
        self._enemy_threshold = random.randint(*self.enemy_threshold_range)
        self.dots_threshold_range = 50, 100
        self.dots_rows = 3
        self.dots_columns_range = 2, 4
        self.dots_speed = 8

        self.enemies = [
            lambda world: monospace.spawn_roll(world, 3),
            lambda world: monospace.spawn_shooter(world, 8),
            lambda world: monospace.spawn_rocket(world, 4),
            lambda world: monospace.spawn_sphere(world, 4)]
        self.enemy_chances = [1, 1, 1, 1]

        self.rewards = [monospace.powerup_delay1,
                        monospace.powerup_drift,
                        monospace.powerup_help]
        self.num_rewards = 2


class SixthWave(DotsWave):
    """Custom wave for the second one of the game."""
    bg_color = SDL_Color(0, 0, 0, 255)

    def __init__(self):
        super().__init__()

        self.enemy_threshold_range = 80, 120
        self._enemy_threshold = random.randint(*self.enemy_threshold_range)
        self.dots_threshold_range = 50, 100
        self.dots_rows = 2
        self.dots_columns_range = 2, 4
        self.dots_speed = 9

        self.enemies = [
            lambda world: monospace.spawn_roll(world, 4),
            lambda world: monospace.spawn_shooter(world, 9),
            lambda world: monospace.spawn_rocket(world, 5),
            lambda world: monospace.spawn_sphere(world, 4)]
        self.enemy_chances = [1, 1, 1, 1]

        self.rewards = [monospace.powerup_quick, monospace.powerup_help]
        self.num_rewards = 1

    def spawn_dot(self, world, x, y=-50):
        """Spawn stronger dot enemy at given position."""
        world.create_entity(
            dsdl.Position(x, y),
            dsdl.BoundingBox(w=50, h=50), dsdl.Velocity(0, self.dots_speed),
            monospace.model.res['text']['enemies']['dot2'].get(),
            dsdl.Animation(2, 60), monospace.Dot2Enemy())


class SeventhWave(SixthWave):
    """Custom wave for the second one of the game."""
    bg_color = SDL_Color(30, 30, 30, 255)

    def __init__(self):
        super().__init__()

        self.enemy_threshold_range = 50, 100
        self._enemy_threshold = random.randint(*self.enemy_threshold_range)
        self.dots_threshold_range = 40, 80
        self.dots_rows = 2
        self.dots_columns_range = 2, 4
        self.dots_speed = 10

        self.enemies = [
            lambda world: monospace.spawn_roll2(world, 4),
            lambda world: monospace.spawn_shooter(world, 12),
            lambda world: monospace.spawn_rocket2(world, 5),
            lambda world: monospace.spawn_sphere2(world, 4)]
        self.enemy_chances = [1, 1, 1, 1]

        self.rewards = [monospace.powerup_delay1]
        self.num_rewards = 1


class InfWave(SixthWave):
    """Custom wave for the second one of the game."""
    bg_color = SDL_Color(0, 0, 0, 255)

    def __init__(self):
        super().__init__()

        self.enemy_threshold_range = 50, 80
        self._enemy_threshold = random.randint(*self.enemy_threshold_range)
        self.dots_threshold_range = 30, 70
        self.dots_rows = 3
        self.dots_columns_range = 2, 4
        self.dots_speed = 11

        self.enemies = [
            lambda world: monospace.spawn_roll2(world, 3),
            lambda world: monospace.spawn_shooter(world, 15),
            lambda world: monospace.spawn_rocket2(world,
                                                  random.randint(6, 14)),
            lambda world: monospace.spawn_sphere2(world, 7)]
        self.enemy_chances = [1, 1, 1, 1]

        self.rewards = [monospace.powerup_delay1]
        self.num_rewards = 1
