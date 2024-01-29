import os

import pytest

from src.common.utils.env import replace_env_var
from src.common.utils.file import (
    create_path_if_needed,
    delete_directory,
    get_file_content,
)

current_file_path = os.path.abspath(__file__)
directory_of_file = os.path.dirname(current_file_path)
path = os.path.join(directory_of_file, "temp")
env_file = os.path.realpath(os.path.join(directory_of_file, ".env.source"))
expected_env_file = os.path.realpath(os.path.join(directory_of_file, ".env.expected"))
target_file = os.path.join(path, ".env")


@pytest.fixture(scope="function", autouse=True)
def clean_temp_files():
    delete_directory(path)
    create_path_if_needed(path)


def test_replace_env_var():
    replace_env_var(env_file, target_file, "GIT_BRANCHES", "[{'test':'toto'}]")
    assert get_file_content(target_file) == get_file_content(expected_env_file)
