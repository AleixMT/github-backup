#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


class ProviderType(Enum):
    GITHUB = 1
    GITLAB = 2


class RenameStrategy(Enum):
    SHORTEST = 1
    SHORTEST_SYSTEMATIC = 2
    SYSTEMATIC = 3
    IGNORE = 4


class FlattenLevel(Enum):
    ROOT = 1
    USER = 2
    PROVIDER = 3
    ORGANIZATION = 4


class CollisionAction(Enum):
    FULL_UPDATE = 1
    UPDATE = 2
    IGNORE = 3
    REMOVE = 4



