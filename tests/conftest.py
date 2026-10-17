import pytest

from tests.helpers import RepoFactory
from tests.helpers import make_repo as _make_repo


@pytest.fixture
def make_repo() -> RepoFactory:
    return _make_repo
