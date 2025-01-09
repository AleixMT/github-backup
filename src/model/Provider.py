#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum

from src.defines.ProviderType import ProviderType


class Provider:
    def __init__(self, url: str, provider: ProviderType, token: str):
        self.url = url
        self.provider = provider
        self.token = token


