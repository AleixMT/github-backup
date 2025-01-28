#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re


from src.defines.ProviderType import ProviderType
from src.service.IOService import read_file, read_env_var


def get_github_official_token():
    return get_token("GH_TOKEN")


def get_gitlab_official_token():
    return get_token("GL_TOKEN")


# For GitHub enterprise in example.com its token deduced name would be EXAMPLE_COM_GITHUB
def deduce_name(provider: ProviderType, hostname: str):
    return infer_name(hostname).replace('.', '_').capitalize() + "_" + provider.name


# Based on the provided custom provider, get the corresponding token from file or env vars with the deduced name
def get_custom_provider_token(provider: ProviderType, hostname: str):
    return get_token(deduce_name(provider, hostname))


def get_token(token_name):
    """Retrieve a token from predefined sources in order of priority."""
    sources = [
        lambda: read_file(f"/run/secrets/{token_name}"),
        lambda: read_file(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
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
