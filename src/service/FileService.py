#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


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
