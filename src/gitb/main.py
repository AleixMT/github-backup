from argparse import Namespace
from pathlib import Path

from gitb.defines.FlattenLevel import FlattenLevel
from gitb.defines.ProviderType import ProviderType
from gitb.model.Provider import Provider
from gitb.model.Repository import Repository
from gitb.service.ArgumentParserService import (
    build_argument_parser,
    parse_arguments,
)
from gitb.service.GitHubService import (
    GitHubService,
    build_github_official_provider,
)
from gitb.service.GitLabService import (
    GitLabService,
    build_gitlab_official_provider,
)
from gitb.service.ProviderService import ProviderService, build_custom_provider
from gitb.service.RepositoryService import resolve_collisions
from gitb.service.UnparserService import print_summary

"""
/backup/owner/provider/organization/repo
"""


def build_providers(args: Namespace) -> list[Provider]:
    providers: list[Provider] = []

    if not args.exclude_enterprise:
        if not args.exclude_gitlab:
            providers.append(build_gitlab_official_provider())
        if not args.exclude_github:
            providers.append(build_github_official_provider())
    for custom_provider in args.custom_providers or []:
        if not args.exclude_gitlab:
            providers.append(
                build_custom_provider(ProviderType.GITLAB, custom_provider)
            )
        if not args.exclude_github:
            providers.append(
                build_custom_provider(ProviderType.GITHUB, custom_provider)
            )

    return providers


def build_provider_service(provider: Provider) -> ProviderService:
    if provider.provider is ProviderType.GITLAB:
        return GitLabService(provider.token, provider.url)
    if provider.provider is ProviderType.GITHUB:
        return GitHubService(provider.token, provider.url)
    raise ValueError(f"Unsupported provider type: {provider.provider}")


def ignored_levels(args: Namespace) -> set[FlattenLevel]:
    return {FlattenLevel[name] for name in args.flatten_directories}


def build_model(args: Namespace) -> dict[Path, Repository]:
    repos: list[Repository] = []
    for username in args.usernames:
        for provider in build_providers(args):
            provider_service = build_provider_service(provider)

            organizations = [username]
            organizations.extend(provider_service.get_user_organization_names(username))
            for organization in organizations:
                for repo in provider_service.get_organization_repo_names(organization):
                    new_repo = Repository(
                        args.backup_name,
                        username,
                        provider,
                        organization,
                        repo,
                        provider.url.rstrip("/") + "/" + organization + "/" + repo,
                    )
                    repos.append(new_repo)

    return resolve_collisions(repos, args.rename_strategy, ignored_levels(args))


def clone_repos(model: dict[Path, Repository], backup_folder: str) -> None:
    for key, value in model.items():
        provider_service = build_provider_service(value.provider)
        print(value.link + "   " + backup_folder + "/" + str(key))
        provider_service.clone_repo(
            value.link, Path(backup_folder) / key, value.provider.token
        )


def main() -> None:
    parser = build_argument_parser()
    args = parse_arguments(parser)
    if args.is_verbose:
        print(print_summary(args))
    model = build_model(args)
    clone_repos(model, args.backup_folder)


if __name__ == "__main__":
    main()
