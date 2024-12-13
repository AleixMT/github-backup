#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def read_file(file_path):
    """
    Reads the GH_TOKEN file and returns its content.
    Handles edge cases such as the file being empty, not existing, or being unreadable.

    Args:
        file_path (str): Path to the token file.

    Returns:
        str: The content of the token file if valid.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read due to permission issues.
        ValueError: If the file is empty or contains only whitespace.
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        # Check if the file is readable
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"The file '{file_path}' cannot be read. Check permissions.")

        # Read the file
        with open(file_path, "r") as file:
            content = file.read().strip()

        # Check if the file is empty or contains only whitespace
        if not content:
            raise ValueError(f"The file '{file_path}' is empty or contains only whitespace.")

        return content

    except FileNotFoundError as e:
        raise
    except PermissionError as e:
        raise
    except ValueError as e:
        raise
    except Exception as e:
        raise


def read_env_var(var_name):
    """
    Reads an environment variable and validates its content.

    Args:
        var_name (str): Name of the environment variable.

    Returns:
        str: The value of the environment variable if valid.

    Raises:
        KeyError: If the environment variable does not exist.
        ValueError: If the environment variable is empty or contains only whitespace.
    """
    try:
        # Check if the environment variable exists
        if var_name not in os.environ:
            raise KeyError(f"The environment variable '{var_name}' does not exist.")

        # Read the value
        value = os.environ[var_name].strip()

        # Check if the value is empty or contains only whitespace
        if not value:
            raise ValueError(f"The environment variable '{var_name}' is empty or contains only whitespace.")

        return value

    except KeyError as e:
        print(f"Error: {e}")
        raise
    except ValueError as e:
        print(f"Error: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


def get_github_token():
    return get_token("GH_TOKEN")


def get_token(token_name):
    """Retrieve a token from predefined sources in order of priority."""
    sources = [
        lambda: read_file(f"/run/secrets/{token_name}"),
        lambda: read_file(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "secrets",
                token_name
            ).__str__()
        ),
        lambda: read_env_var(token_name),
    ]

    for source in sources:
        try:
            return source()
        except Exception as e:
            continue

    print(f"Could not read {token_name} from any source")
    sys.exit(1)
