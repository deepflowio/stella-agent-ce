from sanic import Blueprint
import asyncio
from llm_agent_app.worker import app_worker
from utils.response_tools import wrap_resp, wrap_resp_stream
from const import API_PREFIX

llm_agent_app = Blueprint("llm_agent", url_prefix=API_PREFIX)

# agent的配置curd
# 配置必须属于一个用户


@llm_agent_app.route("/llm_agent_config/<platform:str>", name="by_platform")
@llm_agent_app.route("/llm_agent_config")
@wrap_resp
async def llm_agent_config_list(request, platform=""):
    worker = app_worker(request)
    res = await worker.llm_agent_config_list(platform)
    return res


# 流返回
@llm_agent_app.route("/ai/stream/<platform:str>", methods=["POST"])
@wrap_resp_stream
async def llm_agent_stream_system(request, platform=""):
    worker = app_worker(request)
    # 流数据
    res = await worker.llm_agent_stream(platform)
    return res
