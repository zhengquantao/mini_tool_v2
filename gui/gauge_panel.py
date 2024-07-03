import wx
from common import loggers
from common.common import async_raise


class GaugePanel(wx.GenericProgressDialog):
    def __init__(self, parent, title, thread_id=None,):
        self.maximum = 3278
        wx.GenericProgressDialog.__init__(self, title, "准备中", maximum=self.maximum, parent=parent,
                                          style=wx.PD_APP_MODAL | wx.PD_CAN_ABORT | wx.PD_CAN_SKIP)
        self.thread_id = thread_id

        cancel_button = self.FindWindowByName("Cancel")
        if cancel_button:
            cancel_button.SetLabel("停止")
        skip_button = self.FindWindowByName("&Skip")
        if skip_button:
            skip_button.SetLabel("后台运行")

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_progress)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.timer.Start(600)

    def on_close(self, event):
        self.close()

    def update_progress(self, event):
        try:
            if self.WasCancelled():
                loggers.logger.info("任务强制停止")
                async_raise(self.thread_id, SystemExit, logger=loggers.logger)
                wx.CallAfter(self.close)
                return
            elif self.WasSkipped():
                wx.CallAfter(self.close)
                return
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
