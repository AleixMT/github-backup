#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

from src.defines.FlattenLevel import FlattenLevel


def compute_path(repository, ignore_backup: bool = False, ignore_owner: bool = False, ignore_provider: bool = False,
                 ignore_organization: bool = False, flatten_level: FlattenLevel = FlattenLevel.REPO):
    separator = "__"
    repository.path = Path()
    if not ignore_backup:
        repository.path = repository.path / repository.backup
    if not ignore_owner:
        repository.path = repository.path / repository.owner
    if not ignore_provider:
        repository.path = repository.path / repository.provider.provider.name
    if not ignore_organization:
        repository.path = repository.path / repository.organization

    if flatten_level == FlattenLevel.REPO:
        repository.path = repository.path / repository.name
    elif flatten_level == FlattenLevel.ORGANIZATION:
        repository.path = repository.path / repository.name + separator + repository.organization
    elif flatten_level == FlattenLevel.PROVIDER:
        repository.path = (repository.path / repository.name + separator + repository.organization + separator +
                           repository.provider)
    elif flatten_level == FlattenLevel.USER:
        repository.path = (repository.path / repository.name + separator + repository.organization + separator +
                           repository.provider + separator + repository.user)
    elif flatten_level == FlattenLevel.ROOT:
        repository.path = (repository.path / repository.name + separator + repository.organization + separator +
                           repository.provider + separator + repository.user + separator + repository.backup)

