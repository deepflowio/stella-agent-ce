from exception import BadRequestException
import const
from llm_agent_app.llm_agent import llm_agent_worker
from config import config
from utils.curl_tools import curl_tools
from utils import logger
import json
import time

from llm_agent_app.llm_agent_config import llm_agent_config_worker

log = logger.getLogger(__name__)


class app_worker(object):

    args = data = user_info = None

    def __init__(self, request):
        app_worker.request = request
        app_worker.args = request.args
        if app_worker.args:
            for k, v in self.args.items():
                app_worker.args[k] = [i for i in v]

        app_worker.data = request.json
        app_worker.user_info = request.ctx.user

    @classmethod
    async def llm_agent_config_add(cls):
        # 校验todoing
        return await llm_agent_config_worker.llm_agent_config_add(cls.user_info, cls.args, cls.data)

    @classmethod
    async def llm_agent_config_list(cls, platform=""):

        return await llm_agent_config_worker.llm_agent_config_list(cls.user_info, platform)

    @classmethod
    async def llm_agent_config_update(cls, platform="", key_name=""):
        # 校验todoing
        return await llm_agent_config_worker.llm_agent_config_update(cls.user_info, platform, key_name, cls.args, cls.data)

    @classmethod
    async def llm_agent_config_delete(cls, platform="", engine_name=""):
        # 校验todoing
        return await llm_agent_config_worker.llm_agent_config_delete(cls.user_info, platform, engine_name, cls.args, cls.data)

    # 流处理
    @classmethod
    async def llm_agent_stream(cls, platform, prompt_type=''):
        # 校验todoing
        engine_name = cls.args.get("engine", "")
        if not engine_name:
            raise BadRequestException("INVALID_PARAMETERS", f"{const.INVALID_PARAMETERS}, 缺失使用的引擎名称")
        return await llm_agent_worker.assistant_stream(cls.request, cls.user_info, platform, engine_name, prompt_type, cls.args, cls.data)

    # 组件
    @classmethod
    async def llm_agent_module(cls, platform):
        engine_name = cls.args.get("engine", "")
        if not engine_name:
            raise BadRequestException("INVALID_PARAMETERS", f"{const.INVALID_PARAMETERS}, 缺失使用的引擎名称")
        return await llm_agent_worker.module(cls.request, cls.user_info, platform, engine_name, cls.args, cls.data)
