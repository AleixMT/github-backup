from collections.abc import Callable

from src.defines.ProviderType import ProviderType
from src.model.Provider import Provider
from src.model.Repository import Repository

GITHUB = Provider(ProviderType.GITHUB, "https://github.com", "token")
GITLAB = Provider(ProviderType.GITLAB, "https://gitlab.com/", "token")

RepoFactory = Callable[..., Repository]


def make_repo(
    name: str = "repo",
    organization: str = "org",
    provider: Provider = GITHUB,
    owner: str = "me",
    backup: str = "bk",
) -> Repository:
    link = f"{provider.url.rstrip('/')}/{organization}/{name}"
    return Repository(backup, owner, provider, organization, name, link)
