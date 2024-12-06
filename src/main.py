#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import argparse
import os
from github import Github
from github import Auth

# Generate same date string for all entities
datetime_string = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # ISO 8601-like format


def is_file_directory_writable(file_path):
    if os.access(os.path.dirname(file_path), os.W_OK):
        return True
    else:
        return False


def is_file_writable(file_path):
    try:
        # Try opening file in write mode
        open(file_path, 'w')
        return True
    except (OSError, PermissionError):
        return False


def parse_arguments():
    parser = argparse.ArgumentParser(description="Backup your git repos in your local filesystem")

    # Optional arguments
    parser.add_argument("-p", "--provider", "--providers",
                        type=str,
                        nargs="+",  # Allow one or more values
                        help="Adds custom GitLab providers",
                        dest="custom_providers")
    parser.add_argument("-f", "--force",
                        action="store_true",
                        help="Does not ask confirmation for destructive actions.",
                        default=False,
                        dest="is_forced")
    parser.add_argument("-r", "--remove", "--remove-folder",
                        action="store_true",
                        help="Removes the backup content after the backup.",
                        default=False,
                        dest="remove_backup_folder_afterwards")
    parser.add_argument("-s", "--scratch", "--from-scratch",
                        action="store_true",
                        help="Empties the backup folder before starting the backup.",
                        default=False,
                        dest="empty_backup_folder_first")
    parser.add_argument("-c", "--compress",
                        action="store_true",
                        help="Produces a compressed file with the backup folders.",
                        default=False,
                        dest="produce_compressed")
    parser.add_argument("-C", "--compressed-path",
                        type=str,
                        metavar="PATH",
                        help="Custom path where the compressed file will be stored. Implies -c.",
                        dest="compressed_path")
    parser.add_argument("-y", "--hierarchy", "--hierarchy-backup", "--keep-hierarchy",
                        action="store_true",
                        help="Clone repos keeping organizations and user hierarchy in the backup folder.",
                        default=False,
                        dest="reflect_hierarchy")
    parser.add_argument("-F", "--flatten", "--Flatten",
                        type=str,
                        choices=["user", "provider", "organization"],
                        nargs="+",  # Allow one or more values
                        help="Directory levels that will be flatten in the backup folder. Implies -y except when "
                             "flattening all directory level",
                        dest="flatten_directories")
    parser.add_argument("-l", "--handle-collision", "--handle-collision-strategy",
                        choices=["rename", "ignore", "remove"],
                        help="Strategy to follow to handle collisions (a repo that because of its name has to be cloned"
                             " in the same folder path as another one):"
                             "rename: Use a systematic name (the shortest possible) for the new repo that produces the"
                             " collision"
                             "ignore: Ignores repos that have filename collisions."
                             "remove: Removes the repo already cloned and clones the new one with the same name.",
                        dest="collision_strategy")
    parser.add_argument("-j", "--json", "--generate-json", "--produce-json",
                        action="store_true",
                        help="Generates a JSON report of the backup folders and repos.",
                        default=False,
                        dest="produce_json")
    parser.add_argument("-J", "--json-path",
                        type=str,
                        metavar="PATH",
                        help="Custom path where the JSON report will be stored. Implies -j.",
                        dest="json_path")
    parser.add_argument("-b", "--backup", "--backup-directory", "--backup-folder",
                        type=str,
                        metavar="PATH",
                        help="Custom folder where all the clones will be done. Requires a value.",
                        dest="backup_folder")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Enable verbose output during backup.",
                        default=False,
                        dest="is_verbose")
    parser.add_argument("--exclude-github",
                        action="store_true",
                        help="Exclude GitHub repositories from the backup.")
    parser.add_argument("--exclude-gitlab",
                        action="store_true",
                        help="Exclude GitLab repositories from the backup.")
    parser.add_argument("--exclude-enterprise",
                        action="store_true",
                        help="Exclude \"official\" providers (github.com and gitlab.com).")
    # Positional argument for usernames of the profiles to scrap
    parser.add_argument("usernames",
                        nargs="+",
                        metavar="USERNAME1 USERNAME2 USERNAME3 ...",
                        help="List of usernames to back up.")

    args = parser.parse_args()

    # Supply default backup directory
    if not args.backup_folder:
        args.backup_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup")

    # Check existence and access of backup directory
    if not os.path.exists(args.backup_folder):
        try:
            os.makedirs(args.backup_folder)
        except OSError as e:
            parser.error(f"The folder for the backup {args.backup_folder} does not exist and cannot be created.")
    else:
        if not os.access(args.backup_folder, os.W_OK):
            parser.error(f"The folder for the backup {args.backup_folder} cannot be written or there is some problem "
                         f"with it: ")

    # Flattening all directory levels makes hierarchy disappears, so it makes no sense to select both configurations
    if args.flatten_directories \
            and "rename" in args.flatten_directories \
            and "ignore" in args.flatten_directories \
            and "remove" in args.flatten_directories \
            and args.reflect_hierarchy:
        parser.error("You cannot use -y when flattening all directory levels with -F because it makes no sense.")

    # When keeping the complete hierarchy we ensure that there will be no collisions
    if not args.flatten_directories \
            and args.reflect_hierarchy \
            and args.collision_strategy:
        parser.error("You do not need to supply a collision strategy with -l when keeping the hierarchy with -y and not"
                     " flattening any directory (not supplying -F)")

    # Supply default collision strategy if needed
    if args.reflect_hierarchy \
            and args.flatten_directories \
            and not args.collision_strategy:
        args.collision_strategy = "rename"

    if not args.collision_strategy:
        args.collision_strategy = "rename"

    # If path supplied -c implicit
    if not args.produce_compressed and args.compressed_path:
        args.produce_compressed = True

    # If -c but no path provided set to default value
    if args.produce_compressed and not args.compressed_path:
        args.compressed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup" + datetime_string +
                                            ".tar.gz")

    # Check access to json file
    if args.compressed_path and not is_file_directory_writable(args.compressed_path):
        parser.error("File " + args.compressed_path + " is not writable because its directory cannot be accessed.")

    # Check write access to json file
    if args.compressed_path and not is_file_writable(args.compressed_path):
        parser.error("File " + args.compressed_path + " is not writable.")

    # If path supplied -j implicit
    if not args.produce_json and args.json_path:
        args.produce_json = True

    # If -j but no path provided set to default value
    if args.produce_json and not args.json_path:
        args.json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup" + datetime_string + ".json")

    # Check access to json file
    if args.json_path and not is_file_directory_writable(args.json_path):
        parser.error("File " + args.json_path + " is not writable because its directory cannot be accessed.")

    # Check write access to json file
    if args.json_path and not is_file_writable(args.json_path):
        parser.error("File " + args.json_path + " is not writable.")

    # Check if at least one source is included
    if args.exclude_github and args.exclude_gitlab:
        parser.error("You cannot exclude both GitHub and GitLab. At least one provider must be included.")

    if args.custom_providers:
        custom_providers = []
        for custom_provider in args.custom_providers:
            if args.exclude_github:
                custom_providers.append({'url': custom_provider, 'provider': "GitLab"})
            if args.exclude_gitlab:
                custom_providers.append({'url': custom_provider, 'provider': "GitHub"})
    return args


