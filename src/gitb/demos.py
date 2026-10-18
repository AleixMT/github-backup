from gitb.service.GitHubService import GitHubService
from gitb.service.ProviderService import ProviderService
from gitb.service.TokenService import get_github_official_token


def get_my_gh_organization_names() -> None:
    gh: ProviderService = GitHubService(get_github_official_token())
    print(gh.get_user_organization_names("AleixMT"))


def get_my_gh_owned_repo_names() -> None:
    gh: ProviderService = GitHubService(get_github_official_token())
    print(gh.get_user_owned_repo_names("AleixMT"))


def get_my_gh_collaboration_repo_names() -> None:
    gh: ProviderService = GitHubService(get_github_official_token())
    print(gh.get_user_collaboration_repo_names("AleixMT"))


def get_my_gh_organization_repo_names() -> None:
    gh: ProviderService = GitHubService(get_github_official_token())
    print(gh.get_organization_repo_names("AleixMT"))


def get_my_gh_organizations_repo_names() -> None:
    gh: ProviderService = GitHubService(get_github_official_token())
    for org_name in gh.get_user_organization_names("AleixMT"):
        print("GH organization name: " + org_name)
        print("Repositories:")
        print(gh.get_organization_repo_names(org_name))


def main() -> None:
    get_my_gh_collaboration_repo_names()
    get_my_gh_owned_repo_names()
    get_my_gh_organization_repo_names()
    get_my_gh_organization_names()
    get_my_gh_organizations_repo_names()


if __name__ == "__main__":
    main()
