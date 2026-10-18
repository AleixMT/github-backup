from itertools import permutations
from pathlib import Path

import pytest

from gitb.defines.FlattenLevel import FlattenLevel
from gitb.defines.RenameStrategy import RenameStrategy
from gitb.model.Repository import Repository
from gitb.service.RepositoryService import RENAME_LEVELS, resolve_collisions
from tests.helpers import GITHUB, GITLAB, RepoFactory

FLAT = {level for level in FlattenLevel if level is not FlattenLevel.REPO}


def build(strategy: RenameStrategy, repos: list[Repository]) -> dict[Path, Repository]:
    return resolve_collisions(repos, strategy, FLAT)


def paths(model: dict[Path, Repository]) -> set[str]:
    return {str(path) for path in model}


@pytest.mark.parametrize("strategy", list(RenameStrategy))
def test_no_collision_keeps_plain_name(
    make_repo: RepoFactory, strategy: RenameStrategy
) -> None:
    model = build(strategy, [make_repo("x"), make_repo("y")])
    assert paths(model) == {"x", "y"}


def test_ignore_keeps_first_repo(
    make_repo: RepoFactory, capsys: pytest.CaptureFixture[str]
) -> None:
    first = make_repo("x", "a")
    model = build(RenameStrategy.IGNORE, [first, make_repo("x", "b")])
    assert model == {Path("x"): first}
    assert "WARNING" in capsys.readouterr().out


def test_shortest_renames_only_later_repos(make_repo: RepoFactory) -> None:
    model = build(
        RenameStrategy.SHORTEST,
        [make_repo("x", "a"), make_repo("x", "b"), make_repo("x", "a", GITLAB)],
    )
    assert paths(model) == {"x", "x__b", "x__a"}
    assert model[Path("x")].organization == "a"
    assert model[Path("x")].provider is GITHUB
    assert model[Path("x__a")].provider is GITLAB


def test_shortest_depends_on_order(make_repo: RepoFactory) -> None:
    model = build(RenameStrategy.SHORTEST, [make_repo("x", "b"), make_repo("x", "a")])
    assert paths(model) == {"x", "x__a"}
    assert model[Path("x")].organization == "b"


def test_shortest_ignores_repo_without_free_name(
    make_repo: RepoFactory, capsys: pytest.CaptureFixture[str]
) -> None:
    repos = [make_repo("x") for _ in range(7)]
    model = build(RenameStrategy.SHORTEST, repos)
    # Plain name plus one per longer name level
    assert len(model) == len(RENAME_LEVELS) + 1
    assert "WARNING" in capsys.readouterr().out


def test_systematic_renames_all_colliding_repos(make_repo: RepoFactory) -> None:
    model = build(
        RenameStrategy.SYSTEMATIC,
        [make_repo("x", "a"), make_repo("x", "b"), make_repo("x", "c"), make_repo("y")],
    )
    assert paths(model) == {
        "x__a__GITHUB__me__bk",
        "x__b__GITHUB__me__bk",
        "x__c__GITHUB__me__bk",
        "y",
    }


def test_systematic_does_not_overwrite_duplicates(
    make_repo: RepoFactory, capsys: pytest.CaptureFixture[str]
) -> None:
    first = make_repo("x")
    model = build(RenameStrategy.SYSTEMATIC, [first, make_repo("x"), make_repo("x")])
    assert list(model.values()) == [first]
    assert "WARNING" in capsys.readouterr().out


def test_shortest_systematic_uses_shortest_distinct_level(
    make_repo: RepoFactory,
) -> None:
    model = build(
        RenameStrategy.SHORTEST_SYSTEMATIC, [make_repo("x", "a"), make_repo("x", "b")]
    )
    assert paths(model) == {"x__a", "x__b"}


