from gitlab import Gitlab
from gitlab.const import AccessLevel
from gitlab.v4.objects import GroupProject, Project, UserProject

from src.defines.ProviderType import ProviderType
from src.model.Provider import Provider
from src.service.ProviderService import ProviderService, build_provider
from src.service.TokenService import get_gitlab_official_token


class GitLabService(ProviderService):
    """Service for interacting with GitLab."""

    def __init__(self, access_token: str, url: str | None = None) -> None:
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.gl = Gitlab(url, private_token=access_token)

    def get_user_organization_names(self, username: str) -> list[str]:
        # Groups (and subgroups) the authenticated user is a member of
        groups = self.gl.groups.list(min_access_level=AccessLevel.GUEST, get_all=True)
        return [group.full_path for group in groups]

    def get_user_owned_repos(self, username: str) -> list[UserProject]:
        user = next(iter(self.gl.users.list(username=username)), None)
        if user is None:
            return []
        return list(user.projects.list(get_all=True))

    def get_user_owned_repo_names(self, username: str) -> list[str]:
        return [project.path for project in self.get_user_owned_repos(username)]

    def get_user_collaboration_repos(self, username: str) -> list[Project]:
        org_names = self.get_user_organization_names(username)
        return [
            project
            for project in self.gl.projects.list(membership=True, get_all=True)
            if project.namespace["full_path"] != username
            and project.namespace["full_path"] not in org_names
        ]

    def get_user_collaboration_repo_names(self, username: str) -> list[str]:
        return [project.path for project in self.get_user_collaboration_repos(username)]

    def get_organization_repos(
        self, organization: str
    ) -> list[UserProject] | list[GroupProject]:
        # Like in GitHub, the user itself is also treated as an organization
        user_repos = self.get_user_owned_repos(organization)
        if user_repos:
            return user_repos
        group = self.gl.groups.get(organization)
        return list(group.projects.list(get_all=True))

    def get_organization_repo_names(self, organization: str) -> list[str]:
        return [project.path for project in self.get_organization_repos(organization)]


def build_gitlab_official_provider() -> Provider:
    return build_provider(
        ProviderType.GITLAB, "https://gitlab.com/", get_gitlab_official_token()
    )
