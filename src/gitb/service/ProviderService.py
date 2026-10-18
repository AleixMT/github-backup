import base64
from abc import ABC, abstractmethod
from pathlib import Path

from git import Repo

from gitb.defines.ProviderType import ProviderType
from gitb.model.Provider import Provider
from gitb.service.TokenService import get_custom_provider_token


class ProviderService(ABC):
    """Interface for provider services like GitHub and GitLab."""

    # Username sent along with the token when cloning through HTTPS
    clone_username: str

    @abstractmethod
    def get_user_organization_names(self, username: str) -> list[str]: ...

    @abstractmethod
    def get_user_owned_repo_names(self, username: str) -> list[str]: ...

    @abstractmethod
    def get_user_collaboration_repo_names(self, username: str) -> list[str]: ...

    @abstractmethod
    def get_organization_repo_names(self, organization: str) -> list[str]: ...

    def clone_repo(self, url: str, path: Path, token: str) -> None:
        # Authenticate through an HTTP header passed as environment config, so the token is used to clone private
        # repos but is not persisted in the remote URL or the .git/config of the backup.
        credentials = base64.b64encode(
            f"{self.clone_username}:{token}".encode()
        ).decode()
        env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "http.extraHeader",
            "GIT_CONFIG_VALUE_0": f"Authorization: Basic {credentials}",
        }
        Repo.clone_from(url, path, env=env)


def build_provider(provider_type: ProviderType, url: str, token: str) -> Provider:
    return Provider(provider_type, url, token)


def build_custom_provider(provider_type: ProviderType, url: str) -> Provider:
    return Provider(provider_type, url, get_custom_provider_token(provider_type, url))
