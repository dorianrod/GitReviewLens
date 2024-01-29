from src.domain.repositories.tests.pull_requests import (
    test_cannot_create_into_wrong_git_repo,
    test_create_same_id_in_two_repos,
    test_find_all,
    test_find_all_does_not_return_pull_requests_from_other_repositories,
    test_get_by_id,
    test_get_by_id_does_not_return_pull_requests_from_other_repositories,
    test_update,
    test_upsert,
    test_upsert_all,
)

test_cannot_create_into_wrong_git_repo
test_create_same_id_in_two_repos
test_find_all
test_find_all_does_not_return_pull_requests_from_other_repositories
test_get_by_id
test_get_by_id_does_not_return_pull_requests_from_other_repositories
test_update
test_upsert
test_upsert_all
