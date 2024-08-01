import argparse

from dotenv import load_dotenv

from src.common.settings import reload
from src.infra.monitoring.logger import LoggerDefault

logger = LoggerDefault()

parser = argparse.ArgumentParser(description='Load env file.')
parser.add_argument('--file', type=str)

args = parser.parse_args()

logger.info(f"Load file env: {args.file}")
load_dotenv(dotenv_path=args.file, verbose=True, override=True)

reload()
