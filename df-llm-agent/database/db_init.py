from tortoise import Tortoise, run_async
from utils import logger
from database.database import database
import sys


class dbTools(object):

    @classmethod
    async def db_init(cls):
        # 无db下连接mysql
        try:
            client = await database.GetConnectionWithoutDatabase()
        except Exception as e:
            print(f"连接mysql失败: {e}")
            sys.exit(1)

        # 数据库不存在则创建否则跳过
        try:
            first_install = await database.CreateDatabaseIfNotExists(client)
        except Exception as e:
            print(f"database不存在, 创建失败: {e}")
            sys.exit(1)
        finally:
            await Tortoise.close_connections()

        # 使用db连接mysql
        try:
            client = await database.GetConnectionWithDatabase()
        except Exception as e:
            print(f"连接数据库失败: {e}")
            sys.exit(1)

        #
        try:
            # 第一次安装，初始化安装表&记录version为环境变量里的版本（不需执行issu，初始化sql里已经包含），如果失败就回滚并删除数据库
            if first_install:
                await database.DropDatabaseIfInitTablesFailed(client)
            else:
                # 不是第一次安装，不存在db_version表，就初始化安装表,如果失败不删除数据库(正常不会出现这个问题，除非人为的删除该表)
                update_issu = await database.InitTables(client)
                # 存在db_version表,需要执行issu升级
                if update_issu:
                    try:
                        # 获取db_version中version版本，判断issu中版本，只执行大于version版本的issu.sql
                        await database.ExecuteIssus(client)
                    except Exception as e:
                        print(f"issu执行失败: {e}")
                        sys.exit(1)
        except Exception as e:
            print(f"初始化表失败: {e}")
            sys.exit(1)
        finally:
            await Tortoise.close_connections()


db_init = dbTools()