def test_shortest_systematic_climbs_levels(make_repo: RepoFactory) -> None:
    # Same organization, so the provider is needed to tell them apart
    model = build(
        RenameStrategy.SHORTEST_SYSTEMATIC,
        [make_repo("x", "a"), make_repo("x", "a", GITLAB)],
    )
    assert paths(model) == {"x__a__GITHUB", "x__a__GITLAB"}


def test_shortest_systematic_uses_one_level_for_the_whole_group(
    make_repo: RepoFactory,
) -> None:
    # The organization is not enough for the two "a" repos, so all of them use the provider
    model = build(
        RenameStrategy.SHORTEST_SYSTEMATIC,
        [make_repo("x", "a"), make_repo("x", "b"), make_repo("x", "a", GITLAB)],
    )
    assert paths(model) == {"x__a__GITHUB", "x__b__GITHUB", "x__a__GITLAB"}


def test_shortest_systematic_ignores_identical_repo(
    make_repo: RepoFactory, capsys: pytest.CaptureFixture[str]
) -> None:
    first = make_repo("x")
    model = build(RenameStrategy.SHORTEST_SYSTEMATIC, [first, make_repo("x")])
    assert list(model.values()) == [first]
    assert "WARNING" in capsys.readouterr().out


@pytest.mark.parametrize(
    "strategy", [RenameStrategy.SYSTEMATIC, RenameStrategy.SHORTEST_SYSTEMATIC]
)
def test_systematic_strategies_do_not_depend_on_order(
    make_repo: RepoFactory, strategy: RenameStrategy
) -> None:
    repos = [
        make_repo("x", "a"),
        make_repo("x", "b"),
        make_repo("x", "a", GITLAB),
        make_repo("x__a", "z"),
        make_repo("y"),
    ]
    results = {
        frozenset(
            (str(path), repo.link)
            for path, repo in build(strategy, list(order)).items()
        )
        for order in permutations(repos)
    }
    assert len(results) == 1


def test_renamed_path_does_not_take_a_base_path(make_repo: RepoFactory) -> None:
    # "x__a" is the plain name of another repo, so the "x" group cannot use it
    plain = make_repo("x__a", "z")
    model = build(
        RenameStrategy.SHORTEST_SYSTEMATIC,
        [make_repo("x", "a"), make_repo("x", "b"), plain],
    )
    assert paths(model) == {"x__a", "x__a__GITHUB", "x__b__GITHUB"}
    assert model[Path("x__a")] is plain


def test_shortest_renamed_path_does_not_take_a_base_path(
    make_repo: RepoFactory,
) -> None:
    plain = make_repo("x__b", "z")
    model = build(
        RenameStrategy.SHORTEST, [make_repo("x", "a"), make_repo("x", "b"), plain]
    )
    assert paths(model) == {"x", "x__b", "x__b__GITHUB"}
    assert model[Path("x__b")] is plain


def test_renamed_path_does_not_take_a_vacated_base_path(
    make_repo: RepoFactory,
) -> None:
    # Group "x__a" is renamed, but its plain name stays reserved for nobody
    model = build(
        RenameStrategy.SHORTEST_SYSTEMATIC,
        [
            make_repo("x", "a"),
            make_repo("x", "b"),
            make_repo("x__a", "p"),
            make_repo("x__a", "q"),
        ],
    )
    assert paths(model) == {"x__a__GITHUB", "x__b__GITHUB", "x__a__p", "x__a__q"}


def test_renamed_paths_of_two_groups_do_not_collide(make_repo: RepoFactory) -> None:
    # Group "x" renames to "x__a__GITHUB", which is also the organization level
    # name of a repo called "x__a" in an organization called "GITHUB"
    repos = [
        make_repo("x", "a"),
        make_repo("x", "a", GITLAB),
        make_repo("x__a", "GITHUB"),
        make_repo("x__a", "q"),
    ]
    model = build(RenameStrategy.SHORTEST_SYSTEMATIC, repos)
    assert len(model) == len(repos)
    assert {repo.link for repo in model.values()} == {repo.link for repo in repos}
