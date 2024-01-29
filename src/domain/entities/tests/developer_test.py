from ..developer import Developer


def test_developer_creation():
    developer = Developer(full_name="toto", email="toto@email.com")
    assert developer.full_name == "toto"
    assert developer.email == "toto@email.com"


def test_developer_from_dict(fixture_developer_dict):
    developer = Developer.from_dict(fixture_developer_dict)
    assert developer.to_dict() == {
        **fixture_developer_dict,
        "id": fixture_developer_dict["email"],
    }


def test_developer_to_dict():
    developer = Developer(full_name="toto", email="toto@email.com")
    assert developer.to_dict() == {
        "full_name": "toto",
        "id": "toto@email.com",
        "email": "toto@email.com",
    }


def test_developer_comparison(fixture_developer_dict):
    developer_1 = Developer.from_dict(fixture_developer_dict)
    developer_2 = Developer.from_dict(fixture_developer_dict)
    developer_3 = Developer(full_name="toto", email="blabla@email.com")
    assert developer_1 == developer_2
    assert developer_1 != developer_3
