import base64

from src.domain.entities.repository import Repository


def get_header(repository: Repository):
    token_bytes = f"{repository.token}:".encode("ascii")
    base64_token = base64.b64encode(token_bytes).decode("ascii")

    return {
        "Content-Type": "application/json; charset=utf-8; api-version=7.1",
        "Authorization": f"Basic {base64_token}",
    }


def get_base_url(repository: Repository) -> str:
    return f"https://dev.azure.com/{repository.organisation}/{repository.project}/_apis/git/repositories/{repository.name}"
