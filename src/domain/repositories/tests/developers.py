import asyncio

import pytest

from src.domain.entities.developer import Developer


@pytest.fixture(scope="function")
def create_developper(developer_repository, fixture_developer_dict):
    async def fnc():
        developer = Developer.from_dict(fixture_developer_dict)
        await developer_repository.create(developer)
        return developer

    return fnc


class MixinDeveloper:
    async def test_it_is_race_condition_proof(
        self, developer_repository, fixture_developer_dict
    ):
        async def upsert_developer():
            await developer_repository.upsert(
                Developer.from_dict(fixture_developer_dict)
            )

        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(upsert_developer()) for _ in range(5)]
        await asyncio.gather(*tasks)
        assert len(await developer_repository.find_all()) == 1

    async def test_it_gets_developer(self, developer_repository, create_developper):
        created_developper = await create_developper()
        dev_in_db = await developer_repository.get_by_id(created_developper.id)
        assert dev_in_db == created_developper

    async def test_it_creates_developer(self, create_developper, developer_repository):
        created_developper = await create_developper()
        assert await developer_repository.find_all() == [created_developper]

    async def test_it_creates_developer_with_upsert(
        self, developer_repository, fixture_developer_dict
    ):
        developer = Developer.from_dict(fixture_developer_dict)
        await developer_repository.upsert(developer)

        all_dev = await developer_repository.find_all()
        assert all_dev == [developer]

    async def test_it_raises_exception_if_create_an_existing_developer(
        self, developer_repository, create_developper, fixture_developer_dict
    ):
        await create_developper()
        with pytest.raises(Exception):
            await developer_repository.create(fixture_developer_dict)

    async def test_it_raises_exception_if_update_on_inexisting_developer(
        self, developer_repository, fixture_developer_dict
    ):
        with pytest.raises(Exception):
            await developer_repository.update(fixture_developer_dict)

    async def test_it_updates_developer(
        self, developer_repository, fixture_developer_dict, create_developper
    ):
        await create_developper()

        new_developer = Developer.from_dict(
            {**fixture_developer_dict, "full_name": "toto"}
        )
        await developer_repository.update(new_developer)

        all_dev = await developer_repository.find_all()
        assert all_dev == [new_developer]

    async def test_it_retrieves_all_developers(
        self,
        developer_repository,
        fixture_developer_dict,
        fixture_developer_2_dict,
    ):
        developer = Developer.from_dict(fixture_developer_dict)
        developer_2 = Developer.from_dict(fixture_developer_2_dict)

        await developer_repository.create(developer)
        await developer_repository.create(developer_2)

        assert await developer_repository.find_all() == [developer, developer_2]
