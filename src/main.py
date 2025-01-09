#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

from src.defines.FlattenLevel import FlattenLevel
from src.defines.RenameStrategy import RenameStrategy
from src.model.Repository import Repository
from src.service.GitHubService import GitHubService, build_github_official_provider
from src.service.ProviderService import ProviderService, build_provider
from src.service.RepositoryService import compute_path
from src.service.TokenService import get_github_token
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
                providers.append(build_provider(custom_provider, ProviderType.GITLAB))
            if args.exclude_gitlab:
                providers.append(build_provider(custom_provider, ProviderType.GITHUB))
            if not args.exclude_gitlab and not args.exclude_github:
                providers.append(build_provider(custom_provider, ProviderType.GITLAB))
                providers.append(build_provider(custom_provider, ProviderType.GITHUB))

    model = {}
    for username in args.usernames:
        for provider in providers:
            provider_service = None
            if provider.provider == ProviderType.GITLAB:
                provider_service = GitLabService(provider.token, provider.url)
            elif provider.provider == ProviderType.GITHUB:
                provider_service = GitHubService(provider.token, provider.url)

            organizations = [username]
            organizations.extend(provider_service.get_user_organization_names(username))
            for organization in organizations:
                repos = provider_service.get_organization_repo_names(organization)
                for repo in repos:
                    new_repo = Repository(args.backup_name, username, provider, organization, repo,
                               provider.url + "/" + organization + "/" + repo)
                    computed_path = compute_path(repo, FlattenLevel.ROOT.name in args.flatten_directories,
                                                 FlattenLevel.USER.name in args.flatten_directories,
                                                 FlattenLevel.PROVIDER.name in args.flatten_directories,
                                                 FlattenLevel.ORGANIZATION.name in args.flatten_directories)
                    new_repo.path = computed_path
                    if computed_path not in model:
                        model[computed_path] = [new_repo]
                    else:
                        if args.rename_strategy == RenameStrategy.IGNORE:
                            pass
                        elif args.rename_strategy == RenameStrategy.SHORTEST:
                            new_repo = Repository(args.backup_name, username, provider, organization, repo,
                                       provider.url + "/" + organization + "/" + repo)
                            repo_name_level = FlattenLevel.USER
                            while computed_path in model:
                                repo_name_level = FlattenLevel(repo_name_level.value - 1)
                                computed_path = compute_path(new_repo, FlattenLevel.ROOT.name in args.flatten_directories,
                                                              FlattenLevel.USER.name in args.flatten_directories,
                                                              FlattenLevel.PROVIDER.name in args.flatten_directories,
                                                              FlattenLevel.ORGANIZATION.name in args.flatten_directories,
                                                              FlattenLevel(repo_name_level.value - 1))
                            new_repo.path = computed_path
                            model[computed_path] = [new_repo]
                        elif args.rename_strategy == RenameStrategy.SYSTEMATIC:
                            repo1 = model.pop(computed_path)
                            repo1.path = compute_path(repo1, FlattenLevel.ROOT.name in args.flatten_directories,
                                                              FlattenLevel.USER.name in args.flatten_directories,
                                                              FlattenLevel.PROVIDER.name in args.flatten_directories,
                                                              FlattenLevel.ORGANIZATION.name in args.flatten_directories,
                                                              FlattenLevel.ROOT)
                            model[repo1.path] = [repo1]

                            new_repo = Repository(args.backup_name, username, provider, organization, repo,
                                       provider.url + "/" + organization + "/" + repo)
                            new_repo.path = computed_path(repo, FlattenLevel.ROOT.name in args.flatten_directories,
                                          FlattenLevel.USER.name in args.flatten_directories,
                                          FlattenLevel.PROVIDER.name in args.flatten_directories,
                                          FlattenLevel.ORGANIZATION.name in args.flatten_directories,
                                          FlattenLevel.ROOT)
                            model[new_repo.path] = new_repo
                        elif args.rename_strategy == RenameStrategy.SHORTEST_SYSTEMATIC:
                            pass
                            # TODO

    print(model)

def main():
    parser = build_argument_parser()
    args = parse_arguments(parser)
    if args.is_verbose:
        print_summary(args)
    model = build_model(args)


if __name__ == "__main__":
    # Generate same date string for all entities

    gh: ProviderService = GitHubService(get_github_token())
    print(gh.get_user_collaboration_repo_names("AleixMT"))

    main()
