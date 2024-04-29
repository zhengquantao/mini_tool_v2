import wx
import logging
import threading


class LogFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="实时日志显示")
        self.log_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.log_ctrl.Bind(wx.EVT_SIZE, self.OnResize)
        self.Show()

    def OnResize(self, event):
        self.log_ctrl.SetSize(event.GetSize())


class RealTimeLogHandler(logging.Handler):
    def __init__(self, text_ctrl):
        logging.Handler.__init__(self)
        self.text_ctrl = text_ctrl

    def emit(self, record):
        message = self.format(record)
        # 安全地在UI主线程中更新TextCtrl
        wx.CallAfter(self.text_ctrl.AppendText, message + '\n')


def main():
    app = wx.App(False)
    frame = LogFrame()
    log_handler = RealTimeLogHandler(frame.log_ctrl)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)

    # 测试日志输出
    threading.Thread(target=lambda: logger.error('这是一条错误日志')).start()

    app.MainLoop()


if __name__ == '__main__':
    main()