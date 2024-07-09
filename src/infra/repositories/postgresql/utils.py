from sqlalchemy import select

from src.domain.exceptions import AlreadyExistsException, NotExistsException


def raise_exception_if_upsert_cannot_be_done(options, entity):
    options = options or {}
    is_new = options.get("is_new", None)
    if is_new is True and entity is not None:
        raise AlreadyExistsException()
    if is_new is False and entity is None:
        raise NotExistsException()


async def upsert(session, entity, SqlEntity, options=None):
    options = options or {}
    is_new = options.get("is_new", None)

    columns = SqlEntity.from_entity(entity, options)

    if is_new is None or is_new is False:
        stmt = select(SqlEntity).where(SqlEntity.id == entity.id)
        result = await session.execute(stmt)
        existing_entity = result.scalars().one_or_none()
        raise_exception_if_upsert_cannot_be_done(options, existing_entity)

        sql_entity = existing_entity
        if sql_entity:
            for col, value in columns.items():
                setattr(sql_entity, col, value)
            await session.merge(sql_entity)
        else:
            sql_entity = SqlEntity(**columns)
            session.add(sql_entity)

    elif is_new:
        sql_entity = SqlEntity(**columns)
        session.add(sql_entity)

    return entity
