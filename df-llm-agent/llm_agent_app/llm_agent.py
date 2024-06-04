from openai import AsyncAzureOpenAI, AzureOpenAI
import openai

import tiktoken

import dashscope

import qianfan

import zhipuai

from http import HTTPStatus
from exception import BadRequestException
import const
import json
from utils import logger
from database import db_models
import datetime
import copy
from utils.curl_tools import curl_tools
from utils.tools import generate_uuid
from config import config
from chat_record_app.chat_record import chat_record_worker

from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableBranch

log = logger.getLogger(__name__)

# https://learn.microsoft.com/zh-cn/azure/ai-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions

# https://help.aliyun.com/zh/dashscope/developer-reference/?spm=a2c4g.11174283.0.0.2b8a16e9dSzAQL

# https://cloud.baidu.com/doc/WENXINWORKSHOP/s/xlmokikxe#%E5%A4%9A%E8%BD%AE%E5%AF%B9%E8%AF%9D

# https://cloud.tencent.com/document/product/1729/97732#bac1763f-47e3-4564-8712-9a510b60fabd

# 配置文件(engine_name可以多个具体看各个平台支持的引擎列表，其他key需要在各个平台保持唯一)
# 注释部分只是说明格式，参数值没有任何意义
# azure需要的配置项
# {
#     "api_key": "api_key_xxx",
#     "api_type": "azure",
#     "api_base":"https://df.openai.azure.com/",
#     "api_version":"2023-07-01-preview",
#     "engine_name":"DF-GPT-16K",
#     "engine_name":"DF-GPT4"
# }

# dashscope需要的配置文件
# {
#     "api_key": "api_key_xxx",
#     "engine_name": "qwen-turbo",
#     "engine_name": "qwen-plus",
# }

# qianfan需要的配置文件
# {
#     "api_key": "api_key_xxx",
#     "api_secret":"api_key_secret"
#     "engine_name": "ERNIE-Bot",
#     "engine_name": "ERNIE-Bot-turbo",
# }

# zhipu需要的配置文件
# {
#     "api_key": "api_key_xxx",
#     "engine_name": "chatglm_turbo",
# }

# 对接外部agent


