import time

import wx


class GaugePanel:
    def __init__(self, parent, title):
        self.panel_dialog = wx.ProgressDialog(title,
                                              "准备中",
                                              maximum=100,
                                              parent=parent,
                                              style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)

        self.count = 0
        self.timer = wx.Timer(self.panel_dialog)
        self.panel_dialog.Bind(wx.EVT_TIMER, self.update_progress)
        self.timer.StartOnce()

    def update_progress(self, event):
        try:
            while self.count < 50:
                self.count += 0.5
                time.sleep(1)
                self.panel_dialog.Update(self.count, "加载中")
            while self.count >= 50 and self.count < 100:
                time.sleep(1)
                self.count += 0.02
                self.panel_dialog.Update(self.count, "加载中")

            if self.count >= 100:
                self.timer.Stop()
                self.panel_dialog.Destroy()
                # self.panel_dialog.Close(True)
        except:
            pass

    def destroy(self):
        try:
            self.panel_dialog.Update(98, "加载中")
            time.sleep(1.5)
            self.panel_dialog.Update(100, "加载完成")
            self.count = 100
            self.timer.Stop()
            self.panel_dialog.Destroy()
            # self.panel_dialog.Close(True)
        except Exception as e:
            print(e)

