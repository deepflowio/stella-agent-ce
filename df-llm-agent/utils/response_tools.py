from sanic.response import HTTPResponse, ResponseStream
from sanic.response import text as s_text_response
from sanic.response import json as s_json_response
from tortoise.models import ModelMeta
from functools import wraps
from utils.exception_tools import exception_decorate
from utils import common
import json
from datetime import datetime
import const


class LCJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        # Datetime class
        if isinstance(obj, datetime):
            return obj.strftime(const.DATE_PATTEN)

        elif isinstance(obj.__class__, ModelMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:

                if hasattr(obj, '_fillable') and obj._fillable \
                        and field not in obj._fillable:
                    continue

                if hasattr(obj, '_hidden') and obj._hidden\
                        and field in obj._hidden:
                    continue

                data = obj.__getattribute__(field)
                try:
                    if isinstance(data, datetime):
                        data = data.strftime(const.DATE_PATTEN)
                    # this will fail on non-encodable values, like other
                    # classes
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    continue

            return fields
        return json.JSONEncoder.default(self, obj)


# json格式化
async def json_response(data=None, status='SUCCESS'):
    resp = await common.trueReturn(data=data, status=status)

    return LCJSONEncoder().encode(resp)


#
def wrap_resp_stream(func):

    @wraps(func)
    @exception_decorate
    async def wrap_decorator(*args, **kwargs):
        res = await func(*args, **kwargs)
        # chat_res = []

        # async def sample_streaming_fn(response):

        #     async def chat_streaming_fn(response):
        #         async for chunk in res:
        #             chat_res.append(chunk)
        #             await response.write(f"{chunk}")

        #     print("~~~~~~~~~~")
        #     print(chat_res)
        #     return await chat_streaming_fn(response)
        # print("!!!!!!!!!")
        # print(chat_res)

        # return ResponseStream(sample_streaming_fn, content_type="text/plain; charset=utf-8")

        async def sample_streaming_fn(response):
            async for chunk in res:
                await response.write(f"{chunk}")
        return ResponseStream(sample_streaming_fn, content_type="text/plain; charset=utf-8")

        # return ResponseStream.stream(res())

    return wrap_decorator


# json
def wrap_resp(func):

    @wraps(func)
    @exception_decorate
    async def wrap_decorator(*args, **kwargs):
        resp = await func(*args, **kwargs)
        res = await json_response(resp)
        return HTTPResponse(res, content_type="application/json")

    return wrap_decorator
