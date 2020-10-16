"""Module for single touch management."""
from collections import deque
from sdl2 import *

finger_stack = deque()  # [fing_id0, fing_id1, ...]
fingers = {}            # {fing_id: SDL_TouchFingerEvent(), ...}


class FingerMotion:
    __slots__ = 'dx', 'dy'

    def __init__(self, dx=0, dy=0):
        self.dx = dx
        self.dy = dy


def finger_id_down(fing_id, struct):
    fingers[fing_id] = FingerMotion()
    finger_stack.append(fing_id)

    # print('down', fing_id)


def finger_id_up(fing_id):
    fingers[fing_id] = None
    try:
        finger_stack.remove(fing_id)
    except ValueError:
        pass

    # print('up', fing_id)


def finger_id_update(fing_id, struct):
    if fingers[fing_id] is None:
        fingers[fing_id] = FingerMotion()

    fingers[fing_id].dx = struct.dx
    fingers[fing_id].dy = struct.dy
