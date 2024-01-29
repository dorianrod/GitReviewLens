import os
import shutil


def has_extension(path):
    filename = os.path.basename(path)
    base, extension = os.path.splitext(filename)
    return bool(extension)


def create_path_if_needed(path: str):
    if has_extension(path):
        path = os.path.dirname(path)
    os.makedirs(path, exist_ok=True)


def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def get_file_content(path):
    with open(path, 'r') as file:
        return file.read()
