from aredis import StrictRedis
from aredis import StrictRedisCluster
from aredis.exceptions import RedisError

import urllib.parse
import aiofiles
import os
import sys
import importlib
from exception import BadRequestException
from utils import logger
from config import config
import const
import traceback

log = logger.getLogger(__name__)


class cache(object):

    redis_cluster = config.redis_cluster
    redis_host = config.redis_host
    redis_port = config.redis_port
    redis_db = config.redis_db
    redis_password = urllib.parse.quote_plus(config.redis_password)

    @classmethod
    async def GetCacheServer(cls):
        # 集群
        if cls.redis_cluster:
            startup_nodes = []
            for host in cls.redis_host:
                node = {'host': f"{host}", 'port': cls.redis_port}
                startup_nodes.append(node)
            client = StrictRedisCluster(startup_nodes=startup_nodes, password=cls.redis_password, decode_responses=True)
        else:
            if isinstance(cls.redis_host, list):
                redis_host = cls.redis_host[0]
            else:
                redis_host = cls.redis_host

            client = StrictRedis(host=f"{redis_host}", port=cls.redis_port, db=cls.redis_db, password=cls.redis_password, decode_responses=True)

        try:
            res = await client.ping()
            if not res:
                raise BadRequestException("FAIL", f"{const.FAIL}: redis ping 返回 false", f"{const.FAIL}: {traceback.format_exc()}")
        except Exception:
            raise BadRequestException("FAIL", f"{const.FAIL}: redis ping 失败", f"{const.FAIL}: {traceback.format_exc()}")
        return client


cache = cache()
