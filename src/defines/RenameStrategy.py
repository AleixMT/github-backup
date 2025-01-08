#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


class RenameStrategy(Enum):
    SHORTEST = 1
    SHORTEST_SYSTEMATIC = 2
    SYSTEMATIC = 3
    IGNORE = 4