import random
import monospace
import dsdl


class Wave:
    """A class representing a game's wave metadata.

    It defines which enemies and with what probability can be spawned
    during a specific wave(and which rewards can be assigned).

    It's a base class and should be implemented to define the lists
    containing the possible spawn function and probabilities.
    """

    def __init__(self):
        self.enemies = [None]
        # Functions that accept a single paramenter of type World, and
        # spawn a designed enemy when invoked.

        self.enemy_chances = [1]

    def spawn(self, world):
        """Main method that spawns enemies from this wave.

        If the extracted spawn function is None, spawn nothing.
        """
        spawn_fun = random.choices(self.enemies, self.enemy_chances)[0]
        if spawn_fun is not None:
            spawn_fun(world)


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
        enemy_bbox = dsdl.BoundingBox(w=50, h=50)
        world.create_entity(
            dsdl.Position(x, y),
            enemy_bbox, dsdl.Velocity(0, 5),
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
