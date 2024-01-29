import random

from faker import Faker

from src.common.utils.string import clean_string


def get_random_title():
    fake = Faker()

    types = ["feat", "fix", "release", "hotfix"]

    feat_type = random.choice(types)

    domain = clean_string(fake.word())
    title = fake.catch_phrase()

    return f"{feat_type}({domain}): {title}"
