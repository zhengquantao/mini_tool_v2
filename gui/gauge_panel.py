import wx
from common import loggers
from common.common import async_raise


class GaugePanel(wx.GenericProgressDialog):
    def __init__(self, parent, title, thread_id=None,):
        self.maximum = 3278
        wx.GenericProgressDialog.__init__(self, title, "准备中", maximum=self.maximum, parent=parent,
                                          style=wx.PD_APP_MODAL | wx.PD_CAN_ABORT)
        self.thread_id = thread_id
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_progress)
        self.timer.Start(600)

    def update_progress(self, event):
        try:
            if self.WasCancelled():
                loggers.logger.info("任务强制停止")
                async_raise(self.thread_id, SystemExit, logger=loggers.logger)
                wx.CallAfter(self.close)

            value = self.GetValue()
            if value < self.maximum * 0.4:
                value += 5
                self.Update(value, "加载中")
            elif value >= self.maximum * 0.4 and value < self.maximum * 0.98:
                value += 1
                self.Update(value, "加载中")

            elif value >= self.maximum * 0.98 and value < self.maximum:
                self.Update(value, "加载中")
            else:
                wx.CallAfter(self.close)
        finally:
            pass

    def destroy(self):
        try:
            self.Update(100, "加载完成")
            wx.CallAfter(self.close)

        except Exception as e:
            print(e)

    def close(self):
        self.timer.Stop()
        wx.CallAfter(self.Destroy)
