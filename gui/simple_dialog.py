from json import detect_encoding

import pandas as pd
import wx


class SimpleDialog(wx.Dialog):
    def __init__(self, parent, title=u"Bar Chart"):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=title, pos=wx.DefaultPosition, size=wx.Size(350, 300),
                           style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        wSizer2 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)

        self.m_staticText44 = wx.StaticText(self, wx.ID_ANY, u"选择需要读取的文件：", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText44.Wrap(-1)

        wSizer2.Add(self.m_staticText44, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        self.t_input = wx.TextCtrl(self,  size=(169, 25))

        wSizer2.Add(self.t_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)

        bSizer3.Add(wSizer2, 0, 0, 5)

        wSizer3 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)

        self.m_staticText45 = wx.StaticText(self, wx.ID_ANY, u"选择需要Y轴的字段：", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText45.Wrap(-1)

        wSizer3.Add(self.m_staticText45, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        self.ylist = wx.CheckListBox(self, size=(170, 130), choices=[], style=wx.TC_MULTILINE)

        wSizer3.Add(self.ylist, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer3.Add(wSizer3, 0, 0, 5)

        wSizer4 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)

        self.m_staticText46 = wx.StaticText(self, wx.ID_ANY, u"选择需要X轴的字段：", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText46.Wrap(-1)

        wSizer4.Add(self.m_staticText46, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        self.xlist = wx.ComboBox(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(170, 30),
                                 choices=[])
        self.xlist.AutoComplete([])
        wSizer4.Add(self.xlist, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer3.Add(wSizer4, 0, 0, 5)

        wSizer6 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)

        self.m_button1 = wx.Button(self, wx.ID_ANY, u"取消", wx.DefaultPosition, wx.DefaultSize, 0)
        wSizer6.Add(self.m_button1, 0, wx.ALL, 10)

        self.m_button2 = wx.Button(self, wx.ID_OK, u"画图", wx.DefaultPosition, wx.DefaultSize, 0)
        wSizer6.Add(self.m_button2, 0, wx.ALL, 10)

        bSizer3.Add(wSizer6, 0, wx.ALIGN_RIGHT, 5)

        self.SetSizer(bSizer3)
        self.Layout()

        self.Centre(wx.BOTH)

        self.m_button1.Bind(wx.EVT_LEFT_UP, self.on_button10)
        # self.m_button2.Bind(wx.EVT_LEFT_UP, self.on_button20)
        self.t_input.Bind(wx.EVT_LEFT_UP, self.on_select_file)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def __del__(self):
        pass

    def on_close(self, event):
        self.Destroy()

    def on_select_file(self, event):
        select_dialog = wx.FileDialog(self, "请选择要打开的csv文件：", style=wx.DD_DEFAULT_STYLE,
                                      wildcard="Text files (*.csv)|*.csv")
        if select_dialog.ShowModal() != wx.ID_OK:
            return

        path = select_dialog.GetPath()
        print(f"Chosen directory: {path}")
        self.t_input.SetValue(path)
        self.t_input.SetEditable(False)
        self.data_df = pd.read_csv(path, encoding=detect_encoding(path))
        self.ylist.SetItems(self.data_df.columns)
        self.xlist.SetItems(self.data_df.columns)
        self.xlist.AutoComplete(self.data_df.columns)

    # Virtual event handlers, overide them in your derived class
    def on_button20(self, event):
        self.on_close(event)
        # event.Skip()

    def on_button10(self, event):
        self.on_close(event)
        # event.Skip()
