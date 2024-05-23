import wx
import time


class Mywin(wx.Frame):
    def __init__(self, parent, title):
        super(Mywin, self).__init__(parent, title=title, size=(300, 150))

        panel = wx.Panel(self)
        self.gauge = wx.Gauge(panel, range=100, size=(250, 25), pos=(10, 10))
        start_button = wx.Button(panel, label="停止", pos=(100, 100))
        start_button.Bind(wx.EVT_BUTTON, self.OnStart)
        self.count = 0

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(500)
        self.Centre()
        self.Show(True)

    def OnStart(self, event):
        self.timer.Stop()

    def OnTimer(self, event):
        self.count = self.count + 1
        self.gauge.SetValue(self.count)
        self.Disable()
        if self.count >= 100:
            self.timer.Stop()
            self.count = 0
            self.Enable()


app = wx.App()
Mywin(None, "Gauge Example")
app.MainLoop()