class llmAgentWorker(object):

    def __init__(self, request=None, user_info='', user_question={}, system_content="", messages="", query="", res_chat_id=0, engine_name="", output=[], output_all=[], custom_llm={}, azure_client=None, langchain_azure_client=None):
        self.request = request

        self.user_info = user_info

        # 原生问题
        self.user_question = user_question

        #
        self.system_content = system_content
        self.messages = messages

        # 拼装后的问题
        self.query = query

        # 会话id
        self.res_chat_id = res_chat_id

        # 使用引擎名称
        self.engine_name = engine_name

        # llm返回的数据经过提取后用于显示的内容
        self.output = output
        # llm返回的原生数据或请求异常信息
        self.output_all = output_all

        self.custom_llm = custom_llm

        # agent
        self.azure_client = azure_client

        # Df组件
        self.langchain_azure_client = langchain_azure_client

    # openai token 计算
    async def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = (
                4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            )
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            print(
                "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613."
            )
            return await self.num_tokens_from_messages(
                messages, model="gpt-3.5-turbo-0613"
            )
        elif "gpt-4" in model:
            print(
                "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
            )
            return await self.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    # 记录会话，等gpt处理后再依据返回更新该对话
    async def chat_add(self):

        chat_data = {}
        chat_data["engine"] = self.engine_name
        chat_data["chat_topic_id"] = self.request.ctx.chat_topic_id
        chat_data["input"] = self.user_question
        # chat_data["output"] = ""

        res = await chat_record_worker.chat_record_add(
            user_info=self.user_info, args={}, data=chat_data
        )

        self.res_chat_id = res.get("res_chat_id", 0)

        if self.request.ctx.chat_topic_id <= 0:
            self.request.ctx.chat_topic_id = res.get("res_chat_topic_id", 0)

    # 更新会话
    async def chat_up(self):
        chat_data = {}
        chat_data["output"] = "".join(self.output)
        chat_data["output_all"] = self.output_all

        await chat_record_worker.chat_record_update(
            user_info=self.user_info, res_chat_id=self.res_chat_id, data=chat_data
        )

    # 基础参数配置
    async def assistant_base(
        self, user_info, platform, engine_name, prompt_type, args, data
    ):

        # user_id = user_info.get("ID", 0)
        if (
            not isinstance(data, dict)
            or "user_content" not in data
            or "system_content" not in data
        ):
            raise BadRequestException(
                "INVALID_POST_DATA",
                f"{const.INVALID_PARAMETERS}, 缺失user_content或system_content参数",
            )

        #
        self.query = [{"role": "user", "content": data["user_content"]}]

        self.system_content = data["system_content"]

        if platform == "baidu" or platform == "zhipu":
            self.query = [
                {"role": "user", "content": self.system_content},
                {
                    "role": "assistant",
                    "content": "好的，后面的回复将按照你给我的角色和要求来解答",
                },
                {"role": "user", "content": data["question"]},
            ]

        # 获取配置
        data_info = {}
        # data_info["user_id"] = user_id
        data_info["platform"] = platform

        engine_config = {}

        if hasattr(config, "platforms"):
            res_config = config.platforms
            for _info in res_config:
                if _info.get("platform", "") == platform and _info.get("enable", False):

                    engine_config = copy.deepcopy(_info)

                    _engine_name = _info.get("engine_name", [])
                    if engine_name in _engine_name:
                        engine_config["engine_name"] = f"{engine_name}"
                    else:
                        engine_config["engine_name"] = ""

            if not engine_config.get("enable", False):
                raise BadRequestException(
                    "INVALID_PARAMETERS",
                    f"{const.INVALID_PARAMETERS}, 平台: {platform} 未启用",
                )

        # print(engine_config, engine_config.get("engine_name"), engine_name)

        if engine_config.get("engine_name", "") != engine_name:
            raise BadRequestException(
                "INVALID_PARAMETERS",
                f"{const.INVALID_PARAMETERS}, 引用的引擎错误: {engine_name}",
            )

        # 检查配置项目
        if platform == "azure":
            for key in (
                "api_key",
                "api_type",
                "api_base",
                "api_version",
                "engine_name",
            ):
                if key not in engine_config or engine_config.get(f"{key}", "") == "":
                    raise BadRequestException(
                        "DATA_NOT_FOUND",
                        f"{const.DATA_NOT_FOUND}: 请确认{key}已经正确配置",
                    )

            # 组件
            if prompt_type == "langchain":
                self.langchain_azure_client = AzureChatOpenAI(
                    azure_endpoint=engine_config.get("api_base"),
                    deployment_name=engine_config.get("engine_name"),
                    openai_api_version=engine_config.get("api_version"),
                    openai_api_type=engine_config.get("api_type"),
                    openai_api_key=engine_config.get("api_key"),
                )
            else:
                self.azure_client = AsyncAzureOpenAI(
                    api_key=engine_config.get("api_key"),
                    api_version=engine_config.get("api_version"),
                    azure_endpoint=engine_config.get("api_base"),
                )

            self.engine_name = engine_config.get("engine_name")

        elif platform == "openai":
            for key in ("api_key", "engine_name"):
                if key not in engine_config or engine_config.get(f"{key}", "") == "":
                    raise BadRequestException(
                        "DATA_NOT_FOUND",
                        f"{const.DATA_NOT_FOUND}: 请确认{key}已经正确配置",
                    )

            openai.api_key = engine_config.get("api_key")
            self.engine_name = engine_config.get("engine_name")

        elif platform == "aliyun":
            for key in ("api_key", "engine_name"):
                if key not in engine_config or engine_config.get(f"{key}", "") == "":
                    raise BadRequestException(
                        "DATA_NOT_FOUND",
                        f"{const.DATA_NOT_FOUND}: 请确认{key}已经正确配置",
                    )

            dashscope.api_key = engine_config.get("api_key")
            self.engine_name = engine_config.get("engine_name")

        elif platform == "baidu":
            for key in ("api_key", "api_secret", "engine_name"):
                if key not in engine_config or engine_config.get(f"{key}", "") == "":
                    raise BadRequestException(
                        "DATA_NOT_FOUND",
                        f"{const.DATA_NOT_FOUND}: 请确认{key}已经正确配置",
                    )

            qianfan.AK(engine_config.get("api_key"))
            qianfan.SK(engine_config.get("api_secret"))
            self.engine_name = engine_config.get("engine_name")

        elif platform == "zhipu":
            for key in ("api_key", "engine_name"):
                if key not in engine_config or engine_config.get(f"{key}", "") == "":
                    raise BadRequestException(
                        "DATA_NOT_FOUND",
                        f"{const.DATA_NOT_FOUND}: 请确认{key}已经正确配置",
                    )

            zhipuai.api_key = engine_config.get("api_key")
            self.engine_name = engine_config.get("engine_name")

        elif platform == "custom_llm":
            for key in (
                "api_key",
                "api_type",
                "api_base",
                "api_version",
                "engine_name",
            ):
                if key not in engine_config or engine_config.get(f"{key}", "") == "":
                    raise BadRequestException(
                        "DATA_NOT_FOUND",
                        f"{const.DATA_NOT_FOUND}: 请确认{key}已经正确配置",
                    )

            custom_llm_config = {}
            custom_llm_config["api_key"] = engine_config.get("api_key")
            custom_llm_config["api_type"] = engine_config.get("api_type")
            custom_llm_config["api_base"] = engine_config.get("api_base")
            custom_llm_config["api_version"] = engine_config.get("api_version")
            custom_llm_config["api_url"] = engine_config.get("api_url")

            self.custom_llm = custom_llm_config
            self.engine_name = engine_config.get("engine_name")
        else:
            raise BadRequestException(
                "INVALID_PARAMETERS",
                f"{const.INVALID_PARAMETERS}, 模型所在平台名称错误",
            )
        #
        self.user_info = user_info
        self.user_question = json.dumps(data)

        # 消息

        # self.messages = [{'role': 'user', 'content': 'Count to 1000, with a comma between each number and no newlines. E.g., 1, 2, 3, ...'}]

        self.messages = [{"role": "system", "content": self.system_content}, *self.query]

        if platform == "baidu" or platform == "zhipu":
            self.messages = [*self.query]

        if platform == "custom_llm":
            self.messages = {"messages": self.messages}

        conv_history_tokens = 0
        if platform == "azure" or platform == "openai":
            try:
                conv_history_tokens = await self.num_tokens_from_messages(self.messages)
            except Exception as e:
                raise BadRequestException(
                    "FAIL", f"{const.FAIL}: 计算token数量错误: {e}"
                )

        elif platform == "aliyun":

            response_token = dashscope.Tokenization.call(
                model=self.engine_name, messages=self.messages
            )
            if response_token.status_code != HTTPStatus.OK:
                raise BadRequestException(
                    "FAIL", f"{const.FAIL}: 计算token数量错误: {response_token.message}"
                )

            usage = response_token.usage

            conv_history_tokens = usage.get("input_tokens", 0)

        print(conv_history_tokens)
        # 记录会话
        await self.chat_add()

    # 流处理

    async def assistant_stream(
        self, user_info, platform, engine_name, prompt_type, args, data
    ):

        # 校验
        await self.assistant_base(user_info, platform, engine_name, prompt_type, args, data)

        # 开始时间
        working_start_time = datetime.datetime.now()

        if platform == "azure" or platform == "openai":
            try:
                if platform == "azure":
                    response = await self.azure_client.chat.completions.create(
                        model=self.engine_name, messages=self.messages, stream=True
                    )
                else:
                    response = await openai.ChatCompletion.acreate(
                        engine=self.engine_name, messages=self.messages, stream=True
                    )

            except Exception as e:
                raise BadRequestException("APP_ERROR", const.APP_ERROR, f"{e}")

            output = []
            output_all = []

            async def generate_data(output, output_all):

                async for item in response:
                    item_json = json.loads(item.model_dump_json(indent=2))
                    # print(item_json)
                    # 结束时间
                    working_end_time = datetime.datetime.now()

                    all_time = (
                        working_end_time.timestamp() - working_start_time.timestamp()
                    )

                    # msg = f"用户: {self.user_info.get('ID', 0)} 请求gpt开始时间: {working_start_time}, 结束时间: {working_end_time}, 共耗时: {all_time} 秒,返回信息: {item}"
                    msg = {}
                    msg["user_id"] = self.user_info.get("ID", 0)
                    msg["start_time"] = f"{working_start_time}"
                    msg["end_time"] = f"{working_end_time}"
                    msg["all_time"] = all_time
                    msg["return"] = item_json

                    output_all.append(msg)

                    content = ""
                    if "choices" in item_json:
                        choices = item_json["choices"]
                        if choices:
                            delta = choices[0].get("delta", {})
                            if "content" in delta:
                                delta_content = delta.get("content", None)
                                if delta_content is not None:
                                    content = delta_content

                    output.append(f"{content}")

                    yield content

                # 写入
                self.output = output
                self.output_all = output_all
                await self.chat_up()

            return generate_data(output, output_all)

        elif platform == "aliyun":
            try:

                responses = dashscope.Generation.call(
                    model=self.engine_name,  # Generation.Models.qwen_turbo,
                    messages=self.messages,
                    result_format="message",
                    stream=True,
                    incremental_output=True,
                )
            except Exception as e:
                raise BadRequestException("APP_ERROR", const.APP_ERROR, f"{e}")

            # 定义迭代器

            output = []
            output_all = []

            async def generate_data(output, output_all):
                for response in responses:
                    # 结束时间
                    working_end_time = datetime.datetime.now()

                    all_time = (
                        working_end_time.timestamp() - working_start_time.timestamp()
                    )

                    # msg = f"用户: {self.user_info.get('ID', 0)} 请求gpt开始时间: {working_start_time}, 结束时间: {working_end_time}, 共耗时: {all_time} 秒,返回信息: {response}"
                    msg = {}
                    msg["user_id"] = self.user_info.get("ID", 0)
                    msg["start_time"] = f"{working_start_time}"
                    msg["end_time"] = f"{working_end_time}"
                    msg["all_time"] = all_time
                    msg["return"] = response

                    output_all.append(msg)

                    content = ""
                    if response.status_code == HTTPStatus.OK:
                        # print(response)
                        item = response.output
                        if item["choices"]:
                            delta = item["choices"][0].get("message", {})
                            if "content" in delta:
                                content = delta.get("content", "")
                    else:
                        content = response.message
                        # content = '流式返回错误: 请求id: %s, 状态码: %s, 错误码: %s, 错误信息: %s' % (response.request_id, response.status_code, response.code, response.message)

                    output.append(f"{content}")
                    yield content

                # 写入
                self.output = output
                self.output_all = output_all
                await self.chat_up()

            return generate_data(output, output_all)

        elif platform == "baidu":

            try:
                chat_comp = qianfan.ChatCompletion()
                # 指定特定模型
                response = await chat_comp.ado(
                    model=self.engine_name, messages=self.messages, stream=True
                )

            except Exception as e:
                raise BadRequestException("APP_ERROR", const.APP_ERROR, f"{e}")

            # 定义迭代器
            output = []
            output_all = []

            async def generate_data(output, output_all):
                async for item in response:
                    # 结束时间
                    working_end_time = datetime.datetime.now()

                    all_time = (
                        working_end_time.timestamp() - working_start_time.timestamp()
                    )

                    # msg = f"用户: {self.user_info.get('ID', 0)} 请求gpt开始时间: {working_start_time}, 结束时间: {working_end_time}, 共耗时: {all_time} 秒,返回信息: {item}"

                    msg = {}
                    msg["user_id"] = self.user_info.get("ID", 0)
                    msg["start_time"] = f"{working_start_time}"
                    msg["end_time"] = f"{working_end_time}"
                    msg["all_time"] = all_time
                    msg["return"] = item

                    output_all.append(msg)

                    content = ""

                    if item.get("code", 0) == HTTPStatus.OK:

                        content = item.get("result", "")
                    else:
                        # msg = '返回错误: 请求id: %s, 状态码: %s, 错误信息: %s' % (item.get('id', ''), item.get('code', 0), item.get('result', ''))
                        content = item.get("result", "")

                    output.append(f"{content}")
                    yield content

                # 写入
                self.output = output
                self.output_all = output_all
                await self.chat_up()

            return generate_data(output, output_all)

        elif platform == "zhipu":

            try:
                response = zhipuai.model_api.sse_invoke(
                    model=self.engine_name, prompt=self.messages
                )

            except Exception as e:
                raise BadRequestException("APP_ERROR", const.APP_ERROR, f"{e}")

            # 定义迭代器
            output = []
            output_all = []

            async def generate_data(output, output_all):

                for event in response.events():

                    # 结束时间
                    working_end_time = datetime.datetime.now()

                    all_time = (
                        working_end_time.timestamp() - working_start_time.timestamp()
                    )

                    # msg = f"用户: {self.user_info.get('ID', 0)} 请求gpt开始时间: {working_start_time}, 结束时间: {working_end_time}, 共耗时: {all_time} 秒,返回信息: "
                    msg = {}
                    msg["user_id"] = self.user_info.get("ID", 0)
                    msg["start_time"] = f"{working_start_time}"
                    msg["end_time"] = f"{working_end_time}"
                    msg["all_time"] = all_time

                    content = ""
                    if event.event == "add":
                        content = event.data
                        # msg += f"{content}"
                        msg["return"] = content
                    elif event.event == "error" or event.event == "interrupted":
                        content = event.data
                        # msg += f"{content}"
                        msg["return"] = content
                    elif event.event == "finish":
                        content = event.data
                        # msg += f"{content}, meta:{event.meta}"
                        msg["return"] = content
                        msg["return_meta"] = event.meta
                    else:
                        content = event.data
                        # msg += f"{content}"
                        msg["return"] = content

                    output_all.append(msg)

                    output.append(f"{content}")
                    yield content

                # 写入
                self.output = output
                self.output_all = output_all
                await self.chat_up()

            return generate_data(output, output_all)

        elif platform == "custom_llm":

            lcuuid = generate_uuid()
            headers = {
                "BCS-APIHub-RequestId": lcuuid,
                "X-CHJ-GWToken": self.custom_llm["api_key"],
            }
            url = self.custom_llm["api_url"]
            try:
                response = curl_tools.curl_app_stream(
                    "post", url, headers, json.dumps(self.messages)
                )
            except BadRequestException as e:
                raise BadRequestException(
                    "APP_ERROR", f"{const.APP_ERROR}:{e.message}", f"{e}"
                )

            output = []
            output_all = []

            async def generate_data(output, output_all):
                async for chunked in response:
                    line = chunked.decode("utf-8").strip()
                    # 找到包含"data:"的部分并提取"data"字段的值
                    event_data = ""
                    if line.startswith("data:"):
                        data_start = len("data:")
                        data_value = line[data_start:].strip()
                        if data_value != "[DONE]":
                            # 解析JSON格式的数据
                            try:
                                event_data = json.loads(data_value)
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON:{e}")
                                event_data = data_value

                    # 结束时间
                    working_end_time = datetime.datetime.now()

                    all_time = (
                        working_end_time.timestamp() - working_start_time.timestamp()
                    )

                    # msg = f"用户: {self.user_info.get('ID', 0)} 请求gpt开始时间: {working_start_time}, 结束时间: {working_end_time}, 共耗时: {all_time} 秒,返回信息: {item}"
                    msg = {}
                    msg["user_id"] = self.user_info.get("ID", 0)
                    msg["start_time"] = f"{working_start_time}"
                    msg["end_time"] = f"{working_end_time}"
                    msg["all_time"] = all_time
                    msg["return"] = line

                    output_all.append(msg)

                    content = ""
                    if event_data or isinstance(event_data, dict):

                        if event_data.get("code", 0) != 0 or "data" not in event_data:
                            content = event_data.get("msg", "")
                        else:
                            data = event_data["data"]
                            if data["choices"]:
                                choices = data["choices"][0]
                                if isinstance(choices, dict):
                                    content = choices.get("content", "")

                            output.append(f"{content}")

                    yield content

                # 写入
                self.output = output
                self.output_all = output_all
                await self.chat_up()

            return generate_data(output, output_all)


llm_agent_worker = llmAgentWorker()
