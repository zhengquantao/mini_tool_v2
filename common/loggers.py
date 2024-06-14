import logging
import os
from logging.handlers import RotatingFileHandler

import wx

from settings.settings import log_level


class RealTimeLogHandler(logging.Handler):
    def __init__(self, text_ctrl):
        logging.Handler.__init__(self)
        formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')
        self.setFormatter(formatter)
        self.text_ctrl = text_ctrl

    def emit(self, record):
        message = self.format(record)
        # if log_level == "DEBUG":
        #     self.text_ctrl.SetStyle(wx.TextAttr(wx.BLUE))
        # elif log_level == "INFO":
        #     self.text_ctrl.SetStyle(wx.TextAttr(wx.BLACK))
        # elif log_level == "WARNING":
        #     self.text_ctrl.SetStyle(wx.TextAttr(wx.YELLOW))
        # elif log_level == "ERROR":
        #     self.text_ctrl.SetStyle(0, 5, wx.TextAttr(wx.RED))
        # 安全地在UI主线程中更新TextCtrl
        wx.CallAfter(self.text_ctrl.AppendText, message + '\n')


def init_log(frame=None):
    log = logging.getLogger()
    log_handler = RealTimeLogHandler(frame)
    log.addHandler(log_handler)

    last_log_file = os.path.join(os.path.expanduser("~"), "mini_tool.log")
    rotate_file_handler = RotatingFileHandler(last_log_file, maxBytes=1024*1024*1, backupCount=1)
    rotate_file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'))
    log.addHandler(rotate_file_handler)

    log.setLevel(log_level)
    return log


logger_frame = None
logger = None
