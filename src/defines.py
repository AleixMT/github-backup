#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


class ProviderType(Enum):
    GITHUB = 1
    GITLAB = 2


class CollisionStrategy(Enum):
    RENAME = 1
    SYSTEMATIC = 2
    IGNORE = 3
    REMOVE = 4


class FlattenLevel(Enum):
    ROOT = 1
    USER = 2
    PROVIDER = 3
    ORGANIZATION = 4


