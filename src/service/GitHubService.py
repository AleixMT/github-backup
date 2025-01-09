from typing import Optional, List

from src.service.ProviderService import ProviderService, build_provider
from github import Github
from github import Auth

from src.defines.ProviderType import ProviderType


class GitHubService(ProviderService):
    """Service for interacting with GitHub."""

    def __init__(self, access_token, url: Optional[str] = None):
        if url:
            self.g = Github(base_url=url, auth=Auth.Token(access_token))
        else:
            self.g = Github(auth=Auth.Token(access_token))

    def get_user_organizations(self):
        user_orgs = []
        for orgs in self.g.get_user().get_orgs():
            user_orgs.append(orgs)
        self.g.close()
        return user_orgs

    def get_user_organization_names(self, username) -> List[str]:
        return [org.login for org in self.get_user_organizations()]

    def get_user_repos(self):
        user = self.g.get_user()
        return user.get_repos()

    def get_user_owned_repos(self, username):
        user_repos = self.g.get_user(username).get_repos()
        owned_repos = [repo for repo in user_repos if repo.owner.login == username]
        self.g.close()
        return owned_repos

    def get_user_owned_repo_names(self, username) -> List[str]:
        return [repo.name for repo in self.get_user_owned_repos(username)]

    def get_user_collaboration_repos(self, username):
        user_repos = self.get_user_repos()
        org_names = self.get_user_organization_names(username)
        owned_repos = [repo for repo in user_repos
                       if repo.owner.login != username and repo.owner.login not in org_names]
        self.g.close()
        return owned_repos

    def get_user_collaboration_repo_names(self, username) -> List[str]:
        return [repo.name for repo in self.get_user_collaboration_repos(username)]

    def get_organization_repos(self, organization):
        return self.get_user_owned_repos(organization)

    def get_organization_repo_names(self, organization) -> List[str]:
        return [repo.name for repo in self.get_user_owned_repos(organization)]


def build_github_official_provider():
    return build_provider('https://github.com/', ProviderType.GITHUB)
