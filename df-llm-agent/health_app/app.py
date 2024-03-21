# -*- coding: utf-8 -*-
from sanic import Blueprint
from sanic.response import json as sanic_json
from const import API_PREFIX

health_app = Blueprint("health", url_prefix=API_PREFIX)


@health_app.route('/health/', methods=['GET', 'HEAD'])
async def health_get_api(request):
    return sanic_json({}, content_type='application/json; charset=utf-8', status=200)
