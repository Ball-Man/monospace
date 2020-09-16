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


def bbox_to_bbox_collision(bbox1, bbox2):
    """Check for collisions between to bbox(return a boolean)."""
    if (bbox1.x is None or bbox1.y is None or bbox2.x is None
            or bbox2.y is None):
        return False

    if (bbox2.x >= bbox1.x + bbox1.w or bbox1.x >= bbox2.x + bbox2.w
            or bbox2.y >= bbox1.y + bbox1.h or bbox1.y >= bbox2.y + bbox2.h):
        return False
    return True


def bbox_to_circle_collision(bbox, circle):
    """Check for collisions between bbox and circle(return a boolean)."""
    if (bbox.x is None or bbox.y is None or circle.x is None
            or circle.y is None):
        return False

    test_x = circle.x
    test_y = circle.y
    bbox_x2 = bbox.x + bbox.w
    bbox_y2 = bbox.y + bbox.h

    test_x = (circle.x < bbox.x) * bbox.x + (circle.x > bbox_x2) * bbox_x2
    test_y = (circle.y < bbox.y) * bbox.y + (circle.y > bbox_y2) * bbox_y2

    dist2 = (circle.x - test_x) ** 2 + (circle.y - test_y) ** 2

    return dist2 <= circle.rad ** 2


# Dictionary used to lookup collision functions
# collision_functions = {
#     frozenset({BoundingBox, BoundingBox}): bbox_to_bbox_collision,
#     frozenset({BoundingBox, CollisionCircle}): bbox_to_circle_collision
# }


# def check_collisions(collider1, collider2):
#     """Check collisions on the given colliders, based on their types."""
#     pass
