import math
import functools
import dsdl


class BoundingBox:
    """Rectangle representing a collision bounding box."""

    def __init__(self, offset=dsdl.Offset.ORIGIN, w=0, h=0):
        self.x = None
        self.y = None
        self.w = w
        self.h = h

        if isinstance(offset, (list, tuple)) and len(offset) != 2:
            raise TypeError('Please provide two values for an offset(x, y)')
        elif (not isinstance(offset, (list, tuple))
              and not isinstance(offset, dsdl.Offset)):
            raise TypeError('The given offset should be of type dsdl.Offset, \
                             or of type list/tuple providing two values(x, y)')

        self.offset = offset

    def overlaps(self, bbox):
        """Check for the collision between this box and a given one."""
        if (self.x is None or self.y is None or bbox.x is None
                or bbox.y is None):
            return False

        if (bbox.x >= self.x + self.w or self.x >= bbox.x + bbox.w
                or bbox.y >= self.y + self.h or self.y >= bbox.y + bbox.h):
            return False
        return True


class CollisionCircle:
    """Circle representing a collision."""

    def __init__(self, rad):
        self.x = None
        self.y = None
        self.rad = rad

    def overlaps(self, circle):
        """Check for the collision between this circle and another."""
        if (self.x is None or self.y is None or circle.x is None
                or circle.y is None):
            return False

        return ((self.x - circle.x) ** 2 + (self.y - circle.y) ** 2
                <= (self.rad + circle.rad) ** 2)


def bbox_to_bbox_collision(dic):
    """Check for collisions between to bbox(return a boolean).

    Accepts a dictionary in the form {class: (instance, )}.
    """
    bbox1, bbox2 = dic[BoundingBox]

    if (bbox1.x is None or bbox1.y is None or bbox2.x is None
            or bbox2.y is None):
        return False

    if (bbox2.x >= bbox1.x + bbox1.w or bbox1.x >= bbox2.x + bbox2.w
            or bbox2.y >= bbox1.y + bbox1.h or bbox1.y >= bbox2.y + bbox2.h):
        return False
    return True


def bbox_to_circle_collision(dic):
    """Check for collisions between bbox and circle(return a boolean).

    Accepts a dictionary in the form {class: (instance, )}.
    """
    bbox = dic[BoundingBox][0]
    circle = dic[CollisionCircle][0]

    if (bbox.x is None or bbox.y is None or circle.x is None
            or circle.y is None):
        return False

    test_x = circle.x
    test_y = circle.y
    bbox_x2 = bbox.x + bbox.w
    bbox_y2 = bbox.y + bbox.h

    if circle.x < bbox.x:
        test_x = bbox.x
    elif circle.x > bbox_x2:
        test_x = bbox_x2

    if circle.y < bbox.y:
        test_y = bbox.y
    elif circle.y > bbox_y2:
        test_y = bbox_y2

    dist2 = (circle.x - test_x) ** 2 + (circle.y - test_y) ** 2

    return dist2 <= circle.rad ** 2


def circle_to_circle_collision(dic):
    """Check for collisions between circle and circle(return a boolean).

    Accepts a dictionary in the form {class: (instance, )}
    """
    circle1, circle2 = dic[CollisionCircle]

    if (circle1.x is None or circle1.y is None or circle2.x is None
            or circle2.y is None):
        return False

    return ((circle1.x - circle2.x) ** 2 + (circle1.y - circle2.y) ** 2
                <= (circle1.rad + circle2.rad) ** 2)


# Dictionary used to lookup collision functions
collision_functions = {
    frozenset({BoundingBox}): bbox_to_bbox_collision,
    frozenset({BoundingBox, CollisionCircle}): bbox_to_circle_collision,
    frozenset({CollisionCircle}): circle_to_circle_collision
}


def check_collisions(collider1, collider2):
    """Check collisions on the given colliders, based on their types."""
    dic = {}
    type1, type2 = type(collider1), type(collider2)

    if type1 is type2:
        dic[type1] = collider1, collider2
    else:
        dic[type1] = (collider1, )
        dic[type2] = (collider2, )

    return collision_functions[frozenset((type1, type2))](dic)


class SpatialHash:
    """Data structure for optimized collision detection.

    It stores couples (Object, BoundingBox) in a grid.
    """

    def __init__(self, width, height, grid_size):
        self.grid_size = grid_size
        self.width = width
        self.height = height
        self.num_columns = math.ceil(width / grid_size)
        self.num_rows = math.ceil(height / grid_size)
        self._grid = []
        for x in range(self.num_columns + 1):
            col = []
            self._grid.append(col)
            for y in range(self.num_rows + 1):
                col.append(set())

        self._population = {}       # (Object, BoundingBox): {(x, y), ...}

        print(self.num_rows, self.num_columns)

    def update(self, couple):
        """Add object to the grid, if not present.

        If already present, update its position.
        """
        bbox = couple[1]
        if bbox.x is None or bbox.y is None:
            return

        new_pos = set()
        x1 = int(bbox.x // self.grid_size)
        y1 = int(bbox.y // self.grid_size)
        x2 = int((bbox.x + bbox.w) // self.grid_size)
        y2 = int((bbox.y + bbox.h) // self.grid_size)

        # New population set
        positions = (x1, y1), (x1, y2), (x1, y2), (x2, y2)
        for pos in positions:
            if (0 <= pos[0] <= self.num_columns
                    and 0 <= pos[1] <= self.num_rows):
                new_pos.add(pos)

        # Remove from previous locations
        for pos in self._population.get(couple, set()) - new_pos:
            self._grid[pos[0]][pos[1]].discard(couple)
        # Add to new locations
        for pos in new_pos - self._population.get(couple, set()):
            self._grid[pos[0]][pos[1]].add(couple)

        # Update population
        self._population[couple] = new_pos

    def remove(self, couple):
        """Remove an object from the grid, if present."""
        pop = self._population.get(couple, set())
        for pos in pop:
            self._grid[pos[0]][pos[1]].discard(couple)

        pop.discard(couple)

    def get(self, x, y):
        """Get the content of the cell of (non hashed) x, y."""
        if x > self.width or y > self.height or x < 0 or y < 0:
            return set()

        return self._grid[int(x // self.grid_size)][int(y // self.grid_size)]

    def get_from_bbox(self, bbox):
        """Get the content of all the cells where a bbox intersects."""
        if bbox.x is None or bbox.y is None:
            return set()

        x1 = bbox.x
        x2 = bbox.x + bbox.w
        y1 = bbox.y
        y2 = bbox.y + bbox.h
        points = ((x1, y1), (x1, y2), (x2, y1), (x2, y2))

        return functools.reduce(lambda s, x: s.union(x),
                                (self.get(*p) for p in points))
