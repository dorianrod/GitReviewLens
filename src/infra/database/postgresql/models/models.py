from src.common.settings import settings
from src.infra.database.postgresql.models.factory import build_models

models = build_models(settings.db_schema)

BaseModel = models["BaseModel"]
Base = models["Base"]
Developer = models["Developer"]
Feature = models["Feature"]
Comment = models["Comment"]
PullRequest = models["PullRequest"]
pull_request_approvers = models["pull_request_approvers"]