def print_summary(args):
    print("BACKUP SUMMARY:")
    print("Backing up the following users:")
    for user in args.usernames:
        print(f"  - {user}")

    print("Using the following providers:")
    if args.custom_providers:
        for provider in args.custom_providers:
            print(f"  - {provider['provider']} ({provider['url']})")
    if args.exclude_gitlab:
        print("  - GitHub (github.com)")
    if args.exclude_github:
        print("  - GitLab (gitlab.com)")

    if args.backup_folder:
        print("* Backup folder:                                                     " + args.backup_folder)

    if args.produce_compressed:
        print("* Compressed backup path:                                            " + args.compressed_path)

    if args.produce_json:
        print("* JSON summary path:                                                 " + args.json_path)

    print("* Empty backup folder before performing backup (start from scratch): ", end="")
    if args.empty_backup_folder_first:
        print("Yes")
    else:
        print("No")

    print("* Remove backup folder after performing backup: ", end="")
    if args.remove_backup_folder_afterwards:
        print("                     Yes")
    else:
        print("                     No")

    print("* Produces a hierarchical structure for the backup: ", end="")
    if args.reflect_hierarchy:
        print("                 Yes")
    else:
        print("                 No")

    if args.flatten_directories:
        print("* Directory levels to flatten:                                       " +
              ", ".join(args.flatten_directories))

    if args.collision_strategy:
        print("* Strategy to avoid collision in the folder names of the repos:      " + args.collision_strategy)

    print("* Verbose output: ", end="")
    if args.is_verbose:
        print("                                                   Yes")
    else:
        print("                                                   No")

    print("* Do not ask for confirmation on destructive actions: ", end="")
    if args.is_forced:
        print("               Yes")
    else:
        print("               No")


