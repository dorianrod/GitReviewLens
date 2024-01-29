from .get_developers import blueprint_get_developers
from .get_features import blueprint_get_features
from .get_pull_requests import blueprint_get_pull_requests
from .health import blueprint_health
from .load_git_features import blueprint_load_git_features
from .load_pull_requests import blueprint_load_pull_requests
from .test import blueprint_test

routes = [
    blueprint_test,
    blueprint_health,
    blueprint_get_developers,
    blueprint_load_pull_requests,
    blueprint_get_pull_requests,
    blueprint_load_git_features,
    blueprint_get_features,
]

__all__ = ["routes"]
