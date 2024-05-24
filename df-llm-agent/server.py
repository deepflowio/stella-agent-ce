from sanic import Sanic
from sanic_cors import CORS
from sanic import HTTPResponse
from sanic.worker.manager import WorkerManager
from sanic.exceptions import Unauthorized, NotFound, Forbidden, ServerError
from sanic.response import json as json_response
from utils import common
from data import init_db, close_db
from chat_record_app.app import chat_record_app
from llm_agent_app.app import llm_agent_app
from health_app.app import health_app
from resource_app.app import resource_app
import traceback
from utils import logger

app = Sanic("df-llm-agent")

app.config.CORS_ORIGINS = "*"
app.config.CORS_AUTOMATIC_OPTIONS = True
app.config.RESPONSE_TIMEOUT = 500

app.blueprint(health_app)
app.blueprint(llm_agent_app)
app.blueprint(chat_record_app)
app.blueprint(resource_app)

CORS(app)

WorkerManager.THRESHOLD = 600

log = logger.getLogger(__name__)


@app.middleware("request")
async def run_before_handler(request):
    req_headers = dict(request.headers)
    # req_path = request.path

    if request.method.lower() == 'options':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*',
        }
        return HTTPResponse('', headers=headers)

    current_dict = {}
    current_dict['ID'] = "1"
    current_dict['TYPE'] = "1"

    request.ctx.user = current_dict

    request.ctx.chat_topic_id = int(req_headers.get("x-chat-topic-id", 0))


@app.listener("before_server_start")
async def init_orm(app, loop):
    await init_db()


@app.listener("after_server_stop")
async def close_orm(app, loop):
    await close_db()


@app.middleware("response")
async def custom_banner(request, response):

    if hasattr(request.ctx, 'chat_topic_id'):
        response.headers["X-chat-topic-id"] = int(request.ctx.chat_topic_id)


@app.exception(Unauthorized)
async def Not_Unauthorized(request, exception):
    traceback.print_exc()
    resp = await common.falseReturn("SERVER_ERROR", "系统错误", f"{exception}")
    status = 400

    return json_response(resp, status=status)


@app.exception(NotFound)
async def Not_Found(request, exception):
    traceback.print_exc()
    resp = await common.falseReturn("SERVER_ERROR", "系统错误", f"{exception}")
    status = 400
    return json_response(resp, status=status)


@app.exception(Forbidden)
async def Not_Forbidden(request, exception):
    traceback.print_exc()
    resp = await common.falseReturn("SERVER_ERROR", "系统错误", f"{exception}")
    status = 400

    return json_response(resp, status=status)


@app.exception(ServerError)
async def Not_ServerError(request, exception):
    traceback.print_exc()
    resp = await common.falseReturn("SERVER_ERROR", "系统错误", f"{exception}")
    status = 500

    return json_response(resp, status=status)
