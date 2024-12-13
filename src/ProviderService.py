from abc import ABC, abstractmethod
from typing import List


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


def build_provider(url, provider_type):
    return {'url': url, 'type': provider_type, 'orgs': {}}
