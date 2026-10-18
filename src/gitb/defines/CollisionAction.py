from enum import Enum


class CollisionAction(Enum):
    FULL_UPDATE = 1
    UPDATE = 2
    IGNORE = 3
    REMOVE = 4
