from pathlib import Path

from src.model.Provider import Provider


class Repository:
    def __init__(self, backup: str, owner: str, provider: Provider, organization: str, name: str, link: str,
                 path: Path = Path()):
        self.backup = backup
        self.owner = owner
        self.provider = provider
        self.organization = organization
        self.name = name
        self.link = link
        self.path = path

    def __str__(self):
        return (f"Repository(provider='{self.provider}', organization='{self.organization}', "
                f"name='{self.name}', repo_link='{self.link}', path='{self.path}')")