def build_model(args):

    model = {datetime_string: {}}

    # TODO: use two auxiliar functions to create the dictionaries DRY code
    for username in args.usernames:
        model[datetime_string][username] = {}
        if not args.exclude_enterprise:
            if args.exclude_github:
                model[datetime_string][username]["GitLab"] = {'url': 'https://gitlab.com/', 'type': 'GitLab',
                                                              'orgs': {}}
            if args.exclude_gitlab:
                model[datetime_string][username]["GitHub"] = {'url': 'https://github.com/', 'type': 'GitHub',
                                                              'orgs': {}}
            if not args.exclude_gitlab and not args.exclude_github:
                model[datetime_string][username]["GitLab"] = {'url': 'https://gitlab.com/', 'type': 'GitLab',
                                                              'orgs': {}}
                model[datetime_string][username]["GitHub"] = {'url': 'https://github.com/', 'type': 'GitHub',
                                                              'orgs': {}}
        if args.custom_providers:
            for custom_provider in args.custom_providers:
                if args.exclude_github:
                    model[datetime_string][username][custom_provider] = {'url': custom_provider, 'type': 'GitLab',
                                                              'orgs': {}}
                if args.exclude_gitlab:
                    model[datetime_string][username][custom_provider] = {'url': custom_provider, 'type': 'GitHub',
                                                              'orgs': {}}
                if not args.exclude_gitlab and not args.exclude_github:
                    model[datetime_string][username][custom_provider] = {'url': custom_provider, 'type': 'GitLab',
                                                                         'orgs': {}}
                    model[datetime_string][username][custom_provider] = {'url': custom_provider, 'type': 'GitHub',
                                                                         'orgs': {}}



def get_organizations(hostname):
    # using an access token
    auth = Auth.Token("".join(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secrets", "GH_TOKEN.txt")).readlines()))

    # Github Enterprise with custom hostname
    #g = Github(base_url="https://" + hostname + "/api/v3", auth=auth)
    g = Github(auth=auth)
    USER = "AleixMT"
    user = g.get_user(USER)

    user_repos = user.get_repos()
    owned_repos = [repo for repo in user_repos if repo.owner.login == USER]
    for repo in owned_repos:
        print(repo.name)
    #for orgs in g.get_user().get_repos():
        #print(orgs)

    '''
    for orgs in g.get_user().get_orgs():
        print()
        print(orgs.login)
        for repo in orgs.get_repos():
            print(repo.name)
    '''
    # To close connections after use
    g.close()

def main():
    args = parse_arguments()
    if args.is_verbose:
        print_summary(args)
    model = build_model(args)

    get_organizations("github.com")


if __name__ == "__main__":
    main()
