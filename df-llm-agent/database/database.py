from tortoise import Tortoise, run_async
from tzlocal import get_localzone
import urllib.parse
import aiofiles
import os
import sys
import importlib

from utils import logger
from config import config

mysql_host = config.mysql_host
mysql_port = config.mysql_port
mysql_database = config.mysql_database

mysql_user_name = config.mysql_user_name
mysql_user_password = urllib.parse.quote_plus(config.mysql_user_password)

env_db_version = os.getenv('DB_VERSION')

log = logger.getLogger(__name__)


class database(object):

    @classmethod
    async def GetConnectionWithoutDatabase(cls):

        if not env_db_version:
            log.error("环境变量中缺少DB_VERSION")
            sys.exit(1)

        mysql_conn = f"mysql://{mysql_user_name}:{mysql_user_password}@{mysql_host}:{mysql_port}/"
        await Tortoise.init(db_url=mysql_conn, modules={'models': []}, timezone=str(get_localzone()))
        return Tortoise.get_connection("default")

    @classmethod
    async def CreateDatabaseIfNotExists(cls, client):

        affected_rows, result = await client.execute_query("show databases")
        # 提取所有数据库
        databases = []
        for item in result:
            databases.append(item['Database'])

        if mysql_database not in databases:
            affected_rows, result = await client.execute_query(f"create database {mysql_database}")
            log.info(f"初始化创建数据库: {mysql_database} 成功")
            return True
        else:
            return False

    @classmethod
    async def GetConnectionWithDatabase(cls):
        db_conn = f"mysql://{mysql_user_name}:{mysql_user_password}@{mysql_host}:{mysql_port}/{mysql_database}"
        await Tortoise.init(db_url=db_conn, modules={'models': []}, timezone=str(get_localzone()))
        return Tortoise.get_connection("default")

    @classmethod
    async def InitTablesIfNotExists(cls, client):

        sql_path = f"{config.instance_path}/database/init.sql"
        # sql_path = "/root/df-llm-agent-test/df-llm-agent/database/init.sql"

        if os.path.exists(sql_path):
            async with aiofiles.open(sql_path) as f:
                sql = await f.read()

            affected_rows, result = await client.execute_query(sql)
            affected_rows, result = await client.execute_query(f"INSERT INTO db_version (`version`) VALUES ('{env_db_version}');")
            log.info(f"初始化表成功,sql路径: {sql_path}")
            log.info(f"version版本为:{env_db_version}")
        else:
            raise Exception(f"初始化sql: {sql_path} 不存在,终止运行")

    @classmethod
    async def DropDatabaseIfInitTablesFailed(cls, client):
        try:
            await cls.InitTablesIfNotExists(client)
        except Exception as e:
            await cls.DropDatabase(client)
            msg = f"首次安装服务，初始化表失败,回滚并删除数据库, 错误: {e}"
            raise Exception(msg)

    # @classmethod
    # async def InitTablesWithoutRollBack(cls, client):
    #     try:
    #         await cls.InitTablesIfNotExists(client)
    #     except Exception as e:
    #         log.info(f"初始化表失败, 错误: {e}")

    @classmethod
    async def InitTables(cls, client):
        # 执行 SQL 语句
        sql = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{mysql_database}' AND TABLE_NAME='db_version'"
        affected_rows, results = await client.execute_query(sql)

        # 表存在
        if affected_rows > 0:
            log.info("数据库存在,db_version表存在,执行issu")
            return True
        else:
            log.info("数据库存在,db_version表不存在,初始化表")
            await cls.InitTablesIfNotExists(client)
            return False

    @classmethod
    async def DropDatabase(cls, client):
        affected_rows, result = await client.execute_query(f"drop database {mysql_database}")

    # 获取用来升级的sql文件名（版本号.小版本号）
    @classmethod
    async def getAscSortedNextVersions(cls, up_sql_path, db_version):
        # 获取用来升级的sql文件名（版本号.小版本号）
        filename_list = []
        for _file in os.listdir(up_sql_path):
            filename = os.path.splitext(_file)[0]
            filename_suffix = os.path.splitext(_file)[1]
            # print(f"{filename},{filename_suffix}")
            # 非sql跳过
            if "sql" not in filename_suffix:
                continue
            filename_list.append(filename)

        # 防止 db里记录了6.1.1.0 ，但是issu 里从6.1.1.1获取issu的list，导致db记录的值不存在list里的index里导致报错
        if db_version and f"{db_version}" not in filename_list:
            filename_list.append(f"{db_version}")

        # 没有需要执行的issu 或者获取不到db里系统版本号
        if not filename_list or not db_version:
            return []

        # 获取所有已经存在的issu
        # 补齐0.0.0.0格式
        # 版本排序
        n_filename_list = []
        # print(filename_list)
        for v in filename_list:
            v_l = v.split(".")
            v_l = list(map(int, v.split('.')))
            if len(v_l) < 3 or len(v_l) > 4:
                continue

            if len(v_l) == 3:
                v_l.append(0)

            if v_l not in n_filename_list:
                n_filename_list.append(v_l)

        n_filename_list.sort()

        # 转成["6.1.1.0","6.1.2.0"] 格式
        n_filename = list(map(lambda xs: '.'.join(str(x) for x in xs), n_filename_list))

        # db里已经到的版本，前面的issu全部跳过，只执行比他大的issu
        try:
            v_index = n_filename.index(db_version)
        except ValueError as e:
            log.error(f"系统里使用了不存在的版本：{db_version}, 错误：{e},跳过issu升级")
            sys.exit(1)
        e_n_filename = n_filename[v_index + 1::]
        if len(e_n_filename) <= 0:
            # db里已经是最新的版本了，返回最后一个版本
            return n_filename[-1]
        else:
            return e_n_filename

    @classmethod
    async def ExecuteIssus(cls, client):

        # 正常不会出现，除非人为的置空
        version = ""
        # 数据库记录的版本
        affected_rows, results = await client.execute_query("select version from db_version limit 1")
        if affected_rows > 0:
            version = results[0]["version"]

        db_sql_path = f"{config.instance_path}/database/issu"
        # db_sql_path = "/root/df-llm-agent-test/df-llm-agent/database/issu"

        #
        up_issu_list = await cls.getAscSortedNextVersions(db_sql_path, version)

        # 没有需要执行的issu
        if len(up_issu_list) <= 0 or isinstance(up_issu_list, str):
            if version:
                #
                if version != env_db_version:
                    # affected_rows, result = await client.execute_query(f"UPDATE db_version SET version='{env_db_version}', updated_at= now();")
                    log.info(f"没有需要执行的issu且数据库记录中的version版本: {version} 和环境变量中的版本: {env_db_version} 不一致。请检查服务镜像是否回退、手动修改数据库记录中的version版本")
                else:
                    print("当前issu版本已经最新")
            else:
                affected_rows, result = await client.execute_query(f"UPDATE db_version SET version='{env_db_version}', updated_at= now();")
                log.info(f"没有需要执行的issu且数据库记录中的version为空, 和环境变量中的版本: {env_db_version} 不一致, 更新db_version到环境变量版本")

            return True

        # 多个issu需要循环执行升级
        for _version in up_issu_list:

            # 获取该版本的issu的sql（升级时可能没有issu）
            sql_path = f"{db_sql_path}/{_version}.sql"
            msg = f"issu文件: {sql_path}"

            if os.path.exists(sql_path):
                async with aiofiles.open(sql_path) as f:
                    sql = await f.read()

                try:
                    affected_rows, result = await client.execute_query(sql)
                    log.info(f"执行成功, {msg}")
                except Exception as e:
                    log.info(f"执行失败, {msg}, 错误：{e}")
                    sys.exit(1)
            else:
                log.info(f"{msg} 不存在, 跳过")

            # 是否有脚本

            __version = _version.replace(".", "")

            script_file_path = f"{db_sql_path}/{__version}_script.py"

            if os.path.exists(script_file_path):
                log.info(f"脚本执行成功, 文件路径: {script_file_path}")
                script_module = importlib.import_module(f"database.issu.{__version}_script")
                script_module.script_service.run(client)


database = database()
