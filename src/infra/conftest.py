import pytest
from aioresponses import aioresponses


@pytest.fixture
def mocker_aio():
    with aioresponses() as mocker:
        yield mocker
