from tortoise.transactions import atomic, in_transaction
from tortoise.exceptions import BaseORMException, OperationalError
from tortoise.expressions import Q
from tortoise.functions import Coalesce, Count, Length, Lower, Min, Sum, Trim, Upper
from exception import BadRequestException
import const
from database import db_models
from utils import logger
import traceback
import datetime
import json
import os
import base64
from utils.tools import generate_uuid

from database.cache import cache

log = logger.getLogger(__name__)


class resourceWorker(object):

    # 校验数据
    @staticmethod
    async def verify_data(file):
        pass

    # 新增
    @classmethod
    async def img_add(cls, user_info, args, files):

        allow_type = ['.jpg', '.png']

        file = files.get('file')

        file_name = file.name
        file_extension = os.path.splitext(file_name)[1]

        if file_extension not in allow_type:
            raise BadRequestException("FAIL", f"{const.FAIL}: 文件类型格式错误", f"{const.FAIL}: 文件类型格式错误")

        # 文件大小,byte
        filesize = len(file.body)
        if filesize > 10 * 1024 * 1024:
            # 10M
            raise BadRequestException("FAIL", f"{const.FAIL}: 文件大小超过最大值", f"{const.FAIL}: 文件大小超过最大值")

        time_now = datetime.datetime.now()
        create_time = time_now.strftime(const.DATE_PATTEN)
        expire_time = (time_now + datetime.timedelta(days=1)).strftime(const.DATE_PATTEN)

        cache_client = await cache.GetCacheServer()

        # 记录
        lcuuid = generate_uuid()

        file_info = {}
        file_info['lcuuid'] = lcuuid
        file_info['name'] = file_name
        # file_info['size'] = filesize
        file_info['create_time'] = create_time
        file_info['expire_time'] = expire_time
        file_info['img'] = f"data:{file.type};base64,{base64.b64encode(file.body).decode('utf8')}"
        try:
            await cache_client.hmset(lcuuid, file_info)
            await cache_client.expire(lcuuid, 86400)
            return await cache_client.hgetall(lcuuid)
        except Exception:
            raise BadRequestException("FAIL", f"{const.FAIL}: 保存图片失败", f"{const.FAIL}: {traceback.format_exc()}")

    @classmethod
    async def img_add_b64(cls, user_info, args, data):
        time_now = datetime.datetime.now()
        create_time = time_now.strftime(const.DATE_PATTEN)
        expire_time = (time_now + datetime.timedelta(days=1)).strftime(const.DATE_PATTEN)

        cache_client = await cache.GetCacheServer()

        # 记录
        lcuuid = generate_uuid()

        file_info = {}
        file_info['lcuuid'] = lcuuid
        file_info['name'] = data.get('name', lcuuid)
        # file_info['size'] = data.get('size')
        file_info['create_time'] = create_time
        file_info['expire_time'] = expire_time
        file_info['img'] = data.get('img')

        try:
            await cache_client.hmset(lcuuid, file_info)
            await cache_client.expire(lcuuid, 86400)
            return await cache_client.hgetall(lcuuid)
        except Exception:
            raise BadRequestException("FAIL", f"{const.FAIL}: 保存图片失败", f"{const.FAIL}: {traceback.format_exc()}")

    @classmethod
    async def img_get(cls, user_info, args, hash_name):
        cache_client = await cache.GetCacheServer()
        try:
            res = await cache_client.hgetall(hash_name)
            # image_bytes = base64.b64decode(image_base64)
            return res
        except Exception:
            raise BadRequestException("FAIL", f"{const.FAIL}: 获取图片失败", f"{const.FAIL}: {traceback.format_exc()}")


resource_worker = resourceWorker()
