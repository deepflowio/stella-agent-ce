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

log = logger.getLogger(__name__)


class chatRecordWorker(object):

    # 校验数据
    @staticmethod
    async def verify_data(data):
        pass

    # 对话记录
    # 新增
    # 调用agent前提前记录，output 默认为空，待agent返回数据后在更新该会话
    @classmethod
    async def chat_record_add(cls, user_info, args, data):

        user_id = user_info.get("ID", 0)

        # 如果不带主题id，先创建主题，主题名称截取input前255个字符
        chat_topic_id = data.get("chat_topic_id", 0)
        # 对话主题类型，暂时默认=1
        type = data.get("type", 1)

        input = data.get("input", "")
        output = data.get("output", "")

        # 对话用的llm引擎
        engine = data.get("engine", "")

        try:
            # 有主题id
            if chat_topic_id > 0:

                where_chat_topic_info = {}
                where_chat_topic_info["user_id"] = user_id
                where_chat_topic_info["id"] = chat_topic_id

                chat_topic_exist = await db_models.ChatTopic.filter(**where_chat_topic_info).count()

                # 主题存在
                if chat_topic_exist > 0:
                    chat_data_info = {}
                    chat_data_info["chat_topic_id"] = chat_topic_id
                    chat_data_info["input"] = input
                    chat_data_info["output"] = output
                    chat_data_info["engine"] = engine

                    res_chat = await db_models.Chat.create(**chat_data_info)

                    res_chat_id = res_chat.id
                else:
                    raise BadRequestException("DATA_NOT_FOUND", f"{const.DATA_NOT_FOUND}: 关联的主题不存在", f"{const.DATA_NOT_FOUND}: 关联的主题不存在")

            else:
                time_now = datetime.datetime.now().strftime(const.DATE_PATTEN)
                async with in_transaction() as connection:

                    # 创建主题
                    chat_topic_info = {}
                    chat_topic_info["user_id"] = user_id
                    chat_topic_info["name"] = f"会话-{time_now}"
                    chat_topic_info["type"] = type

                    res_chat_topic = await db_models.ChatTopic.create(using_db=connection, **chat_topic_info)

                    # 记录对话
                    chat_data_info = {}
                    chat_data_info["chat_topic_id"] = res_chat_topic.id
                    chat_data_info["input"] = input
                    chat_data_info["output"] = output
                    chat_data_info["engine"] = engine

                    res_chat = await db_models.Chat.create(using_db=connection, **chat_data_info)

                    # 返回主题id
                    chat_topic_id = res_chat_topic.id
                    res_chat_id = res_chat.id

            res = {"res_chat_topic_id": chat_topic_id, "res_chat_id": res_chat_id}

            log.info(f"用户：{user_id}, 添加对话记录, 信息: {res}")

            return res

        except BadRequestException as e:
            raise BadRequestException(e.status, e.message, e.err)

        except Exception as e:
            raise BadRequestException("SQL_ERROR", const.SQL_ERROR, f"{e}")

    # 更新
    # agent返回数据后调用更新会话
    @classmethod
    async def chat_record_update(cls, user_info, res_chat_id, data):

        user_id = user_info.get("ID", 0)
        where_info = {}
        where_info["id"] = res_chat_id

        data_info = {}
        data_info["output"] = data.get("output", [])
        data_info["output_all"] = data.get("output_all", [])
        data_info["updated_at"] = datetime.datetime.now().strftime(const.DATE_PATTEN)

        try:
            res = await db_models.Chat.get(**where_info)
            if res:
                await db_models.Chat.filter(**where_info).update(**data_info)
            else:
                raise Exception(f"{const.DATA_NOT_FOUND}")

        except Exception as e:
            log.error(f"用户：{user_id}, 更新会话失败: {e}, 待更新信息: {data}")
            raise BadRequestException("SQL_ERROR", const.SQL_ERROR, f"{e}")
        else:
            log.info(f"用户：{user_id}, 更新会话")
        return True

    # 获取所有主题或某个主题下的所有对话
    @classmethod
    async def chat_record_list(cls, user_info, chat_topic_id=0):

        res_all = []
        try:
            # 某个主题下的对话列表
            if chat_topic_id > 0:

                where_chat_topic_info = {}
                where_chat_topic_info["user_id"] = user_info.get("ID", 0)
                where_chat_topic_info["id"] = chat_topic_id

                chat_topic_exist = await db_models.ChatTopic.filter(**where_chat_topic_info).count()

                # 主题存在，获取该主题下所有对话
                if chat_topic_exist > 0:
                    data_info = {}
                    data_info["chat_topic_id"] = chat_topic_id
                    res_chat = await db_models.Chat.filter(**data_info).all()

                    if res_chat:
                        # 获取所有对话id
                        chat_ids = []
                        for v in res_chat:
                            v_dict = dict(v)
                            chat_ids.append(v_dict["id"])

                        # 获取所有属于这些对话的评分
                        res_score_dict = {}
                        if chat_ids:
                            query = Q(obj_id__in=chat_ids) & Q(type=2)
                            res_score = await db_models.Score.filter(query).all()

                            for v in res_score:
                                v_dict = dict(v)
                                res_score_dict[v_dict["obj_id"]] = v_dict

                        # 所有对话加上获取到的评分
                        chat_list = []
                        for v in res_chat:
                            v_dict = dict(v)
                            chat_id = v_dict["id"]

                            if chat_id in res_score_dict:
                                v_dict["score"] = res_score_dict[chat_id]["score"]
                                v_dict["feedback"] = res_score_dict[chat_id]["feedback"]
                                v_dict["user_name"] = res_score_dict[chat_id]["user_name"]
                            else:
                                v_dict["score"] = ""
                                v_dict["feedback"] = ""
                                v_dict["user_name"] = ""

                            chat_list.append(v_dict)

                        # 赋值
                        res_all = chat_list

                else:
                    raise BadRequestException("DATA_NOT_FOUND", f"{const.DATA_NOT_FOUND}: 关联的主题不存在", f"{const.DATA_NOT_FOUND}: 关联的主题不存在")
            else:
                # 所有主题
                data_info = {}
                data_info["user_id"] = user_info.get("ID", 0)
                res_chat_topic = await db_models.ChatTopic.filter(**data_info).all()

                # 主题存在
                if res_chat_topic:
                    # 获取所有主题id
                    chat_topic_ids = []
                    for v in res_chat_topic:
                        v_dict = dict(v)
                        chat_topic_ids.append(v_dict["id"])

                    # 获取所有属于这些对话的评分
                    res_score_dict = {}
                    if chat_topic_ids:
                        query = Q(obj_id__in=chat_topic_ids) & Q(type=1)
                        res_score = await db_models.Score.filter(query).all()

                        for v in res_score:
                            v_dict = dict(v)
                            res_score_dict[v_dict["obj_id"]] = v_dict

                    # 所有主题加上获取到的评分
                    chat_topic_list = []
                    for v in res_chat_topic:
                        v_dict = dict(v)
                        chat_id = v_dict["id"]

                        if chat_id in res_score_dict:
                            v_dict["score"] = res_score_dict[chat_id]["score"]
                            v_dict["feedback"] = res_score_dict[chat_id]["feedback"]
                            v_dict["user_name"] = res_score_dict[chat_id]["user_name"]
                        else:
                            v_dict["score"] = ""
                            v_dict["feedback"] = ""
                            v_dict["user_name"] = ""

                        chat_topic_list.append(v_dict)

                    # 赋值
                    res_all = chat_topic_list

        except BadRequestException as e:
            raise BadRequestException(e.status, e.message, e.err)

        except Exception as e:
            traceback.print_exc()
            raise BadRequestException("SQL_ERROR", const.SQL_ERROR, f"{e}")

        return res_all

    # 评分
    # 新增
    @classmethod
    async def chat_record_score_add(cls, user_info, args, data, chat_topic_id, chat_id):

        user_id = user_info.get("ID", 0)

        data_info = {}
        data_info["user_id"] = user_id
        data_info["score"] = data.get("score", 0)
        data_info["feedback"] = data.get("feedback", '')
        data_info["user_name"] = data.get("user_name", '')

        try:

            if not isinstance(data_info["score"], int) or data_info["score"] < 0 or data_info["score"] > 100:
                raise BadRequestException("INVALID_POST_DATA", f"{const.INVALID_POST_DATA}: 评分值错误")

            if data_info["feedback"] == "" or data_info["user_name"] == "":
                raise BadRequestException("INVALID_POST_DATA", f"{const.INVALID_POST_DATA}: 反馈内容和用户不能为空")

            # 主题存在与否
            where_chat_topic_info = {}
            where_chat_topic_info["user_id"] = user_id
            where_chat_topic_info["id"] = chat_topic_id
            chat_topic_exist = await db_models.ChatTopic.filter(**where_chat_topic_info).count()

            # 不存在
            if chat_topic_exist <= 0:
                raise BadRequestException("DATA_NOT_FOUND", f"{const.DATA_NOT_FOUND}: 主题不存在")

            # 对话id
            if chat_id > 0:
                # 对话存在与否
                where_chat_info = {}
                where_chat_info["id"] = chat_id
                where_chat_info["chat_topic_id"] = chat_topic_id
                chat_exist = await db_models.Chat.filter(**where_chat_info).count()

                # 不存在
                if chat_exist <= 0:
                    raise BadRequestException("DATA_NOT_FOUND", f"{const.DATA_NOT_FOUND}: 对话不存在")

                data_info["type"] = 2
                data_info["obj_id"] = chat_id
            else:
                data_info["type"] = 1
                data_info["obj_id"] = chat_topic_id

            log.info(f"用户：{user_id}, 添加评分,数据: {data_info}")

        except BadRequestException as e:
            raise BadRequestException(e.status, e.message, e.err)

        try:
            await db_models.Score.create(**data_info)
        except Exception as e:
            raise BadRequestException("SQL_ERROR", const.SQL_ERROR, f"{e}")

        return True


chat_record_worker = chatRecordWorker()
