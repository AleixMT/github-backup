import argparse
from collections.abc import Callable
from pathlib import Path

import pytest

from src.defines.CollisionAction import CollisionAction
from src.defines.RenameStrategy import RenameStrategy
from src.service.ArgumentParserService import (
    build_argument_parser,
    infer_name,
    parse_arguments,
)

Parse = Callable[..., argparse.Namespace]


@pytest.fixture
def parse(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Parse:
    def run(*argv: str) -> argparse.Namespace:
        monkeypatch.setattr(
            "sys.argv", ["github-backup", "user", "-b", str(tmp_path), *argv]
        )
        return parse_arguments(build_argument_parser())

    return run


def test_rejects_hierarchy_when_flattening_all_levels(parse: Parse) -> None:
    with pytest.raises(SystemExit):
        parse("-y", "-F", "ROOT", "USER", "PROVIDER", "ORGANIZATION")


def test_allows_hierarchy_when_flattening_some_levels(parse: Parse) -> None:
    args = parse("-y", "-F", "USER")
    assert args.flatten_directories == ["USER"]


def test_strategies_are_converted_to_enums(parse: Parse) -> None:
    args = parse("-F", "USER", "-R", "SHORTEST", "-S", "IGNORE")
    assert args.rename_strategy is RenameStrategy.SHORTEST
    assert args.collision_strategy is CollisionAction.IGNORE


def test_default_strategies(parse: Parse) -> None:
    args = parse()
    assert args.rename_strategy is RenameStrategy.SHORTEST_SYSTEMATIC
    assert args.collision_strategy is CollisionAction.FULL_UPDATE


def test_existing_output_file_is_kept(parse: Parse, tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    report.write_text("previous report")
    args = parse("-J", str(report))
    assert args.produce_json
    assert report.read_text() == "previous report"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("https://github.com", "github.com"),
        ("gitlab.example.com", "gitlab.example.com"),
        ("http://192.168.1.10", "192.168.1.10"),
    ],
)
def test_infer_name(value: str, expected: str) -> None:
    assert infer_name(value) == expected


def test_infer_name_rejects_invalid_input() -> None:
    with pytest.raises(ValueError, match="Invalid Input"):
        infer_name("not a host!")
