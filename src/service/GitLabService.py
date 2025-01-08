from typing import List

from ProviderService import ProviderService, build_provider
from src.defines.ProviderType import ProviderType


class GitLabService(ProviderService):
    """Service for interacting with GitLab."""

    def __init__(self, access_token):
        self.access_token = access_token
        # Assume some GitLab API client initialization here

    def get_user_organization_names(self, username) -> List[str]:
        pass

    def get_user_owned_repo_names(self, username) -> List[str]:
        pass

    def get_user_collaboration_repo_names(self, username) -> List[str]:
        pass

    def get_organization_repo_names(self, organization) -> List[str]:
        pass


def build_gitlab_official_provider():
    return build_provider('https://gitlab.com/', ProviderType.GITLAB)
