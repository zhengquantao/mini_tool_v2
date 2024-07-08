import logging
from logging.handlers import RotatingFileHandler

import wx

from settings.settings import log_level, log_path


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


def init_log(frame=None):
    log = logging.getLogger()
    log_handler = RealTimeLogHandler(frame.logger)
    log.addHandler(log_handler)

    last_log_file = log_path
    rotate_file_handler = RotatingFileHandler(last_log_file, maxBytes=1024*1024*1, backupCount=1)
    rotate_file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'))
    log.addHandler(rotate_file_handler)

    log.setLevel(log_level)
    return log


logger = None
