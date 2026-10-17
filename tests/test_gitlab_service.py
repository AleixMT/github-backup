from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.service.GitLabService import GitLabService


@pytest.fixture
def gl() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(gl: MagicMock) -> GitLabService:
    with patch("src.service.GitLabService.Gitlab", return_value=gl):
        return GitLabService("token", "https://gitlab.com/")


def projects(*paths: str, namespace: str = "") -> list[SimpleNamespace]:
    return [SimpleNamespace(path=p, namespace={"full_path": namespace}) for p in paths]


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("gitlab.example.com", "https://gitlab.example.com"),
        ("http://gitlab.local", "http://gitlab.local"),
        ("https://gitlab.com/", "https://gitlab.com/"),
    ],
)
def test_url_gets_a_scheme(url: str, expected: str) -> None:
    with patch("src.service.GitLabService.Gitlab") as gitlab:
        GitLabService("token", url)
    gitlab.assert_called_once_with(expected, private_token="token")


def test_organization_names_are_group_full_paths(
    service: GitLabService, gl: MagicMock
) -> None:
    gl.groups.list.return_value = [
        SimpleNamespace(full_path="group"),
        SimpleNamespace(full_path="group/subgroup"),
    ]
    assert service.get_user_organization_names("me") == ["group", "group/subgroup"]


def test_user_owned_repos(service: GitLabService, gl: MagicMock) -> None:
    user = MagicMock()
    user.projects.list.return_value = projects("a", "b")
    gl.users.list.return_value = [user]
    assert service.get_user_owned_repo_names("me") == ["a", "b"]


def test_unknown_user_has_no_repos(service: GitLabService, gl: MagicMock) -> None:
    gl.users.list.return_value = []
    assert service.get_user_owned_repo_names("nobody") == []


def test_organization_repos_of_a_user(service: GitLabService, gl: MagicMock) -> None:
    # main.py treats the username as one more organization
    user = MagicMock()
    user.projects.list.return_value = projects("personal")
    gl.users.list.return_value = [user]
    assert service.get_organization_repo_names("me") == ["personal"]
    gl.groups.get.assert_not_called()


def test_organization_repos_of_a_group(service: GitLabService, gl: MagicMock) -> None:
    gl.users.list.return_value = []
    gl.groups.get.return_value.projects.list.return_value = projects("shared")
    assert service.get_organization_repo_names("group") == ["shared"]
    gl.groups.get.assert_called_once_with("group")


def test_collaboration_repos_exclude_own_and_group_repos(
    service: GitLabService, gl: MagicMock
) -> None:
    gl.groups.list.return_value = [SimpleNamespace(full_path="group")]
    gl.projects.list.return_value = [
        *projects("own", namespace="me"),
        *projects("shared", namespace="group"),
        *projects("contributed", namespace="someone-else"),
    ]
    assert service.get_user_collaboration_repo_names("me") == ["contributed"]
