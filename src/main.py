#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.defines.FlattenLevel import FlattenLevel
from src.defines.RenameStrategy import RenameStrategy
from src.model.Repository import Repository
from src.service.GitHubService import GitHubService, build_github_official_provider
from src.service.ProviderService import ProviderService, build_provider, build_custom_provider
from src.service.RepositoryService import compute_path
from src.service.TokenService import get_github_official_token, get_custom_provider_token, get_gitlab_official_token
from src.defines.ProviderType import ProviderType
from src.service.GitLabService import build_gitlab_official_provider, GitLabService
from src.service.ArgumentParserService import build_argument_parser, parse_arguments
from src.service.UnparserService import print_summary

'''
/backup/owner/provider/organization/repo
'''


def build_model(args):
    providers = []

    if args.custom_providers:
        providers.extend(args.custom_providers)

    if not args.exclude_enterprise:
        if args.exclude_github:
            providers.append(build_gitlab_official_provider())
        if args.exclude_gitlab:
            providers.append(build_github_official_provider())
        if not args.exclude_gitlab and not args.exclude_github:
            providers.append(build_gitlab_official_provider())
            providers.append(build_github_official_provider())
    if args.custom_providers:
        for custom_provider in args.custom_providers:
            if args.exclude_github:
                providers.append(build_custom_provider(ProviderType.GITLAB, custom_provider))
            if args.exclude_gitlab:
                providers.append(build_custom_provider(ProviderType.GITHUB, custom_provider))
            if not args.exclude_gitlab and not args.exclude_github:
                providers.append(build_custom_provider(ProviderType.GITLAB, custom_provider))
                providers.append(build_custom_provider(ProviderType.GITHUB, custom_provider))

    model = {}
    for username in args.usernames:
        for provider in providers:
            provider_service = None
            if provider.provider is ProviderType.GITLAB:
                provider_service = GitLabService(provider.token, provider.url)
            elif provider.provider is ProviderType.GITHUB:
                provider_service = GitHubService(provider.token, provider.url)

            organizations = [username]
            names = provider_service.get_user_organization_names(username)
            organizations.extend(names)
            for organization in organizations:
                repos = provider_service.get_organization_repo_names(organization)
                for repo in repos:
                    new_repo = Repository(args.backup_name, username, provider, organization, repo,
                               provider.url + "/" + organization + "/" + repo)
                    compute_path(new_repo, FlattenLevel.ROOT.name in args.flatten_directories,
                                                 FlattenLevel.USER.name in args.flatten_directories,
                                                 FlattenLevel.PROVIDER.name in args.flatten_directories,
                                                 FlattenLevel.ORGANIZATION.name in args.flatten_directories)
                    computed_path = new_repo.path
                    if computed_path not in model:
                        model[computed_path] = new_repo
                    else:
                        if args.rename_strategy == RenameStrategy.IGNORE:
                            pass
                        elif args.rename_strategy == RenameStrategy.SHORTEST:
                            new_repo = Repository(args.backup_name, username, provider, organization, repo,
                                       provider.url + "/" + organization + "/" + repo, computed_path)
                            repo_name_level = FlattenLevel.USER
                            while computed_path in model:
                                repo_name_level = FlattenLevel(repo_name_level.value - 1)
                                compute_path(new_repo, FlattenLevel.ROOT.name in args.flatten_directories,
                                                              FlattenLevel.USER.name in args.flatten_directories,
                                                              FlattenLevel.PROVIDER.name in args.flatten_directories,
                                                              FlattenLevel.ORGANIZATION.name in args.flatten_directories,
                                                              FlattenLevel(repo_name_level.value - 1))
                            computed_path = new_repo.path
                            model[computed_path] = new_repo
                        elif args.rename_strategy == RenameStrategy.SYSTEMATIC:
                            repo1 = model.pop(computed_path)
                            compute_path(repo1, FlattenLevel.ROOT.name in args.flatten_directories,
                                                              FlattenLevel.USER.name in args.flatten_directories,
                                                              FlattenLevel.PROVIDER.name in args.flatten_directories,
                                                              FlattenLevel.ORGANIZATION.name in args.flatten_directories,
                                                              FlattenLevel.ROOT)
                            model[repo1.path] = repo1

                            new_repo = Repository(args.backup_name, username, provider, organization, repo,
                                       provider.url + "/" + organization + "/" + repo)
                            compute_path(new_repo, FlattenLevel.ROOT.name in args.flatten_directories,
                                          FlattenLevel.USER.name in args.flatten_directories,
                                          FlattenLevel.PROVIDER.name in args.flatten_directories,
                                          FlattenLevel.ORGANIZATION.name in args.flatten_directories,
                                          FlattenLevel.ROOT)
                            model[new_repo.path] = new_repo
                        elif args.rename_strategy == RenameStrategy.SHORTEST_SYSTEMATIC:
                            pass
                            # TODO

    return model


def clone_repos(model, backup_folder):
    for key, value in model.items():
        provider_service = None
        if value.provider.provider is ProviderType.GITLAB:
            provider_service = GitLabService(value.provider.token, value.provider.url)
        elif value.provider.provider is ProviderType.GITHUB:
            provider_service = GitHubService(value.provider.token, value.provider.url)
        print(value.link + "   " + backup_folder + "/" + key.__str__())
        provider_service.clone_repo(value.link, backup_folder / key)


def main():
    parser = build_argument_parser()
    args = parse_arguments(parser)
    if args.is_verbose:
        print_summary(args)
    model = build_model(args)
    clone_repos(model, args.backup_folder)


if __name__ == "__main__":
    # Generate same date string for all entities
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))

    #gh: ProviderService = GitHubService(get_github_official_token())
    #print(gh.get_user_organization_names("AleixMT"))

    main()
