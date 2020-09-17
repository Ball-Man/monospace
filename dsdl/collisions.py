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
