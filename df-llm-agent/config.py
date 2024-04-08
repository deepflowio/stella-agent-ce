import sys
import traceback

from utils.file_read_tools import file_read_tools
import const


class Config(object):

    def __init__(self, _yml=None):
        try:
            if not _yml:
                yml = file_read_tools.yaml_read(const.YML_FILE)
            else:
                yml = _yml

            self.daemon = yml.get('daemon', True)
            self.api_timeout = yml.get('api_timeout', 500)
            self.sql_show = yml.get('sql_show', False)
            self.log_file = yml.get('log_file', "/var/log/web_all.log")
            self.log_level = yml.get('log_level', 'info')

            self.app_key = None

            self.instance_path = yml.get('instance_path', None)

            redis = yml.get('redis', {})
            mysql = yml.get('mysql', {})

            self.redis_cluster = redis.get('cluster_enabled', False)
            self.redis_host = redis.get('host', '127.0.0.1')
            self.redis_port = redis.get('port', 6379)
            self.redis_db = redis.get('db', 7)
            self.redis_password = redis.get('password', 'password123')

            self.mysql_user_name = mysql.get('user_name', 'root')
            self.mysql_user_password = mysql.get('user_password', 'password123')
            self.mysql_host = mysql.get('host', '127.0.0.1')
            self.mysql_port = mysql.get('port', 20130)
            self.mysql_database = mysql.get('database', 'deepflow_llm')

            ai = yml.get('ai', {})
            if ai:
                enable = ai.get('enable', False)
                if enable:
                    self.platforms = ai.get('platforms', [])

        except Exception as e:
            traceback.print_exc()
            print("配置文件解析错误: %s" % e)
            sys.exit(1)


config = Config()
