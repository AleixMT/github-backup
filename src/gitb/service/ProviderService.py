from abc import ABC, abstractmethod
from pathlib import Path

from git import Repo

from gitb.defines.ProviderType import ProviderType
from gitb.model.Provider import Provider
from gitb.service.TokenService import get_custom_provider_token


class ProviderService(ABC):
    """Interface for provider services like GitHub and GitLab."""

    @abstractmethod
    def get_user_organization_names(self, username: str) -> list[str]: ...

    @abstractmethod
    def get_user_owned_repo_names(self, username: str) -> list[str]: ...

    @abstractmethod
    def get_user_collaboration_repo_names(self, username: str) -> list[str]: ...

    @abstractmethod
    def get_organization_repo_names(self, organization: str) -> list[str]: ...

    def clone_repo(self, url: str, path: Path) -> None:
        Repo.clone_from(url, path)


def build_provider(provider_type: ProviderType, url: str, token: str) -> Provider:
    return Provider(provider_type, url, token)


def build_custom_provider(provider_type: ProviderType, url: str) -> Provider:
    return Provider(provider_type, url, get_custom_provider_token(provider_type, url))
