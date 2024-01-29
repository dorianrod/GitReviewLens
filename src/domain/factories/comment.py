from faker import Faker

from src.common.utils.string import generate_text_exact_length
from src.domain.entities.comment import Comment


class CommentFactory:
    @staticmethod
    def create_comment(
        developer=None, content=None, content_length=None, creation_date=None
    ):
        fake = Faker()
        creation_date = creation_date or fake.date_dtime_this_decade()
        content_length = content_length or fake.pyint(min_value=20, max_value=350)
        content = content or generate_text_exact_length(content_length)
        return Comment(
            developer=developer, content=content, creation_date=creation_date
        )
