from exception import BadRequestException
import const
from resource_app.resource import resource_worker
from config import config
from utils.curl_tools import curl_tools
from utils import logger
import json
import time

log = logger.getLogger(__name__)


class app_worker(object):

    args = data = user_info = None

    def __init__(self, request):
        app_worker.request = request
        app_worker.args = request.args
        if app_worker.args:
            for k, v in self.args.items():
                app_worker.args[k] = [i for i in v]
        # app_worker.files = request.files
        # app_worker.data = request.json
        app_worker.user_info = request.ctx.user

    @classmethod
    async def img_add(cls):
        # 校验todoing
        files = cls.request.files
        return await resource_worker.img_add(cls.user_info, cls.args, files)

    @classmethod
    async def img_add_b64(cls):
        # 校验todoing
        data = cls.request.json
        return await resource_worker.img_add_b64(cls.user_info, cls.args, data)

    @classmethod
    async def img_get(cls, hash_name=""):
        # 校验todoing
        return await resource_worker.img_get(cls.user_info, cls.args, hash_name)
