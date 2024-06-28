import wx


class SimpleDialog(wx.Dialog):
    def __init__(self, parent, title=u"过滤", data=None):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=title, pos=wx.DefaultPosition, size=wx.Size(300, 210),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.YES_DEFAULT)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.data = data

        b_sizer3 = wx.BoxSizer(wx.VERTICAL)

        w_sizer2 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)

        self.m_staticText44 = wx.StaticText(self, wx.ID_ANY, f"过滤大于(>)：", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText44.Wrap(-1)

        w_sizer2.Add(self.m_staticText44, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        self.t_input1 = wx.TextCtrl(self, size=(169, 25), value=data.get("L"))

        w_sizer2.Add(self.t_input1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)

        b_sizer3.Add(w_sizer2, 0, wx.ALIGN_RIGHT, 5)

        w_sizer3 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)

        self.m_staticText45 = wx.StaticText(self, wx.ID_ANY, f"过滤小于(<)：", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText45.Wrap(-1)

        w_sizer3.Add(self.m_staticText45, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        self.t_input2 = wx.TextCtrl(self,  size=(169, 25), value=data.get("S"))

        w_sizer3.Add(self.t_input2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        b_sizer3.Add(w_sizer3, 0, wx.ALIGN_RIGHT, 5)

        w_sizer4 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)

        self.m_staticText46 = wx.StaticText(self, wx.ID_ANY, f"过滤包含(in)：", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText46.Wrap(-1)

        w_sizer4.Add(self.m_staticText46, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        self.t_input3 = wx.TextCtrl(self,  size=(169, 25), value=data.get("IN"))

        w_sizer4.Add(self.t_input3, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        b_sizer3.Add(w_sizer4, 0, wx.ALIGN_RIGHT, 5)

        w_sizer6 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)

        self.m_button1 = wx.Button(self, wx.ID_OK, f"确认")
        w_sizer6.Add(self.m_button1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        b_sizer3.Add(w_sizer6, 0,  wx.ALIGN_RIGHT, 5)

        self.SetSizer(b_sizer3)
        self.Layout()

        self.Centre(wx.BOTH)

        self.m_button1.Bind(wx.EVT_BUTTON, self.on_button)
        self.Show()

    def on_button(self, event):
        self.data["L"] = self.t_input1.GetValue()
        self.data["S"] = self.t_input2.GetValue()
        self.data["IN"] = self.t_input3.GetValue()
        self.Destroy()
