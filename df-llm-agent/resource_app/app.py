from sanic import Blueprint
from resource_app.worker import app_worker
from utils.response_tools import wrap_resp
from const import API_PREFIX

resource_app = Blueprint("resource", url_prefix=API_PREFIX)


# 获取文件
@resource_app.route("/img/<hash_name:str>", name="resource_get")
@wrap_resp
async def img_get(request, hash_name=""):
    worker = app_worker(request)
    res = await worker.img_get(hash_name)
    return res


# 提交文件
@resource_app.route("/imgs", methods=["POST"], name="resource_add")
@wrap_resp
async def img_add(request):
    worker = app_worker(request)
    res = await worker.img_add()
    return res


# 提交文件编码
@resource_app.route("/imgs/b64", methods=["POST"], name="resource_add_b64")
@wrap_resp
async def img_add_b64(request):
    worker = app_worker(request)
    res = await worker.img_add_b64()
    return res
