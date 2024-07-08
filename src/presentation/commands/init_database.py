import argparse
import asyncio

from dotenv import load_dotenv

from src.app.controllers.database_dump_and_init.init_database import (
    InitDatabaseController,
)
from src.infra.monitoring.logger import LoggerDefault
from src.presentation.commands.base_command import Command
from src.settings import reload

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--load_pull_requests', action=argparse.BooleanOptionalAction)
parser.add_argument('--load_features', action=argparse.BooleanOptionalAction)
parser.add_argument('--drop_db', action=argparse.BooleanOptionalAction)
parser.add_argument('--path', type=str)
parser.add_argument('--env', type=str, default="")

args = parser.parse_args()

if args.env:
    load_dotenv(dotenv_path=args.env, verbose=True, override=True)
    reload()

command = Command(InitDatabaseController(logger=LoggerDefault()))

asyncio.run(
    command.launch(
        load_pull_requests=args.load_pull_requests,
        load_features=args.load_features,
        drop_db=args.drop_db,
        path=args.path or "/data",
    )
)
