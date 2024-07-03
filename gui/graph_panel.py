import wx
from aui2 import svg_to_bitmap

from common.common import add_notebook_page
from graph import simple_chart
from gui.simple_dialog import SimpleDialog
from settings import settings as cs


class CustomComboBox(wx.ComboBox):
    def __init__(self, *args, **kwargs):
        super(CustomComboBox, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBrush(wx.Brush(self.GetBackgroundColour()))
        dc.SetPen(wx.Pen(self.GetBackgroundColour()))
        dc.DrawRectangle(0, 0, self.GetSize().width, self.GetSize().height)
        event.Skip(False)


class IconTextCtrl(wx.Control):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
                 name="IconTextCtrl", choices=None):
        super().__init__(parent, id, pos, size, style, validator, name)
        self.data = {"field": "", "L": "", "S": "", "IN": ""}

        self.text_ctrl = CustomComboBox(self, wx.ID_ANY, pos=(0, 0), size=(110, 30),
                                        choices=choices, style=wx.BORDER_NONE | wx.NO_BORDER)

        self.bitmap = wx.BitmapButton(self, wx.ID_ANY, svg_to_bitmap(cs.inp_setting_svg, size=(16, 16)), pos=(110, 0), style=wx.NO_BORDER)
        self.bitmap2 = wx.BitmapButton(self, wx.ID_ANY, svg_to_bitmap(cs.inp_close_svg, size=(14, 14)), pos=(130, 0), style=wx.NO_BORDER)

        self.bitmap.Bind(wx.EVT_BUTTON, self.on_setting)
        self.bitmap2.Bind(wx.EVT_BUTTON, self.on_clear)

        self.bitmap.SetBackgroundColour("white")
        self.bitmap2.SetBackgroundColour("white")
        self.SetBackgroundColour("white")

    def on_clear(self, event):
        # 处理按钮点击事件
        self.text_ctrl.SetValue("")

    def on_setting(self, event):
        dialog = SimpleDialog(self, title=f"过滤字段 {self.text_ctrl.GetValue()}", data=self.data)
        result = dialog.ShowModal()
        if result != wx.ID_OK:
            dialog.Destroy()
            return

        self.data = dialog.data


