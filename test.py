import wx


class Mywin(wx.Frame):
    def __init__(self, parent, title):
        super(Mywin, self).__init__(parent, title=title, size=(250, 150))

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        self.text = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        box.Add(self.text, 1, flag=wx.EXPAND | wx.ALL, border=20)

        cpy = wx.Button(panel, -1, "复制")
        cpy.Bind(wx.EVT_BUTTON, self.OnCopy)
        box.Add(cpy, 0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        pst = wx.Button(panel, -1, "粘贴")
        pst.Bind(wx.EVT_BUTTON, self.OnPaste)
        box.Add(pst, 0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        panel.SetSizer(box)
        self.Center()
        self.Show(True)

    def OnCopy(self, event):
        self.text.Copy()

    def OnPaste(self, event):
        self.text.Paste()


app = wx.App()
Mywin(None, '复制粘贴示例')
app.MainLoop()
