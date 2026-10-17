from pathlib import Path

import pytest

from src.defines.FlattenLevel import FlattenLevel
from src.service.RepositoryService import compute_path
from tests.helpers import RepoFactory

ALL_FOLDERS = {
    FlattenLevel.ROOT,
    FlattenLevel.USER,
    FlattenLevel.PROVIDER,
    FlattenLevel.ORGANIZATION,
}


def test_full_hierarchy(make_repo: RepoFactory) -> None:
    repo = make_repo()
    compute_path(repo)
    assert repo.path == Path("bk/me/GITHUB/org/repo")


def test_ignored_levels_are_not_folders(make_repo: RepoFactory) -> None:
    repo = make_repo()
    compute_path(repo, {FlattenLevel.USER, FlattenLevel.ORGANIZATION})
    assert repo.path == Path("bk/GITHUB/repo")


@pytest.mark.parametrize(
    ("level", "expected"),
    [
        (FlattenLevel.REPO, "repo"),
        (FlattenLevel.ORGANIZATION, "repo__org"),
        (FlattenLevel.PROVIDER, "repo__org__GITHUB"),
        (FlattenLevel.USER, "repo__org__GITHUB__me"),
        (FlattenLevel.ROOT, "repo__org__GITHUB__me__bk"),
    ],
)
def test_flatten_level_appends_name_parts(
    make_repo: RepoFactory, level: FlattenLevel, expected: str
) -> None:
    # Used to fail with TypeError (Path + str) and AttributeError (repository.user)
    repo = make_repo()
    compute_path(repo, ALL_FOLDERS, level)
    assert repo.path == Path(expected)
