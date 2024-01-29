import re
from dataclasses import dataclass

from pydriller import Git, Repository  # type: ignore

from src.common.monitoring.logger import LoggerInterface
from src.common.utils.date import parse_date
from src.domain.entities.feature import Feature
from src.domain.repositories.features import FeaturesRepository


@dataclass
class FeaturesGit(FeaturesRepository):
    logger: LoggerInterface
    path: str

    def get_by_id(self, id, options=None):
        options = options or {}

        self.logger.info("Getting git commit...")

        gr = Git(path=self.path)

        git_repository = options.get("git_repository", None)
        commit = gr.get_commit(id)

        deletions = 0
        insertions = 0

        exclude_files = options.get("exclude_files")

        modified_files = []
        for line in commit.modified_files:
            if not exclude_files or not re.match(exclude_files, line.filename):
                deletions += line.deleted_lines
                insertions += line.added_lines
                modified_files.append(line.old_path or line.new_path)

        feature = Feature.from_dict(
            {
                "git_repository": git_repository,
                "count_deleted_lines": deletions,
                "count_inserted_lines": insertions,
                "dmm_unit_complexity": commit.dmm_unit_complexity,
                "dmm_unit_interfacing": commit.dmm_unit_interfacing,
                "dmm_unit_size": commit.dmm_unit_size,
                "date": parse_date(commit.committer_date).isoformat(),
                "commit": commit.hash,
                "developer": {
                    "full_name": commit.author.name,
                    "email": commit.author.email,
                },
                "modified_files": modified_files,
            }
        )

        return feature

    def find_all(self, options=None):
        options = options or {}

        features: list[Feature] = []

        branch = options.get("branch", None)
        from_date = parse_date(options.get("from_date", None))
        if from_date:
            from_date = from_date.isoformat()
        to_date = parse_date(options.get("to_date", None))
        if to_date:
            to_date = to_date.isoformat()

        self.logger.info(f"Finding all commit in git from {from_date} to {to_date}...")

        for commit in Repository(
            path_to_repo=self.path, only_in_branch=branch
        ).traverse_commits():
            commit_date = parse_date(commit.committer_date).isoformat()

            if from_date and commit_date < from_date:
                continue
            if to_date and commit_date > to_date:
                continue
            features.append(self.get_by_id(commit.hash, options))

        return features
