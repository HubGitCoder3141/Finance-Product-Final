import pytest
from coach_app.curriculum import load
from coach_app.storage import Repository


@pytest.fixture
def curriculum():
    return load()


@pytest.fixture
def repo(tmp_path):
    repository = Repository(tmp_path / "test.sqlite3")
    repository.create_session("learner-a")
    repository.create_session("learner-b")
    return repository
