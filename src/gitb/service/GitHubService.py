from github import Auth, Github
from github.Organization import Organization
from github.PaginatedList import PaginatedList
from github.Repository import Repository as GitHubRepository

from gitb.defines.ProviderType import ProviderType
from gitb.model.Provider import Provider
from gitb.service.ArgumentParserService import infer_name
from gitb.service.ProviderService import ProviderService, build_provider
from gitb.service.TokenService import get_github_official_token


class GitHubService(ProviderService):
    """Service for interacting with GitHub."""

    clone_username = "x-access-token"

    def __init__(self, access_token: str, url: str | None = None) -> None:
        if url and infer_name(url) != "github.com":
            self.g = Github(base_url=url, auth=Auth.Token(access_token))
        else:
            self.g = Github(auth=Auth.Token(access_token))

    def get_user_organizations(self) -> list[Organization]:
        user_orgs = list(self.g.get_user().get_orgs())
        self.g.close()
        return user_orgs

    def get_user_organization_names(self, username: str) -> list[str]:
        return [org.login for org in self.get_user_organizations()]

    def get_user_repos(self) -> PaginatedList[GitHubRepository]:
        user = self.g.get_user()
        return user.get_repos()

    def is_authenticated_user(self, username: str) -> bool:
        return self.g.get_user().login.lower() == username.lower()

    def get_user_owned_repos(self, username: str) -> list[GitHubRepository]:
        # /users/{username}/repos only lists public repos, even when authenticated. /user/repos also lists the private
        # repos of the token owner.
        if self.is_authenticated_user(username):
            user_repos = self.g.get_user().get_repos(affiliation="owner")
        else:
            user_repos = self.g.get_user(username).get_repos()
        owned_repos = [repo for repo in user_repos if repo.owner.login == username]
        self.g.close()
        return owned_repos

    def get_user_owned_repo_names(self, username: str) -> list[str]:
        return [repo.name for repo in self.get_user_owned_repos(username)]

    def get_user_collaboration_repos(self, username: str) -> list[GitHubRepository]:
        user_repos = self.get_user_repos()
        org_names = self.get_user_organization_names(username)
        owned_repos = [
            repo
            for repo in user_repos
            if repo.owner.login != username and repo.owner.login not in org_names
        ]
        self.g.close()
        return owned_repos

    def get_user_collaboration_repo_names(self, username: str) -> list[str]:
        return [repo.name for repo in self.get_user_collaboration_repos(username)]

    def get_organization_repos(self, organization: str) -> list[GitHubRepository]:
        # Like in GitLab, the user itself is also treated as an organization
        if self.is_authenticated_user(organization):
            return self.get_user_owned_repos(organization)
        # type="all" includes the private repos of the organization visible to the token owner
        return list(self.g.get_organization(organization).get_repos(type="all"))

    def get_organization_repo_names(self, organization: str) -> list[str]:
        return [repo.name for repo in self.get_organization_repos(organization)]


def build_github_official_provider() -> Provider:
    return build_provider(
        ProviderType.GITHUB, "https://github.com", get_github_official_token()
    )
