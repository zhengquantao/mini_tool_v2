import wx


class GaugePanel(wx.GenericProgressDialog):
    def __init__(self, parent, title):
        wx.GenericProgressDialog.__init__(self, title, "准备中", maximum=100, parent=parent,
                                          style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_progress)
        self.timer.Start(600)

    def update_progress(self, event):
        try:
            value = self.GetValue()
            if value < 50:
                value += 1
                self.Update(value, "加载中")

            elif value >= 50 and value < 100:
                value += 0.02
                self.Update(value, "加载中")

            else:
                wx.CallAfter(self.close)

        except:
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
