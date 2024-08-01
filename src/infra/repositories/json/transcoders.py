import json

from src.common.monitoring.logger import LoggerInterface
from src.common.utils.file import create_path_if_needed
from src.domain.entities.transcoder import Transcoder
from src.domain.repositories.transcoders import TranscodersRepository


class TranscodersJsonRepository(TranscodersRepository):
    logger: LoggerInterface
    path: str

    def __init__(self, logger: LoggerInterface, path: str):
        super().__init__(logger)
        self.path = path

    async def find_all(self, options=None):
        transcoders: dict[str, Transcoder] = {}
        try:
            with open(self.path, "r") as file:
                json_transcoders = json.load(file)
                for name, values in json_transcoders.items():
                    transcoder = Transcoder(
                        name,
                        {item['source']: item['target'] for item in values},
                    )
                    transcoders[name] = transcoder
        except Exception as e:
            self.logger.exception(str(e))

        return list(transcoders.values())

    async def get_by_id(self, id: str):
        try:
            transcoders = await self.find_all()
            items = [transcoder for transcoder in transcoders if transcoder.name == id]
            return items[0] if len(items) > 0 else Transcoder(None, {})
        except Exception as e:
            self.logger.exception(str(e))
            return Transcoder(None, {})

    async def upsert(self, entity: Transcoder, options=None):
        transcoders = await self.find_all()

        transcoders_by_name = {
            transcoder.name: transcoder for transcoder in transcoders
        }
        transcoders_by_name[entity.name] = entity

        create_path_if_needed(self.path)

        with open(self.path, "w") as file:
            json_dump = {}
            for name, transcoder in transcoders_by_name.items():
                json_dump[name] = [
                    {"source": key, "target": value}
                    for key, value in transcoder.values.items()
                ]

            json.dump(json_dump, file)
