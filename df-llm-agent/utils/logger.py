import sys
import logging
from logging import StreamHandler
from logging.handlers import SysLogHandler
from logging.handlers import TimedRotatingFileHandler

LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR,
}


class LoggerManager(object):

    LOGGER = logging.getLogger('root')

    def __init__(self, model_name, log_level, log_file):
        self.model_name = model_name
        self.log_level = LOG_LEVEL_MAP[log_level]
        self.log_file = log_file

    @property
    def syslog_handler(self):
        syslog_handler = SysLogHandler(address='/dev/log', facility=SysLogHandler.LOG_LOCAL2)
        syslog_handler.setFormatter(logging.Formatter(self.model_name + '/%(module)s: %(message)s'))
        return syslog_handler

    @property
    def file_handler(self):
        file_handler = TimedRotatingFileHandler(self.log_file, when='midnight', backupCount=365)
        file_handler.setFormatter(logging.Formatter('%(asctime)s T%(thread)d-%(threadName)s ' '%(levelname)s %(module)s.' '%(funcName)s.%(lineno)s: %(message)s'))
        return file_handler

    @property
    def stdout_handler(self):
        stdout_handler = StreamHandler(sys.stdout)
        stdout_handler.setFormatter(logging.Formatter('%(asctime)s T%(thread)d-%(threadName)s ' '%(levelname)s %(module)s.' '%(funcName)s.%(lineno)s: %(message)s'))
        return stdout_handler

    @classmethod
    def get_logger(cls, name='root'):
        return cls.LOGGER

    def init_logger(self):
        self.LOGGER.setLevel(self.log_level)
        self.LOGGER.addHandler(self.file_handler)
        # self.LOGGER.addHandler(self.syslog_handler)
        self.LOGGER.addHandler(self.stdout_handler)


def getLogger(name='root'):
    return LoggerManager.get_logger(name)
