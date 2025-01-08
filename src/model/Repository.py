from pathlib import Path

from src.defines.defines import ProviderType


class Repository:
    def __init__(self, backup: str, owner: str, provider: ProviderType, organization: str, name: str, link: str):
        self.backup = backup
        self.owner = owner
        self.provider = provider
        self.organization = organization
        self.name = name
        self.link = link
        self.path = Path()

    def __str__(self):
        return (f"Repository(provider='{self.provider}', organization='{self.organization}', "
                f"name='{self.name}', repo_link='{self.link}', path='{self.path}')")

    '''
    /backup/owner/provider/organization/repo
    '''
    def compute_path(self, ignore_backup: bool = False, ignore_owner: bool = False, ignore_provider: bool = False,
                     ignore_organization: bool = False):
        self.path = Path()
        if not ignore_backup:
            self.path = self.path / self.backup
        if not ignore_owner:
            self.path = self.path / self.owner
        if not ignore_provider:
            self.path = self.path / self.provider.name
        if not ignore_organization:
            self.path = self.path / self.organization
        self.path = self.path / self.name


