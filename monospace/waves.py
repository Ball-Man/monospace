import random
import itertools
import monospace
import dsdl


class Wave:
    """A class representing a game's wave metadata.

    It defines which enemies and with what probability can be spawned
    during a specific wave(and which rewards can be assigned).

    It also defines which rewards are spawned at the end of the wave
    (a pool, and a quantity of extracted elements from that pool).

    It's a base class and should be implemented to define the lists
    containing the possible spawn function and probabilities.
    """

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
            rewards = random.choice(tuple(itertools.combinations(self.rewards,
                                                           self.num_rewards)))
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
        self._dots_timer = 0

    def spawn_dot(self, world, x, y=-50):
        """Spawn a dot enemy at given position."""
        world.create_entity(
            dsdl.Position(x, y),
            dsdl.BoundingBox(w=50, h=50), dsdl.Velocity(0, 5),
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
            self.spawn_dots(world, random.randint(1, 3), self.dots_rows)

            self._dots_threshold = random.randint(*self.dots_threshold_range)
            self._dots_timer = 0


class FirstWave(DotsWave):
    """Custom wave for the first one of the game."""

    def __init__(self):
        super().__init__()

        self.rewards = [monospace.powerup_add_blaster]
        self.num_rewards = 1


class SecondWave(DotsWave):
    """Custom wave for the second one of the game."""

    def __init__(self):
        super().__init__()

        self.enemy_threshold_range = 200, 350
        self._enemy_threshold = random.randint(*self.enemy_threshold_range)
        self.dots_threshold_range = 100, 170

        self.enemies = [
            lambda world: self.spawn_roll(world)]
        self.enemy_chances = [1]

    def spawn_dot(self, world, x, y=-50):
        """Spawn a dot enemy at given position."""
        world.create_entity(
            dsdl.Position(x, y),
            dsdl.BoundingBox(w=50, h=50), dsdl.Velocity(0, 7),
            monospace.model.res['text']['enemies']['dot'].get(),
            dsdl.Animation(2, 60), monospace.DotEnemy())

    def spawn_roll(self, world):
        text = monospace.model.res['text']['enemies']['roll'].get()
        pos_x = random.randint(50, monospace.LOGICAL_WIDTH - text.w)
        world.create_entity(
            dsdl.Position(pos_x, -text.h, offset=dsdl.Offset.CENTER),
            dsdl.BoundingBox(w=50, h=50, offset=dsdl.Offset.CENTER),
            dsdl.Velocity(0, 3),
            text, monospace.RollEnemy())
