import wx


class GaugePanel(wx.GenericProgressDialog):
    def __init__(self, parent, title, callable_func: callable = None, args=None):
        wx.GenericProgressDialog.__init__(self, title, "准备中", maximum=100, parent=parent,
                                          style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_CAN_ABORT)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_progress)
        self.timer.Start(600)
        self.finally_progress(callable_func, args)

    def finally_progress(self, func: callable, args: tuple):
        try:
            func(*args)
            self.Update(100, "加载完成")
        finally:
            wx.CallAfter(self.close)

    def update_progress(self, event):
        try:
            value = self.GetValue()
            if value < 50:
                value += 1
                self.Update(value, "加载中")

            elif value >= 50 and value < 99.7:
                value += 0.02
                self.Update(value, "加载中")

            else:
                self.Update(value, "加载中")
        finally:
            pass

    def close(self):
        self.timer.Stop()
        self.Destroy()
