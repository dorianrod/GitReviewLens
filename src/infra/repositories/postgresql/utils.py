from src.domain.exceptions import AlreadyExistsException, NotExistsException


def raise_exception_if_upsert_cannot_be_done(options, entity):
    options = options or {}
    is_new = options.get("is_new", None)
    if is_new is True and entity is not None:
        raise AlreadyExistsException()
    if is_new is False and entity is None:
        raise NotExistsException()
