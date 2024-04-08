import asyncio
from server import app
from const import HOST, PORT
import multiprocessing
from config import config
from database.db_init import db_init
from utils import logger
import argparse

logger_manager = logger.LoggerManager('df-llm-agent', config.log_level, config.log_file)
logger_manager.init_logger()

log = logger.getLogger(__name__)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, help="test port")
    args = parser.parse_args()

    if args.port:
        APP_PORT = args.port
    else:
        APP_PORT = PORT

    # db 初始化&issu执行
    asyncio.run(db_init.db_init())

    try:
        workers = multiprocessing.cpu_count()
        log.info(f'========  Starting df-llm-agent application listen {HOST}:{APP_PORT}, workers={workers} ...========')
        app.run(host=HOST, port=APP_PORT, workers=workers, access_log=True)
    except KeyboardInterrupt:
        log.info("ctrl+c Stopping df-llm-agent application...")
