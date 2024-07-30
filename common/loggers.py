import logging
from logging.handlers import RotatingFileHandler

import wx

from settings.settings import log_level, log_path

logger = logging.getLogger()


class RealTimeLogHandler(logging.Handler):
    def __init__(self, text_ctrl):
        logging.Handler.__init__(self)
        formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')
        self.setFormatter(formatter)
        self.text_ctrl = text_ctrl

    def emit(self, record):
        message = self.format(record)
        # 安全地在UI主线程中更新TextCtrl
        wx.CallAfter(self.text_ctrl.AppendText, message + '\n')


def init_logger(create_ctrl=None):
    # global logger
    # logger = logging.getLogger()
    log_handler = RealTimeLogHandler(create_ctrl())
    logger.addHandler(log_handler)

    last_log_file = log_path
    rotate_file_handler = RotatingFileHandler(last_log_file, maxBytes=1024*1024*1, backupCount=1)
    rotate_file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'))
    logger.addHandler(rotate_file_handler)

    logger.setLevel(log_level)
    logger.info("正在运行中....")
    return logger
