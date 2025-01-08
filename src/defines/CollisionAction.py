#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


class CollisionAction(Enum):
    FULL_UPDATE = 1
    UPDATE = 2
    IGNORE = 3
    REMOVE = 4