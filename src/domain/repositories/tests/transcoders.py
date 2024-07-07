from src.domain.entities.transcoder import Transcoder


async def test_it_creates_transcoder(transcoder_repository, fixture_transcoder_dict):
    transcoder = Transcoder.from_dict(fixture_transcoder_dict)
    await transcoder_repository.create(transcoder)

    created_transcoders = await transcoder_repository.find_all()
    assert created_transcoders == [transcoder]


async def test_it_updates_transcoder(transcoder_repository, fixture_transcoder_dict):
    transcoder = Transcoder.from_dict(fixture_transcoder_dict)
    await transcoder_repository.create(transcoder)

    new_transcoder = Transcoder.from_dict(fixture_transcoder_dict)
    new_transcoder.values["test"] = "toto"
    await transcoder_repository.update(new_transcoder)

    assert await transcoder_repository.find_all() == [new_transcoder]


async def test_it_retrieves_all_transcoders(
    transcoder_repository,
    fixture_transcoder_dict,
    fixture_transcoder_2_dict,
):
    transcoder = Transcoder.from_dict(fixture_transcoder_dict)
    transcoder_2 = Transcoder.from_dict(fixture_transcoder_2_dict)

    await transcoder_repository.create(transcoder)
    await transcoder_repository.create(transcoder_2)

    assert await transcoder_repository.find_all() == [transcoder, transcoder_2]


async def test_find_all_with_invalid_directory(transcoder_repository):
    transcoder = await transcoder_repository.get_by_id("not_exists")
    assert transcoder is not None
    assert transcoder.values == {}
