#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum


class FlattenLevel(Enum):
    ROOT = 1
    USER = 2
    PROVIDER = 3
    ORGANIZATION = 4
    REPO = 5
