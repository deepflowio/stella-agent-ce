from exception import BadRequestException
import const
from llm_agent_app.llm_agent import llmAgentWorker
from config import config
from utils.curl_tools import curl_tools
from utils import logger
import json
import time

from llm_agent_app.llm_agent_config import llm_agent_config_worker

log = logger.getLogger(__name__)


class app_worker(object):

    def __init__(self, request):
        self.request = request
        self.args = request.args
        if self.args:
            for k, v in self.args.items():
                self.args[k] = [i for i in v]

        self.data = request.json
        self.user_info = request.ctx.user

    async def llm_agent_config_add(self):
        # 校验todoing
        return await llm_agent_config_worker.llm_agent_config_add(self.user_info, self.args, self.data)

    async def llm_agent_config_list(self, platform=""):

        return await llm_agent_config_worker.llm_agent_config_list(self.user_info, platform)

    async def llm_agent_config_update(self, platform="", key_name=""):
        # 校验todoing
        return await llm_agent_config_worker.llm_agent_config_update(self.user_info, platform, key_name, self.args, self.data)

    async def llm_agent_config_delete(self, platform="", engine_name=""):
        # 校验todoing
        return await llm_agent_config_worker.llm_agent_config_delete(self.user_info, platform, engine_name, self.args, self.data)

    # 流处理
    async def llm_agent_stream(self, platform, prompt_type=''):
        # 校验todoing
        engine_name = self.args.get("engine", "")
        if not engine_name:
            raise BadRequestException("INVALID_PARAMETERS", f"{const.INVALID_PARAMETERS}, 缺失使用的引擎名称")
        llm_agent_worker = llmAgentWorker(self.request)
        return await llm_agent_worker.assistant_stream(self.user_info, platform, engine_name, prompt_type, self.args, self.data)

    # 组件
    async def llm_agent_module(self, platform):
        engine_name = self.args.get("engine", "")
        if not engine_name:
            raise BadRequestException("INVALID_PARAMETERS", f"{const.INVALID_PARAMETERS}, 缺失使用的引擎名称")
        llm_agent_worker = llmAgentWorker(self.request)
        return await llm_agent_worker.module(self.user_info, platform, engine_name, self.args, self.data)
