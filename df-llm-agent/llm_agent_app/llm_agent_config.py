from exception import BadRequestException
import const
import json
from database import db_models
from utils import logger

from config import config

log = logger.getLogger(__name__)


# agent配置
class llmAgentConfigWorker(object):

    # 校验数据
    @staticmethod
    async def verify_data(data):
        pass

    # 获取所有配置
    @classmethod
    async def llm_agent_config_list(cls, user_info, platform=""):
        # user_id = user_info.get("ID", 0)
        data_info = {}
        # data_info["user_id"] = user_id

        if platform:
            data_info["platform"] = platform

        res = {}
        if hasattr(config, "platforms"):
            res_config = config.platforms
            for _info in res_config:
                __info = {}
                _platform = _info.get('platform', '')

                if platform and platform != _platform:
                    continue
                _enable = _info.get('enable', False)
                __info['enable'] = "1" if _enable else "0"
                __info['model'] = _info.get('model', '')
                __info['engine_name'] = _info.get('engine_name', [])

                res[f"{_platform}"] = __info

        return res


llm_agent_config_worker = llmAgentConfigWorker()
