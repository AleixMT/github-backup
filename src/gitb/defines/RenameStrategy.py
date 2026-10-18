from enum import Enum


class RenameStrategy(Enum):
    SHORTEST = 1
    SHORTEST_SYSTEMATIC = 2
    SYSTEMATIC = 3
    IGNORE = 4
