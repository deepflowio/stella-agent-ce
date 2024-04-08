from tortoise import Tortoise, run_async, connections
from config import config
from tzlocal import get_localzone
import urllib.parse

mysql_host = config.mysql_host
mysql_port = config.mysql_port
mysql_database = config.mysql_database

mysql_user_name = config.mysql_user_name
mysql_user_password = urllib.parse.quote_plus(config.mysql_user_password)


async def init_db():
    dbconfig = {
        'connections': {
            'default': {
                'engine': 'tortoise.backends.mysql',
                'credentials': {
                    'host': mysql_host,
                    'port': mysql_port,
                    'user': mysql_user_name,
                    'password': mysql_user_password,
                    'database': mysql_database,
                    'connect_timeout': 60,
                    'maxsize': 10,
                    'echo': True #config.sql_show
                }
            }
        },
        'apps': {
            'llm_agent': {
                'models': ['database.db_models']
            }
        },
        'timezone': str(get_localzone())
    }

    await Tortoise.init(config=dbconfig)

    # 不要依据表结构来创建表，已经提前创建好
    # await Tortoise.generate_schemas()


async def close_db():
    await connections.close_all()


def init_db_sync():
    run_async(init_db())


def close_db_sync():
    run_async(close_db())
