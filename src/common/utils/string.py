import hashlib
import re

from faker import Faker


def get_hash(message):
    sha256 = hashlib.sha256()
    sha256.update(message.encode("utf-8"))
    hash_result = sha256.hexdigest()
    return hash_result


def generate_text_exact_length(content_length):
    fake = Faker()

    random_text = (
        fake.text(max_nb_chars=content_length)
        if content_length > 5
        else "_" * 5  # limitation of faker
    )

    if len(random_text) < content_length:
        diff = content_length - len(random_text)
        random_text += "_" * diff

    return random_text


def clean_string(input_string):
    if not input_string:
        return ""

    cleaned_string = input_string.lower()
    cleaned_string = re.sub(r'\W+', '', cleaned_string)
    return cleaned_string
