from src.domain.repositories.tests.developers import create_developper  # noqa: F401
from src.domain.repositories.tests.developers import (
    test_it_creates_developer,
    test_it_creates_developer_with_upsert,
    test_it_gets_developer,
    test_it_is_race_condition_proof,
    test_it_raises_exception_if_create_an_existing_developer,
    test_it_raises_exception_if_update_on_inexisting_developer,
    test_it_retrieves_all_developers,
    test_it_updates_developer,
)

test_it_is_race_condition_proof
test_it_gets_developer
test_it_creates_developer
test_it_raises_exception_if_create_an_existing_developer
test_it_updates_developer
test_it_creates_developer_with_upsert
test_it_raises_exception_if_update_on_inexisting_developer
test_it_retrieves_all_developers
