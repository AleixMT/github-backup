from abc import ABC, abstractmethod
from typing import List

from src.model.Provider import Provider
from src.service.TokenService import get_custom_provider_token


class ProviderService(ABC):
    """Interface for provider services like GitHub and GitLab."""

    def get_user_organization_names(self, username) -> List[str]:
        pass

    def get_user_owned_repo_names(self, username) -> List[str]:
        pass

    def get_user_collaboration_repo_names(self, username) -> List[str]:
        pass

    def get_organization_repo_names(self, organization) -> List[str]:
        pass

    def clone_repo(self, url, path):
        pass

    def get_user_organizations(self):
        pass


def build_provider(provider_type, url, token):
    return Provider(provider_type, url, token)


def build_custom_provider(provider_type, url):
    return Provider(provider_type, url, get_custom_provider_token(provider_type, url))
