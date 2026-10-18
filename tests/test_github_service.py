from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from gitb.service.GitHubService import GitHubService


@pytest.fixture
def g() -> MagicMock:
    g = MagicMock()
    g.get_user.return_value.login = "Me"
    return g


@pytest.fixture
def service(g: MagicMock) -> GitHubService:
    with patch("gitb.service.GitHubService.Github", return_value=g):
        return GitHubService("token")


def repos(*names: str, owner: str) -> list[SimpleNamespace]:
    return [SimpleNamespace(name=n, owner=SimpleNamespace(login=owner)) for n in names]


def test_authenticated_user_repos_include_private(
    service: GitHubService, g: MagicMock
) -> None:
    # /user/repos is the only endpoint that lists the private repos of the token owner
    g.get_user.return_value.get_repos.return_value = repos(
        "public", "private", owner="me"
    )
    assert service.get_organization_repo_names("me") == ["public", "private"]
    g.get_user.return_value.get_repos.assert_called_once_with(affiliation="owner")
    g.get_organization.assert_not_called()


def test_other_user_repos_use_public_endpoint(
    service: GitHubService, g: MagicMock
) -> None:
    g.get_user.side_effect = lambda *args: (
        g.get_user.return_value if not args else other
    )
    other = MagicMock()
    other.get_repos.return_value = repos("theirs", owner="other")
    assert service.get_user_owned_repo_names("other") == ["theirs"]


def test_organization_repos_include_private(
    service: GitHubService, g: MagicMock
) -> None:
    g.get_organization.return_value.get_repos.return_value = repos(
        "shared", "secret", owner="org"
    )
    assert service.get_organization_repo_names("org") == ["shared", "secret"]
    g.get_organization.assert_called_once_with("org")
    g.get_organization.return_value.get_repos.assert_called_once_with(type="all")


def test_clone_authenticates_without_persisting_token(
    service: GitHubService, tmp_path: Path
) -> None:
    with patch("gitb.service.ProviderService.Repo.clone_from") as clone_from:
        service.clone_repo("https://github.com/me/private", tmp_path, "secret")
    url, _path = clone_from.call_args.args
    assert url == "https://github.com/me/private"
    env = clone_from.call_args.kwargs["env"]
    assert env["GIT_CONFIG_KEY_0"] == "http.extraHeader"
    # base64 of "x-access-token:secret"
    assert (
        env["GIT_CONFIG_VALUE_0"] == "Authorization: Basic eC1hY2Nlc3MtdG9rZW46c2VjcmV0"
    )
