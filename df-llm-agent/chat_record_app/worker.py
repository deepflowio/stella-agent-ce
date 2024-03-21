from exception import BadRequestException
import const
from chat_record_app.chat_record import chat_record_worker
from config import config
from utils.curl_tools import curl_tools
from utils import logger
import json
import time

log = logger.getLogger(__name__)


class app_worker(object):

    args = data = user_info = None

    def __init__(self, request):
        app_worker.args = request.args
        if app_worker.args:
            for k, v in self.args.items():
                app_worker.args[k] = [i for i in v]
        app_worker.data = request.json
        app_worker.user_info = request.ctx.user

    # 对话记录
    @classmethod
    async def chat_record_add(cls):
        # 校验todoing
        return await chat_record_worker.chat_record_add(cls.user_info, cls.args, cls.data)

    @classmethod
    async def chat_record_list(cls, id=0):
        # 校验todoing
        return await chat_record_worker.chat_record_list(cls.user_info, id)

    # 评分
    @classmethod
    async def chat_record_score_add(cls, chat_topic_id=0, chat_id=0):
        # 校验todoing
        return await chat_record_worker.chat_record_score_add(
            cls.user_info,
            cls.args,
            cls.data,
            chat_topic_id,
            chat_id,
        )


# worker = app_worker()
