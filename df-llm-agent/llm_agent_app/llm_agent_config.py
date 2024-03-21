from exception import BadRequestException
import const
import json
from database import db_models
from utils import logger

log = logger.getLogger(__name__)


# agent配置
class llmAgentConfigWorker(object):

    # 校验数据
    @staticmethod
    async def verify_data(data):
        pass

    # 新增
    @classmethod
    async def llm_agent_config_add(cls, user_info, args, data):
        user_id = user_info.get("ID", 0)
        user_type = user_info.get("TYPE", 0)
        if user_type != 1:
            raise BadRequestException("SERVER_ERROR", f"{const.SERVER_ERROR}, 没有权限，只允许超管")

        data_info = {}
        data_info["user_id"] = user_id
        data_info["platform"] = data.get("platform", "")
        data_info["model"] = data.get("model", "")
        data_info["model_info"] = data.get("model_info", "")
        data_info["key"] = data.get("key_name", "")
        data_info["value"] = data.get("value", "")

        # 其他key必须唯一
        # todoing key 需要给范围
        if data_info["key"] != "engine_name":

            raise BadRequestException("INVALID_PARAMETERS", f"{const.INVALID_PARAMETERS}, 只允许添加模型引擎配置")
            # where_info = {}
            # where_info = {}
            # where_info["user_id"] = user_id
            # where_info["platform"] = data_info["platform"]
            # where_info["key"] = data_info["key"]

            # res = await db_models.LlmConfig.exists(**where_info)

            # if res:
            #     raise BadRequestException("INVALID_PARAMETERS", f"{const.INVALID_PARAMETERS}, 该配置项在一个平台下必须唯一")

        try:
            await db_models.LlmConfig.create(**data_info)
        except Exception as e:
            raise BadRequestException("SQL_ERROR", const.SQL_ERROR, f"{e}")

        log.info(f"用户：{user_id}, 添加配置, 数据: {data_info}")

        return True

    # 获取所有配置
    @classmethod
    async def llm_agent_config_list(cls, user_info, platform=""):
        # user_id = user_info.get("ID", 0)
        data_info = {}
        # data_info["user_id"] = user_id

        if platform:
            data_info["platform"] = platform

        try:
            if data_info:
                sql_res = await db_models.LlmConfig.filter(**data_info).all()
            else:
                sql_res = await db_models.LlmConfig.all()
        except Exception as e:
            raise BadRequestException("SQL_ERROR", const.SQL_ERROR, f"{e}")

        res = {}
        for v in sql_res:
            _config = dict(v)

            _platform = _config.get("platform")
            _model = _config.get("model")
            _model_info = _config.get("model_info")

            _key = _config.get("key")
            _value = _config.get("value")

            # 列表过滤敏感数据，详情不过滤
            if platform == "":
                if _key not in ["enable", "engine_name"]:
                    continue

            _merge_config = {}
            _merge_config["model"] = _model
            _merge_config["model_info"] = _model_info

            if f"{_key}" == "engine_name":
                _merge_config[f"{_key}"] = [_value]
            else:
                _merge_config[f"{_key}"] = _value

            if _platform not in res:
                res[f"{_platform}"] = _merge_config
            else:
                if f"{_key}" == "engine_name":
                    if f"{_key}" not in res[f"{_platform}"]:
                        res[f"{_platform}"][f"{_key}"] = [_value]
                    else:
                        res[f"{_platform}"][f"{_key}"] += [_value]
                else:
                    res[f"{_platform}"][f"{_key}"] = _value

        return res

    # 更新
    @classmethod
    async def llm_agent_config_update(cls, user_info, platform, key_name, args, data):
        user_id = user_info.get("ID", 0)
        user_type = user_info.get("TYPE", 0)
        if user_type != 1:
            raise BadRequestException("SERVER_ERROR", f"{const.SERVER_ERROR}, 没有权限，只允许超管")

        if not platform or not key_name:
            raise BadRequestException("INVALID_PARAMETERS", f"{const.INVALID_PARAMETERS}, 缺失平台名或key")

        # engine可以删除和新增。修改意义不大
        if key_name == "engine_name":
            raise BadRequestException("INVALID_PARAMETERS", f"{const.INVALID_PARAMETERS}, 引擎值不支持修改")

        where_info = {}
        where_info["user_id"] = user_id
        where_info["platform"] = platform
        where_info["key"] = key_name

        data_info = {}
        data_info["value"] = data.get("value", "")

        try:
            res = await db_models.LlmConfig.get(**where_info)
            if res:
                await db_models.LlmConfig.filter(**where_info).update(**data_info)
            else:
                raise BadRequestException("DATA_NOT_FOUND", const.DATA_NOT_FOUND)

        except Exception as e:
            raise BadRequestException("SQL_ERROR", const.SQL_ERROR, f"{e}")

        log.info(f"用户：{user_id}, 更新配置, 数据: {data_info}")

        return True

    # 删除
    @classmethod
    async def llm_agent_config_delete(cls, user_info, platform, engine_name, args, data):
        user_id = user_info.get("ID", 0)
        user_type = user_info.get("TYPE", 0)
        if user_type != 1:
            raise BadRequestException("SERVER_ERROR", f"{const.SERVER_ERROR}, 没有权限，只允许超管")

        where_info = {}
        where_info["user_id"] = user_id
        where_info["platform"] = platform
        where_info["key"] = "engine_name"
        where_info["value"] = engine_name

        # 其他配置不允许删除，只有引擎可以
        try:
            llm_config_exist = await db_models.LlmConfig.filter(**where_info).count()
        except Exception as e:
            raise BadRequestException("SQL_ERROR", const.SQL_ERROR, f"{e}")

        if llm_config_exist > 0:
            await db_models.LlmConfig.filter(**where_info).delete()
        else:
            raise BadRequestException("DATA_NOT_FOUND", const.DATA_NOT_FOUND)

        log.info(f"用户：{user_id}, 删除配置, 查询数据: {where_info}")
        return True


llm_agent_config_worker = llmAgentConfigWorker()
