from src.defines.ProviderType import ProviderType


class Provider:
    def __init__(self, provider: ProviderType, url: str, token: str):
        self.provider = provider
        self.url = url
        self.token = token
