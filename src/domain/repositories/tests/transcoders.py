from src.domain.entities.transcoder import Transcoder


def test_it_creates_transcoder(transcoder_repository, fixture_transcoder_dict):
    transcoder = Transcoder.from_dict(fixture_transcoder_dict)
    transcoder_repository.create(transcoder)

    created_transcoders = transcoder_repository.find_all()
    assert created_transcoders == [transcoder]


def test_it_updates_transcoder(transcoder_repository, fixture_transcoder_dict):
    transcoder = Transcoder.from_dict(fixture_transcoder_dict)
    transcoder_repository.create(transcoder)

    new_transcoder = Transcoder.from_dict(fixture_transcoder_dict)
    new_transcoder.values["test"] = "toto"
    transcoder_repository.update(new_transcoder)

    assert transcoder_repository.find_all() == [new_transcoder]


def test_it_retrieves_all_transcoders(
    transcoder_repository,
    fixture_transcoder_dict,
    fixture_transcoder_2_dict,
):
    transcoder = Transcoder.from_dict(fixture_transcoder_dict)
    transcoder_2 = Transcoder.from_dict(fixture_transcoder_2_dict)

    transcoder_repository.create(transcoder)
    transcoder_repository.create(transcoder_2)

    assert transcoder_repository.find_all() == [transcoder, transcoder_2]


def test_find_all_with_invalid_directory(transcoder_repository):
    transcoder = transcoder_repository.get_by_id("not_exists")
    assert transcoder is not None
    assert transcoder.values == {}
