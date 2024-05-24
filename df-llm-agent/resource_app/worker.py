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

    def __init__(self, request):
        self.request = request
        self.args = request.args
        if self.args:
            for k, v in self.args.items():
                self.args[k] = [i for i in v]
        self.user_info = request.ctx.user

    async def img_add(self):
        # 校验todoing
        files = self.request.files
        return await resource_worker.img_add(self.user_info, self.args, files)

    async def img_add_b64(self):
        # 校验todoing
        data = self.request.json
        return await resource_worker.img_add_b64(self.user_info, self.args, data)

    async def img_get(self, hash_name=""):
        # 校验todoing
        return await resource_worker.img_get(self.user_info, self.args, hash_name)
