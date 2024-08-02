from src.domain.entities.repository import Repository

non_blocking_error_codes = [403]


def get_header(repository: Repository):
    return {
        "Authorization": f"Bearer {repository.token}",
    }


def get_email(login):
    return f"{login}@github.com"


def get_base_url(repository: Repository) -> str:
    return f"https://api.github.com/repos/{repository.project or repository.organisation}/{repository.name}"
