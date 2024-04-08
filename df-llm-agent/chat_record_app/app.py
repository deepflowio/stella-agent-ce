from sanic import Blueprint
from chat_record_app.worker import app_worker
from utils.response_tools import wrap_resp
from const import API_PREFIX

chat_record_app = Blueprint("chat_record", url_prefix=API_PREFIX)

#
# 对话必须属于一个主题和用户
#

# 对话记录


# 新增对话记录(通过请求gpt时自动写入，不再提供接口)
# @chat_record_app.route("/chat_record", methods=["POST"])
# @wrap_resp
# async def chat_record_add(request):
#     worker = app_worker(request)
#     # 参数如果不带主题id，先创建主题
#     res = await worker.chat_record_add()
#     return res


# 获取所有主题，或一个主题下的所有对话，并带上评分（如果存在）
@chat_record_app.route("/chat_record", name="chat_record_list_all")
@chat_record_app.route("/chat_record/<id:int>")
@wrap_resp
async def chat_record_list11(request, id=0):
    worker = app_worker(request)
    res = await worker.chat_record_list(id)
    return res


# 对当前用户下的单次对话或一个主题评分


# 对单次对话评分或一个主题评分
@chat_record_app.route("/chat_record/score/<chat_topic_id:int>", methods=["POST"], name="chat_record_score_to_topic")
@chat_record_app.route("/chat_record/score/<chat_topic_id:int>/<chat_id:int>", methods=["POST"])
@wrap_resp
async def chat_record_score_add(request, chat_topic_id=0, chat_id=0):
    worker = app_worker(request)
    res = await worker.chat_record_score_add(chat_topic_id, chat_id)
    return res
