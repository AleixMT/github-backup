from gitb.defines.ProviderType import ProviderType


class Provider:
    def __init__(self, provider: ProviderType, url: str, token: str) -> None:
        self.provider = provider
        self.url = url
        self.token = token
