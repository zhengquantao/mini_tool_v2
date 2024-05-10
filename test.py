import wx
import wx.aui

class MyFrame(wx.Frame):
    def __init__(self, parent, id=-1, title="AUI Test",
                 pos=wx.DefaultPosition, size=(800, 600)):
        wx.Frame.__init__(self, parent, id, title, pos, size)
        self._mgr = wx.aui.AuiManager(self)

        text1 = wx.TextCtrl(self, -1, "Pane 1", style=wx.NO_BORDER | wx.TE_MULTILINE)
        self._mgr.AddPane(text1, wx.aui.AuiPaneInfo().Bottom().Name("Pane Number One").Caption("Pane Number One"))

        # 添加一个恢复按钮
        self.restore_button = wx.Button(self, -1, "Restore Pane")
        self.Bind(wx.EVT_BUTTON, self.OnRestoreButton, self.restore_button)
        self._mgr.AddPane(self.restore_button, wx.aui.AuiPaneInfo().Top().Caption("Restore Button"))

        self._mgr.Update()
        self.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

    def OnPaneClose(self, event):
        pane = event.GetPane()
        pane.Hide()
        self._mgr.Update()

    def OnRestoreButton(self, event):
        self.RestorePane()

    def RestorePane(self):
        pane = self._mgr.GetPane("Pane Number One")
        if pane.IsShown():
            print("Pane is already shown")
        else:
            pane.Show()
            self._mgr.Update()

app = wx.App()
frame = MyFrame(None)
frame.Show()
app.MainLoop()
