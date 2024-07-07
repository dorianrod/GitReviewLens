from src.domain.entities.developer import Developer


async def test_it_creates_developer(developer_repository, fixture_developer_dict):
    developer = Developer.from_dict(fixture_developer_dict)
    await developer_repository.create(developer)

    created_developers = await developer_repository.find_all()
    assert created_developers == [developer]


async def test_it_updates_developer(developer_repository, fixture_developer_dict):
    developer = Developer.from_dict(fixture_developer_dict)
    await developer_repository.create(developer)

    new_developer = Developer.from_dict(fixture_developer_dict)
    new_developer.full_name = "toto"
    await developer_repository.update(new_developer)

    assert await developer_repository.find_all() == [new_developer]


async def test_it_retrieves_all_developers(
    developer_repository,
    fixture_developer_dict,
    fixture_developer_2_dict,
):
    developer = Developer.from_dict(fixture_developer_dict)
    developer_2 = Developer.from_dict(fixture_developer_2_dict)

    await developer_repository.create(developer)
    await developer_repository.create(developer_2)

    assert await developer_repository.find_all() == [developer, developer_2]
