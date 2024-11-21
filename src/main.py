#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse


"""
-r|--remove|--remove-folder --> Removes the backup folder after the backup
-s|--scratch|--from-scratch --> Empties the backupb folder previous to start the backup
-c|--compress --> Produces a compressed file with the backup folders
-p|--compressed-path  --> custom folder where the compressed file will be stored. Needs value., Implies -c
-h|--hierarchy|--hierarchy-backup  --> Clone repos keeping organization and user hierarchy in backup folder
-j|--json|--generate-json  --> generates a json of the of the backup up folders and repos
-J|--json-path --> custom folder where the json report will be stored
-b|--backup|--backup-path  --> custom folder where all the clones will be done. Needs value
-l|--gitlab -> Custom user that will be backed from gitlab. needs one or more value
-f|--force --> Does not ask confirmation for destructive actions 
"""


def main():
    parser = argparse.ArgumentParser(description="Backup your git repos in your local filesystem")

    # Optional arguments
    parser.add_argument("-r", "--remove", "--remove-folder",
                        action="store_true",
                        help="Removes the backup folder after the backup.",
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
    parser.add_argument("-p", "--compressed-path",
                        type=str,
                        metavar="PATH",
                        help="Custom path where the compressed file will be stored. Implies -c.",
                        default="backup/backup.tar.gz",
                        dest="compressed_path")
    parser.add_argument("-h", "--hierarchy", "--hierarchy-backup", "--keep-hierarchy",
                        action="store_true",
                        help="Clone repos keeping organizations and user hierarchy in the backup folder.",
                        default=False,
                        dest="reflect_hierarchy")
    parser.add_argument("-j", "--json", "--generate-json", "--produce-json",
                        action="store_true",
                        help="Generates a JSON report of the backup folders and repos.",
                        default=False,
                        dest="produce_json")
    parser.add_argument("-J", "--json-path",
                        type=str,
                        metavar="PATH",
                        help="Custom path where the JSON report will be stored. Implies -j.",
                        default="backup/backup.json",
                        dest="json_path")
    parser.add_argument("-b", "--backup", "--backup-path",
                        type=str,
                        metavar="PATH",
                        help="Custom folder where all the clones will be done. Requires a value.",
                        default="backup",
                        dest="backup_path")
    parser.add_argument("-l", "--gitlab",
                        type=str,
                        metavar="GITLAB_USERS",
                        nargs="+",
                        help="One or more GitLab usernames to back up. Separate multiple usernames with spaces.",
                        dest="gitlab_users")
    parser.add_argument("-f", "--force",
                        action="store_true",
                        help="Does not ask confirmation for destructive actions.",
                        default=False,
                        dest="is_forced")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Enable verbose output during backup.",
                        default=False,
                        dest="is_verbose")
    parser.add_argument("github_users",
                        type=str,
                        metavar="GITHUB_USERS",
                        nargs="*",  # Zero or more GitHub usernames
                        help="One or more GitHub usernames to back up. Separate multiple usernames with spaces. "
                             "Positional argument",
                        dest="github_users")

    args = parser.parse_args()

    # Check if at least one of the user lists is provided (GitHub or GitLab)
    if not args.github and not args.gitlab:
        parser.error("You must provide at least one GitHub or GitLab user.")

    # Compressed path implies -c
    if args.compressed_path:
        args.produce_compressed = True

    # JSON path implies -j
    if args.json_path:
        args.produce_json = True

    print(args)

    print("Backup summary:")

    if args.github_users:
        print("Backing up the following GitHub users:")
        for user in args.github_users:
            print(f"  - {user}")

    if args.gitlab:
        print("Backing up the following GitLab users:")
        for user in args.gitlab:
            print(f"  - {user}")

    if args.backup_path:
        print("Backup folder: " + args.backup_path)

    if args.produce_compressed:
        print("Compressed backup path: " + args.compressed_path)

    if args.produce_json:
        print("JSON summary path: " + args.json_path)

    if args.empty_backup_folder_first:
        print("Empty backup folder before performing backup (start from scratch): " + args.empty_backup_folder_first)

    if args.remove_backup_folder_afterwards:
        print("Remove backup folder after performing backup: " + args.remove_backup_folder_afterwards)

    if args.reflect_hierarchy:
        print("Produces a hierarchical structure for the backup: " + args.remove_backup_folder_afterwards)

    if args.verbose:
        print("Verbose: " + args.verbose)

    if args.force:
        print("Force: " + args.force)


if __name__ == "__main__":
    main()
