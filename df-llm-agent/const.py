# df-llm-agent

HOST = "0.0.0.0"
PORT = 20831

WORKER_NUMBER = 10
YML_FILE = "/etc/web/df-llm-agent.yaml"

# API
API_VERSION = "v1"
API_PREFIX = "/" + API_VERSION

# http
JSON_TYPE = "application/json; charset=utf-8"

# 错误码
SUCCESS = "成功"
FAIL = "失败"
SERVER_ERROR = "系统错误"

APP_ERROR = "APP返回错误"
APP_TIMEOUT = "APP请求超时"

SQL_ERROR = "SQL错误"

INVALID_PARAMETERS = "参数格式错误"
INVALID_POST_DATA = "数据格式错误"
JSON_FORMAT_ERR = "json格式错误"

DATA_NOT_FOUND = "数据不存在"
DATA_IN_USE = "数据被使用"

# 状态码
HTTP_OK = 200
HTTP_PARTIAL_RESULT = 206
HTTP_BAD_REQUEST = 400
HTTP_ACCESSDENIED = 403
HTTP_NOT_FOUND = 404
HTTP_NOT_ALLOWED = 405
HTTP_INTERNAL_SERVER_ERROR = 500

DATE_PATTEN = "%Y-%m-%d %H:%M:%S"
