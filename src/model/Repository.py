from dataclasses import dataclass, field
from pathlib import Path

from src.model.Provider import Provider


@dataclass
class Repository:
    backup: str
    owner: str
    provider: Provider
    organization: str
    name: str
    link: str
    path: Path = field(default_factory=Path)

    def __str__(self) -> str:
        return (
            f"Repository(provider='{self.provider}', organization='{self.organization}', "
            f"name='{self.name}', repo_link='{self.link}', path='{self.path}')"
        )
