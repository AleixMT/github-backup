#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime

from FileService import is_file_directory_writable, is_file_writable
from defines import FlattenLevel, CollisionStrategy
import argparse


def build_argument_parser():
    parser = argparse.ArgumentParser(description="Backup your git repos in your local filesystem")

    # Optional arguments
    parser.add_argument("-p", "--provider", "--providers",
                        help="Adds custom GitLab providers",
                        type=str,
                        nargs="+",
                        dest="custom_providers")
    parser.add_argument("-f", "--force",
                        help="Does not ask confirmation for destructive actions.",
                        # type=bool,
                        # nargs=0,
                        dest="is_forced",
                        action="store_true",
                        default=False)
    parser.add_argument("-r", "--remove", "--remove-folder",
                        help="Removes the backup content after the backup.",
                        # type=bool,
                        # nargs=0,
                        dest="remove_backup_folder_afterwards",
                        action="store_true",
                        default=False)
    parser.add_argument("-s", "--scratch", "--from-scratch",
                        help="Empties the backup folder before starting the backup.",
                        # type=bool,
                        # nargs=0,
                        dest="empty_backup_folder_first",
                        action="store_true",
                        default=False)
    parser.add_argument("-c", "--compress",
                        help="Produces a compressed file with the backup folders.",
                        # type=bool,
                        # nargs=0,
                        dest="produce_compressed",
                        action="store_true",
                        default=False)
    parser.add_argument("-C", "--compressed-path",
                        help="Custom path where the compressed file will be stored. Implies -c.",
                        type=str,
                        nargs='?',
                        dest="compressed_path",
                        metavar="FILE_PATH")
    parser.add_argument("-y", "--hierarchy", "--hierarchy-backup", "--keep-hierarchy",
                        help="Clone repos keeping organizations and user hierarchy in the backup folder.",
                        # type=bool,
                        # nargs=0,
                        dest="reflect_hierarchy",
                        action="store_true",
                        default=False)
    parser.add_argument("-F", "--flatten", "--Flatten",
                        help="Hierarchy levels of the backup that will not be present in the hierarchical structure"
                             " of the folder "
                             "structure of the backup. Implies -y except when "
                             "flattening all directory level:" +
                             FlattenLevel.ROOT.name + ": Flattens root folder in the backup." +
                             FlattenLevel.USER.name + ": Flattens user folders in the backup" +
                             FlattenLevel.PROVIDER.name + ": Flattens provider folder in the backup." +
                             FlattenLevel.ORGANIZATION.name + ": Flattens organization folder in the backup.",
                        type=str,
                        nargs="+",
                        dest="flatten_directories",
                        choices=[name for name in FlattenLevel])
    parser.add_argument("-l", "--handle-collision", "--handle-collision-strategy",
                        help="Strategy to follow to handle collisions (a repo that because of its name has to be cloned"
                             " in the same folder path as another one):" +
                             CollisionStrategy.RENAME.name + ": Use a systematic name (the shortest possible) for the "
                                                             "new repo that produces the collision" +
                             CollisionStrategy.SYSTEMATIC.name + ": Use a systematic name for all repos" +
                             CollisionStrategy.IGNORE.name + ": Ignores repos that have filename collisions." +
                             CollisionStrategy.REMOVE.name + ": Removes the repo already cloned and clones the new one "
                                                             "with the same name.",
                        type=str,
                        nargs='?',
                        dest="collision_strategy",
                        choices=[name for name in CollisionStrategy])
    parser.add_argument("-j", "--json", "--generate-json", "--produce-json",
                        help="Generates a JSON report of the backup folders and repos.",
                        # type=bool,
                        # nargs=0,
                        dest="produce_json",
                        action="store_true",
                        default=False)
    parser.add_argument("-J", "--json-path",
                        help="Custom path where the JSON report will be stored. Implies -j. Requires a value.",
                        type=str,
                        nargs='?',
                        dest="json_path",
                        metavar="FILE_PATH")
    parser.add_argument("-b", "--backup-directory", "--backup-folder",
                        help="Custom folder where the backups will be stored.",
                        type=str,
                        nargs='?',
                        dest="backup_folder",
                        metavar="DIRECTORY_PATH")
    parser.add_argument("-n", "--backup-name",
                        help="Custom name for the root backup folder.",
                        type=str,
                        nargs='?',
                        dest="backup_name",
                        metavar="DIRECTORY_NAME")
    parser.add_argument("-v", "--verbose",
                        help="Enable verbose output during backup.",
                        # type=bool,
                        # nargs=0,
                        dest="is_verbose",
                        action="store_true",
                        default=False)
    parser.add_argument("--exclude-github",
                        help="Exclude GitHub repositories from the backup.",
                        # type=bool,
                        # nargs=0,
                        dest="exclude_github",
                        action="store_true"),
    parser.add_argument("--exclude-gitlab",
                        help="Exclude GitLab repositories from the backup.",
                        # type=bool,
                        # nargs=0,
                        dest="exclude_gitlab",
                        action="store_true")
    parser.add_argument("--exclude-enterprise",
                        help="Exclude \"official\" providers (github.com and gitlab.com).",
                        # type=bool,
                        # nargs=0,
                        dest="exclude_enterprise",
                        action="store_true")
    # Positional argument for usernames of the profiles to scrap
    parser.add_argument("usernames",
                        help="List of usernames to back up.",
                        # type=List[str],
                        nargs="+",
                        # dest="usernames",
                        metavar="USERNAME1 USERNAME2 USERNAME3 ...")
    return parser


def parse_arguments(parser: argparse.ArgumentParser):
    args = parser.parse_args()

    if not args.backup_name:
        args.backup_name = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # ISO 8601-like format

    # Supply default backup directory
    if not args.backup_folder:
        args.backup_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backup")

    # Check existence and access of backup directory
    if not os.path.exists(args.backup_folder):
        try:
            os.makedirs(args.backup_folder)
        except OSError as e:
            parser.error(f"The folder for the backup {args.backup_folder} does not exist and cannot be created. Error: "
                         + e.__str__())
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
        args.compressed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup" + args.backup_name +
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
        args.json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup" + args.backup_name + ".json")

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
