import asyncio
import aiohttp
import json
from exception import BadRequestException
import const
from config import config
import time
from utils import logger

log = logger.getLogger(__name__)


class curlTools(object):

    @classmethod
    async def curl_app(cls, method, url, headers, data=None, params=None):

        async with aiohttp.ClientSession() as session:
            try:
                _headers = headers_base = {}
                # 默认header
                headers_base['content-type'] = 'application/json'

                if headers:
                    _headers = {**headers_base, **headers}

                # 如果content-type = application/json，data 必须为json.dumps()后的数据
                # 如果content-type = application/x-www-form-urlencoded，直接传dict
                # params dict格式

                async with getattr(session, method)(url, timeout=config.api_timeout, headers=_headers, data=data, params=params) as r:
                    response = await r.read()
                    response = json.loads(response)
                    status_code = r.status

            except asyncio.TimeoutError as e:
                raise BadRequestException('APP_TIMEOUT', f"{const.APP_TIMEOUT}: {e}")
            except Exception as e:
                raise BadRequestException('APP_ERROR', f"{const.APP_ERROR}: {e}")

            return response, status_code

    @classmethod
    async def curl_app_stream(cls, method, url, headers, data=None, params=None):

        async with aiohttp.ClientSession() as session:
            try:
                _headers = headers_base = {}
                # 默认header
                headers_base['content-type'] = 'application/json'

                if headers:
                    _headers = {**headers_base, **headers}

                async with getattr(session, method)(url, timeout=config.api_timeout, headers=_headers, data=data, params=params) as resp:
                    while True:
                        chunk = await resp.content.readline()
                        if not chunk:
                            break
                        yield chunk
            except asyncio.TimeoutError as e:
                raise BadRequestException('APP_TIMEOUT', f"{const.APP_TIMEOUT}: {e}")
            except Exception as e:
                raise BadRequestException('APP_ERROR', f"{const.APP_ERROR}: {e}")


curl_tools = curlTools()
