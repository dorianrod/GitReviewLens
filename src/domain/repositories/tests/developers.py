from src.domain.entities.developer import Developer


def test_it_creates_developer(developer_repository, fixture_developer_dict):
    developer = Developer.from_dict(fixture_developer_dict)
    developer_repository.create(developer)

    created_developers = developer_repository.find_all()
    assert created_developers == [developer]


def test_it_updates_developer(developer_repository, fixture_developer_dict):
    developer = Developer.from_dict(fixture_developer_dict)
    developer_repository.create(developer)

    new_developer = Developer.from_dict(fixture_developer_dict)
    new_developer.full_name = "toto"
    developer_repository.update(new_developer)

    assert developer_repository.find_all() == [new_developer]


def test_it_retrieves_all_developers(
    developer_repository,
    fixture_developer_dict,
    fixture_developer_2_dict,
):
    developer = Developer.from_dict(fixture_developer_dict)
    developer_2 = Developer.from_dict(fixture_developer_2_dict)

    developer_repository.create(developer)
    developer_repository.create(developer_2)

    assert developer_repository.find_all() == [developer, developer_2]
