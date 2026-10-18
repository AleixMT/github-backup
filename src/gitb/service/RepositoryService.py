from collections.abc import Collection, Iterable
from pathlib import Path

from gitb.defines.FlattenLevel import FlattenLevel
from gitb.defines.RenameStrategy import RenameStrategy
from gitb.model.Repository import Repository

SEPARATOR = "__"


def compute_path(
    repository: Repository,
    ignored_levels: Collection[FlattenLevel] = (),
    flatten_level: FlattenLevel = FlattenLevel.REPO,
) -> None:
    """Compute repository.path.

    ignored_levels are the hierarchy levels that are not present as folders in the path
    (ROOT: backup, USER: owner, PROVIDER: provider, ORGANIZATION: organization).
    flatten_level tells which levels are appended to the repository folder name to
    disambiguate it, from REPO (only the repo name) down to ROOT (all levels).
    """
    path = Path()
    if FlattenLevel.ROOT not in ignored_levels:
        path /= repository.backup
    if FlattenLevel.USER not in ignored_levels:
        path /= repository.owner
    if FlattenLevel.PROVIDER not in ignored_levels:
        path /= repository.provider.provider.name
    if FlattenLevel.ORGANIZATION not in ignored_levels:
        path /= repository.organization

    # Name parts ordered from the most to the least specific level
    name_parts = [
        repository.name,
        repository.organization,
        repository.provider.provider.name,
        repository.owner,
        repository.backup,
    ]
    # REPO keeps 1 part, ORGANIZATION 2, PROVIDER 3, USER 4, ROOT 5
    parts_count = FlattenLevel.REPO.value - flatten_level.value + 1
    repository.path = path / SEPARATOR.join(name_parts[:parts_count])


# Flatten levels that add more information to the repo folder name, from the shortest
# (ORGANIZATION: repo__org) to the longest (ROOT: repo__org__provider__owner__backup)
RENAME_LEVELS = sorted(
    (level for level in FlattenLevel if level is not FlattenLevel.REPO),
    key=lambda level: level.value,
    reverse=True,
)


def resolve_collisions(
    repos: Iterable[Repository],
    strategy: RenameStrategy,
    ignored_levels: Collection[FlattenLevel] = (),
) -> dict[Path, Repository]:
    """Compute the path of each repo and rename the repos whose paths collide.

    The repos are grouped by their base path (the path without renaming). Repos alone in
    their group keep the base path. Renamed repos never take the base path of any repo,
    nor a path already taken, so a renamed path cannot collide with another group.
    Groups are resolved in path order, so the result does not depend on the order of
    the repos, except for the order inside a group, which SHORTEST and IGNORE use to
    decide which repo keeps the base path.
    """
    groups: dict[Path, list[Repository]] = {}
    for repo in repos:
        compute_path(repo, ignored_levels)
        groups.setdefault(repo.path, []).append(repo)

    model = {path: group[0] for path, group in groups.items() if len(group) == 1}
    taken = set(groups)
    for base_path in sorted(path for path, group in groups.items() if len(group) > 1):
        group = groups[base_path]
        if strategy is RenameStrategy.IGNORE:
            model[base_path] = group[0]
            _ignore(group[1:], base_path)
        elif strategy is RenameStrategy.SHORTEST:
            # The first repo keeps the base path, the others get the shortest free name
            model[base_path] = group[0]
            for repo in group[1:]:
                _place_with_shortest_free_name(model, taken, repo, ignored_levels)
        elif strategy is RenameStrategy.SYSTEMATIC:
            _place_at_level(model, taken, group, ignored_levels, FlattenLevel.ROOT)
        elif strategy is RenameStrategy.SHORTEST_SYSTEMATIC:
            # The shortest level that gives a different free name to every repo
            level = next(
                (
                    level
                    for level in RENAME_LEVELS
                    if _level_fits(taken, group, ignored_levels, level)
                ),
                FlattenLevel.ROOT,
            )
            _place_at_level(model, taken, group, ignored_levels, level)

    return model


def _ignore(repos: Iterable[Repository], path: Path) -> None:
    for repo in repos:
        print(f"WARNING: Ignoring {repo.link}, its path {path} is already taken")


def _place(model: dict[Path, Repository], taken: set[Path], repo: Repository) -> None:
    model[repo.path] = repo
    taken.add(repo.path)


def _place_with_shortest_free_name(
    model: dict[Path, Repository],
    taken: set[Path],
    repo: Repository,
    ignored_levels: Collection[FlattenLevel],
) -> None:
    base_path = repo.path
    for level in RENAME_LEVELS:
        compute_path(repo, ignored_levels, level)
        if repo.path not in taken:
            _place(model, taken, repo)
            return
    repo.path = base_path
    _ignore([repo], base_path)


def _level_fits(
    taken: set[Path],
    group: list[Repository],
    ignored_levels: Collection[FlattenLevel],
    level: FlattenLevel,
) -> bool:
    paths = set()
    for repo in group:
        compute_path(repo, ignored_levels, level)
        if repo.path in taken or repo.path in paths:
            return False
        paths.add(repo.path)
    return True


def _place_at_level(
    model: dict[Path, Repository],
    taken: set[Path],
    group: list[Repository],
    ignored_levels: Collection[FlattenLevel],
    level: FlattenLevel,
) -> None:
    for repo in group:
        compute_path(repo, ignored_levels, level)
        if repo.path in taken:
            # Identical repo, or a path already used by another group
            _ignore([repo], repo.path)
        else:
            _place(model, taken, repo)
