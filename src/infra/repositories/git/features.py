import re
from dataclasses import dataclass

from pydriller import Git, Repository  # type: ignore

from src.common.monitoring.logger import LoggerInterface
from src.common.utils.date import format_to_utc, parse_date
from src.domain.entities.feature import Feature
from src.domain.repositories.features import FeaturesRepository


@dataclass
class FeaturesGit(FeaturesRepository):
    logger: LoggerInterface
    path: str

    async def get_by_id(self, id, options=None):
        options = options or {}
        self.logger.info("Getting git commit...")
        gr = Git(path=self.path)
        commit = gr.get_commit(id)
        return serialize_commit(commit, options)

    async def find_all(self, options=None):
        options = options or {}
        branch = options.get("branch", None)

        from_date = parse_date(options.get("from_date"))
        to_date = parse_date(options.get("to_date"))

        features: list[Feature] = []
        for commit in Repository(
            path_to_repo=self.path,
            only_in_branch=branch,
            num_workers=50,
            since=from_date,
            to=to_date,
        ).traverse_commits():
            self.logger.info(f"Serialize commit {commit.hash}")
            features.append(serialize_commit(commit, options))

        # worker = GitTraversalWorker(
        #     logger=self.logger,
        #     start_date=from_date,
        #     end_date=to_date,
        #     branch=branch,
        #     path=self.path,
        # )
        # iterator = await worker.fetch()
        # async for rows in iterator:
        #     if not rows:
        #         continue
        #     for commit in rows:
        #         self.logger.info(f"Serialize commit {commit.hash}")
        #         features.append(serialize_commit(commit, options))

        return features


def get_ddm_indicators(commit):
    return {
        "dmm_unit_complexity": commit.dmm_unit_complexity,
        "dmm_unit_interfacing": commit.dmm_unit_interfacing,
        "dmm_unit_size": commit.dmm_unit_size,
    }


def serialize_commit(commit, options={}):
    deletions = 0
    insertions = 0

    git_repository = options.get("git_repository", None)
    exclude_files = options.get("exclude_files")
    ddm = options.get("process_ddm", False)
    get_modified_files = options.get("get_modified_files", False)

    modified_files = []
    if get_modified_files:
        for (
            line
        ) in (
            commit.modified_files
        ):  # execute a git diff, that can add extra time to process
            if not exclude_files or not re.match(exclude_files, line.filename):
                deletions += line.deleted_lines
                insertions += line.added_lines
                modified_files.append(line.old_path or line.new_path)

    feature = {
        "git_repository": git_repository,
        "count_deleted_lines": deletions,
        "count_inserted_lines": insertions,
        "date": format_to_utc(commit.committer_date),
        "commit": commit.hash,
        "developer": {
            "full_name": commit.author.name,
            "email": commit.author.email,
        },
        "modified_files": modified_files,
    }

    if ddm:
        # Very slow, only use it if you need it for analysis
        feature = {**feature, **get_ddm_indicators(commit)}

    return Feature.from_dict(feature)


# class GitTraversalWorker(Worker):
#     def __init__(
#         self,
#         branch,
#         path,
#         start_date,
#         end_date,
#         logger,
#         # Not useful
#         max_concurrency: int = 1,
#         period="3600D",
#     ):
#         super().__init__(max_concurrency)
#         self.logger = logger
#         self.path = path
#         self.branch = branch
#         self.period = period
#         self.start_date = parse_date(start_date)
#         self.end_date = parse_date(end_date)
#         self.period_index = 0
#         self.period_index_lock = asyncio.Lock()

#     async def process_data(self, data, options=None):
#         return data, len(data) > 0

#     async def get_commit(self, period_index: int):
#         commits = []
#         start_date = add_delta_to_date(self.start_date, self.period, period_index)
#         end_date = min(
#             self.end_date,
#             add_delta_to_date(start_date, self.period, period_index + 1),
#         )
#         if start_date > end_date:
#             return []

#         self.logger.info(
#             f"Finding all commit in git from {start_date} to {end_date}..."
#         )

#         for commit in Repository(
#             path_to_repo=self.path,
#             only_in_branch=self.branch,
#             num_workers=50,
#             since=start_date,
#             to=end_date,
#         ).traverse_commits():
#             commits.append(commit)

#         return commits

#     async def add_period_to_queue(self, queue: asyncio.Queue):
#         async with self.period_index_lock:
#             await queue.put(self.period_index)
#             self.period_index += 1

#     async def process_task(self, task: int, queue: asyncio.Queue) -> list:
#         period_index = task
#         data = await self.get_commit(period_index)
#         if len(data):
#             await self.add_period_to_queue(queue)
#         return data if data else None

#     async def fetch(self):
#         iterator = await self.work()
#         for _ in range(self.max_concurrency):  # type: ignore
#             await self.add_period_to_queue(iterator.queue)
#         return iterator
