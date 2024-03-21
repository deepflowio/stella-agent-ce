import yaml
import configparser


class fileReadTools(object):

    # yaml文件解析
    @classmethod
    def yaml_read(cls, YML_FILE):
        try:
            with open(YML_FILE, "r", encoding='utf-8') as y:
                yml = yaml.load(y, Loader=yaml.FullLoader)
            if not yml:
                print("yaml文件不存在")
                return {}
            return yml
        except Exception as e:
            print("yaml文件解析错误: %s" % e)
            return {}

    # conf文件解析
    @classmethod
    def config_parser(cls, config_file, selects=None):
        config_conf = configparser.ConfigParser()
        config_conf.read(config_file, encoding="utf-8")
        if selects:
            items_list = config_conf.items(selects)
            return dict(items_list)
        else:
            return config_conf


file_read_tools = fileReadTools()
