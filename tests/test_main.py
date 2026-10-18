from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

from gitb.defines.RenameStrategy import RenameStrategy
from gitb.main import build_model
from tests.helpers import GITLAB


def test_build_model_links_have_no_double_slash() -> None:
    service = MagicMock()
    service.get_user_organization_names.return_value = ["group"]
    service.get_organization_repo_names.side_effect = lambda org: [f"{org}-repo"]
    args = Namespace(
        usernames=["me"],
        backup_name="bk",
        flatten_directories=[],
        rename_strategy=RenameStrategy.SHORTEST_SYSTEMATIC,
    )

    with (
        patch("gitb.main.build_providers", return_value=[GITLAB]),
        patch("gitb.main.build_provider_service", return_value=service),
    ):
        model = build_model(args)

    assert {str(path): repo.link for path, repo in model.items()} == {
        str(Path("bk/me/GITLAB/me/me-repo")): "https://gitlab.com/me/me-repo",
        str(
            Path("bk/me/GITLAB/group/group-repo")
        ): "https://gitlab.com/group/group-repo",
    }
