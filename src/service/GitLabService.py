from typing import List, Optional

from src.service.ProviderService import ProviderService, build_provider
from src.defines.ProviderType import ProviderType
from src.service.TokenService import get_gitlab_official_token


class GitLabService(ProviderService):
    """Service for interacting with GitLab."""

    def __init__(self, access_token, url: Optional[str] = None):
        self.access_token = access_token
        if url:
            pass
            #self.g = Github(base_url=url, auth=Auth.Token(access_token))
        else:
            pass
            #self.g = Github(auth=Auth.Token(access_token))

    def get_user_organization_names(self, username) -> List[str]:
        pass

    def get_user_owned_repo_names(self, username) -> List[str]:
        pass

    def get_user_collaboration_repo_names(self, username) -> List[str]:
        pass

    def get_organization_repo_names(self, organization) -> List[str]:
        pass


def build_gitlab_official_provider():
    return build_provider(ProviderType.GITLAB, 'https://gitlab.com/', get_gitlab_official_token())
