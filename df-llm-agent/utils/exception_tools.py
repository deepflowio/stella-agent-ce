from functools import wraps
from sanic.response import json as json_response
from schematics.exceptions import ModelConversionError, ModelValidationError
import traceback

import const
from exception import BadRequestException, NotFoundException, AccessDeniedException, MethodNotAllowedException, SQLException
from utils import common


def exception_decorate(func):

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            response = await func(*args, **kwargs)
            return response
        except (ModelConversionError, ModelValidationError) as error:

            resp = await common.falseReturn("FAIL", "Model转换或校验失败", f"{error}")
            status = const.HTTP_BAD_REQUEST

        except (BadRequestException, NotFoundException, AccessDeniedException, MethodNotAllowedException, SQLException) as error:
            traceback.print_exc()
            resp = await common.falseReturn(error.status, error.message, f"{error.err}")
            status = error.status_code

        except Exception as error:
            traceback.print_exc()
            resp = await common.falseReturn("SERVER_ERROR", "系统错误", f"{error}")
            status = const.HTTP_INTERNAL_SERVER_ERROR
        return json_response(resp, status=status)

    return wrapper
