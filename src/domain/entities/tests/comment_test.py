from datetime import datetime

from src.common.utils.date import parse_date

from ..comment import Comment
from ..developer import Developer


def test_comment_creation(fixture_developer_dict):
    comment = Comment(
        content="Please review",
        developer=Developer.from_dict(fixture_developer_dict),
        creation_date=parse_date("2023-10-25T11:10:13"),
    )
    assert comment.developer == Developer.from_dict(fixture_developer_dict)
    assert comment.content == "Please review"
    assert comment.creation_date == parse_date("2023-10-25T11:10:13")


def test_comment_from_dict(fixture_comment_dict):
    comment = Comment.from_dict(fixture_comment_dict)
    assert comment.size == len(fixture_comment_dict["content"])
    assert comment.content == fixture_comment_dict["content"]
    assert comment.creation_date == parse_date(fixture_comment_dict["creation_date"])
    assert comment.developer == Developer.from_dict(fixture_comment_dict["developer"])


def test_comment_without_content_to_dict(fixture_comment_dict):
    comment = Comment.from_dict({**fixture_comment_dict, "content": None})
    assert comment.to_dict() == {
        **fixture_comment_dict,
        'id': '02fc4129806ff8b8e53198c5f14638abcc2c5f81297a027f3713524bd1a088b8',
        "creation_date": "2023-10-25T11:11:13Z",
        "content": "",
        "size": 0,
    }


def test_comment_to_dict(fixture_comment_dict):
    comment = Comment.from_dict(fixture_comment_dict)
    assert comment.to_dict() == {
        **fixture_comment_dict,
        'id': '574c8e69955392b8d64d669588068c724c1961784e1938c2decb4755e00ed2fd',
        "creation_date": "2023-10-25T11:11:13Z",
        "size": len(fixture_comment_dict["content"]),
    }


def test_comment_comparison(fixture_comment_dict, fixture_comment_2_dict):
    comment_1 = Comment.from_dict(fixture_comment_dict)
    comment_2 = Comment.from_dict(fixture_comment_dict)
    comment_3 = Comment.from_dict(fixture_comment_2_dict)

    assert comment_1 == comment_2
    assert comment_1 != comment_3
