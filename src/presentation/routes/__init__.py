from .get_developers import router as developpers_router
from .get_features import router as features_router
from .get_pull_requests import router as pull_requests_router
from .health import router as health_router
from .load_git_features import router as load_git_features
from .load_pull_requests import router as load_pull_requests_router

routes = [
    health_router,
    developpers_router,
    features_router,
    pull_requests_router,
    load_pull_requests_router,
    load_git_features,
]

__all__ = ["routes"]