class GraphPanel(wx.Panel):

    def __init__(self, parent, notebook_ctrl, html_ctrl):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.tmp_chart = None
        self.data = None
        self.columns = []
        self.notebook_ctrl = notebook_ctrl
        self.html_ctrl = html_ctrl
        # self.SetBackgroundColour("white")

    def create_ctrl(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer1 = wx.BoxSizer(wx.VERTICAL)

        label1 = wx.StaticText(self, pos=(5, 0), label='数据')

        list_ctrl = self.build_list_ctrl(self)
        sizer1.Add(label1, 0, wx.ALL, 1)
        sizer1.Add(list_ctrl, 1, wx.ALL | wx.EXPAND, 1)

        sizer2 = wx.BoxSizer(wx.VERTICAL)
        panel2 = wx.Panel(self)
        wx.StaticText(panel2, pos=(5, 0), label='图表')
        panel3 = wx.Panel(panel2, pos=(0, 20), size=(161, 149))
        self.build_bitmap_button(panel3)
        panel3.SetBackgroundColour("white")

        panel4 = wx.Panel(panel2, pos=(0, 150), size=(161, wx.EXPAND))
        wx.StaticText(panel4, pos=(5, 3), label='X轴：')
        # self.tc1 = wx.ComboBox(panel4, wx.ID_ANY, wx.EmptyString, pos=(5, 25), size=(150, 30), choices=self.columns,
        #                        style=wx.TC_MULTILINE)
        # self.tc1.AutoComplete([])
        panel6 = wx.Panel(panel4, pos=(5, 25), size=(150, 30))
        self.tc1 = IconTextCtrl(panel6, style=wx.TE_PROCESS_ENTER, size=(150, 30), choices=self.columns)
        self.tc1.text_ctrl.AutoComplete([])

        wx.StaticText(panel4, pos=(5, 58), label='Y轴：')
        self.tc2 = wx.CheckListBox(panel4, pos=(5, 78), size=(150, 145), choices=self.columns, style=wx.TC_MULTILINE)
        button = wx.Button(panel4, -1, '浏 览', pos=(75, 231))
        button.SetBitmapLabel(svg_to_bitmap(cs.sea_svg, size=(20, 20)))
        button.Bind(wx.EVT_BUTTON, self.on_click)
        panel4.SetBackgroundColour("white")
        sizer2.Add(panel2, 0, wx.ALL, 1)

        sizer.Add(sizer1, 0, wx.ALL, 0)
        sizer.Add(sizer2, 0, wx.ALL, 0)

        self.SetSizer(sizer)
        self.Layout()
        return self

    def set_data(self, data):
        self.data = data
        self.columns = data.columns

        self.listbox.DeleteAllItems()
        for i, d in enumerate(self.columns):
            self.listbox.InsertItem(i, d, 0)

        self.tc1.text_ctrl.Clear()
        self.tc1.text_ctrl.SetItems(self.columns)
        self.tc1.text_ctrl.AutoComplete(self.columns)

        self.tc2.Clear()
        self.tc2.SetItems(self.columns)

    def build_list_ctrl(self, panel5):
        self.listbox = wx.ListCtrl(panel5, wx.ID_ANY, pos=(5, 5), size=(160, wx.EXPAND),
                                   style=wx.NO_BORDER | wx.LC_REPORT | wx.LC_NO_HEADER)
        image_list = wx.ImageList(16, 16, True)
        image_list.Add(svg_to_bitmap(cs.sign_svg, size=(16, 16)))
        self.listbox.AssignImageList(image_list, wx.IMAGE_LIST_SMALL)
        self.listbox.InsertColumn(0, 'columns', width=160)
        return self.listbox

    def build_bitmap_button(self, panel3):
        self.bp_btn_dict = {
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(cs.line_svg, size=(45, 45)), pos=(2, 2), size=(49, 49), name='Line'): "Line",
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(cs.bar_svg, size=(45, 45)), pos=(2, 52), size=(49, 49), name='Bar'): "Bar",
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(cs.scatter_svg, size=(45, 45)), pos=(53, 2), size=(49, 49), name='Scatter'): "Scatter",
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(cs.bar2_svg, size=(45, 45)), pos=(53, 52), size=(49, 49), name='BarStack'): "BarStack",
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(cs.bar3_svg, size=(45, 45)), pos=(105, 2), size=(49, 49), name='BarReversal'): "BarReversal",
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(cs.line2_svg, size=(45, 45)), pos=(105, 52), size=(49, 49), name='LineGap'): "LineGap",
        }
        for btn in self.bp_btn_dict.keys():
            panel3.Bind(wx.EVT_BUTTON, self.on_dpclick, btn)

    def on_dpclick(self, event):
        btn_obj = event.GetEventObject()

        self.tmp_chart = self.bp_btn_dict[btn_obj]
        for btn in self.bp_btn_dict.keys():
            btn.SetBackgroundColour("")

        btn_obj.SetBackgroundColour("#BBDEFB")
        return

    def on_click(self, event):
        if not self.tmp_chart:
            return

        if self.data is None:
            return

        if self.data.empty:
            return

        x_field = self.tc1.text_ctrl.GetValue()
        df = self.filter_df(self.data, self.tc1.data, x_field)

        y_list = self.tc2.GetSelections()
        checks = self.tc2.GetCheckedItems()
        y_list.extend(checks)

        # selected_items = []
        # for sel in y_list:
        #     # 使用GetStringSelection获取选中项的文本
        #     selected_items.append(self.tc2.GetString(sel))

        file_paths, file_name = simple_chart.build_html(x=df[x_field], y=df.iloc[:, y_list],
                                                        title="", echart_type=self.tmp_chart, save_path=None)
        add_notebook_page(self.notebook_ctrl, self.html_ctrl, file_paths, file_name)

    def filter_df(self, df, params, field):
        class_type = type(df[field][0])
        if params.get("L"):
            df = df[df[field] > class_type(params["L"])]
        if params.get("S"):
            df = df[df[field] < class_type(params["S"])]
        if params.get("IN"):
            data_list = params["IN"].split(",")
            df = df[df[field].isin([class_type(i) for i in data_list])]
        return df
