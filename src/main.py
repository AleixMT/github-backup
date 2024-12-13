#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from io import StringIO

from GitHubService import GitHubService, build_github_official_provider
from ProviderService import ProviderService, build_provider
from TokenService import get_github_token
from defines import FlattenLevel, CollisionStrategy, ProviderType
from FileService import is_file_directory_writable
from GitLabService import build_gitlab_official_provider
from ArgumentParserService import build_argument_parser, parse_arguments
from UnparserService import print_summary


def build_model(args):

    model = {args.backup_name: {}}

    for username in args.usernames:
        model[args.backup_name][username] = {}
        if not args.exclude_enterprise:
            if args.exclude_github:
                model[args.backup_name][username]["GitLab"] = build_gitlab_official_provider()
            if args.exclude_gitlab:
                model[args.backup_name][username]["GitHub"] = build_github_official_provider()
            if not args.exclude_gitlab and not args.exclude_github:
                model[args.backup_name][username]["GitLab"] = build_gitlab_official_provider()
                model[args.backup_name][username]["GitHub"] = build_github_official_provider()
        if args.custom_providers:
            for custom_provider in args.custom_providers:
                if args.exclude_github:
                    model[args.backup_name][username][custom_provider] = build_provider(custom_provider, ProviderType.GITLAB)
                if args.exclude_gitlab:
                    model[args.backup_name][username][custom_provider] = build_provider(custom_provider, ProviderType.GITHUB)
                if not args.exclude_gitlab and not args.exclude_github:
                    model[args.backup_name][username][custom_provider] = build_provider(custom_provider, ProviderType.GITLAB)
                    model[args.backup_name][username][custom_provider] = build_provider(custom_provider, ProviderType.GITHUB)



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
