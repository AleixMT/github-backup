#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from io import StringIO


def print_summary(args):
    summary = StringIO()
    summary.write("BACKUP SUMMARY:\n")
    summary.write("Backing up the following users:\n")
    for user in args.usernames:
        summary.write(f"  - {user}\n")

    summary.write("Using the following providers:\n")
    if args.custom_providers:
        for provider in args.custom_providers:
            summary.write(f"  - {provider['provider']} ({provider['url']})\n")
    if args.exclude_gitlab:
        summary.write("  - GitHub (github.com)\n")
    if args.exclude_github:
        summary.write("  - GitLab (gitlab.com)\n")

    if args.backup_folder:
        summary.write(f"* Backup folder:                                                     {args.backup_folder}\n")

    if args.produce_compressed:
        summary.write(f"* Compressed backup path:                                            {args.compressed_path}\n")

    if args.produce_json:
        summary.write(f"* JSON summary path:                                                 {args.json_path}\n")

    summary.write("* Empty backup folder before performing backup (start from scratch): ")
    summary.write("Yes\n" if args.empty_backup_folder_first else "No\n")

    summary.write("* Remove backup folder after performing backup:                     ")
    summary.write("Yes\n" if args.remove_backup_folder_afterwards else "No\n")

    summary.write("* Produces a hierarchical structure for the backup:                 ")
    summary.write("Yes\n" if args.reflect_hierarchy else "No\n")

    if args.flatten_directories:
        summary.write("* Directory levels to flatten:                                       " +
                      ", ".join(args.flatten_directories) + "\n")

    if args.collision_strategy:
        summary.write(f"* Strategy to avoid collision in the folder names of the repos:      {args.collision_strategy}\n")

    summary.write("* Verbose output:                                                   ")
    summary.write("Yes\n" if args.is_verbose else "No\n")

    summary.write("* Do not ask for confirmation on destructive actions:               ")
    summary.write("Yes\n" if args.is_forced else "No\n")

    return summary.getvalue()
