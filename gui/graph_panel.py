import os

import pandas as pd
import wx
from aui2 import svg_to_bitmap

from common.common import add_notebook_page, detect_encoding
from common.loggers import logger
from graph import simple_chart
from gui.simple_dialog import SimpleDialog
from settings import settings as cs
from settings.settings import opening_dict


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
        self.select_idx = []
        self.file_list = []
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
        # panel6 = wx.Panel(panel4, pos=(5, 80), size=(150, 30))
        self.tc1 = IconTextCtrl(panel4, style=wx.TE_PROCESS_ENTER, pos=(5, 25), size=(150, 30), choices=self.columns)
        self.tc1.text_ctrl.AutoComplete([])

        wx.StaticText(panel4, pos=(5, 58), label='Y轴：')
        self.tc2 = wx.CheckListBox(panel4, pos=(5, 78), size=(150, 145), choices=self.columns, style=wx.TC_MULTILINE)
        self.tc2.Bind(wx.EVT_LISTBOX, self.on_item_clicked)
        self.tc2.Bind(wx.EVT_LISTBOX_DCLICK, self.on_item_clicked)
        button1 = wx.Button(panel4, -1, '更 多', pos=(8, 231), size=(70, 30))
        button1.Bind(wx.EVT_BUTTON, self.on_more)
        button1.SetBitmapLabel(svg_to_bitmap(cs.more_svg, size=(16, 16)))
        button2 = wx.Button(panel4, -1, '浏 览', pos=(80, 231), size=(70, 30))
        button2.SetBitmapLabel(svg_to_bitmap(cs.sea_svg, size=(20, 20)))
        button2.Bind(wx.EVT_BUTTON, self.on_click)
        panel4.SetBackgroundColour("white")
        sizer2.Add(panel2, 0, wx.ALL, 1)

        sizer.Add(sizer1, 0, wx.ALL, 0)
        sizer.Add(sizer2, 0, wx.ALL, 0)

        self.SetSizer(sizer)
        self.Layout()
        return self

    def on_item_clicked(self, event):
        index = event.GetSelection()
        self.tc2.Check(index, not self.tc2.IsChecked(index))

    def on_more(self, event):
        dialog = wx.Dialog(self, id=wx.ID_ANY, title="选择要对比的文件", pos=wx.DefaultPosition, size=wx.Size(250, 200),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.YES_DEFAULT)
        self.list_box = wx.ListBox(dialog, choices=self.file_list, style=wx.LB_MULTIPLE)
        for idx in self.select_idx:
            self.list_box.SetSelection(idx)
        self.list_box.Bind(wx.EVT_LISTBOX, self.on_select)
        dialog.ShowModal()

    def on_select(self, event):
        self.select_idx = [index for index in self.list_box.GetSelections()]

    def set_data(self, data):
        self.data = data[0]
        self.columns = data[0].columns
        self.init_more_data(data[1])

        self.listbox.DeleteAllItems()
        for i, d in enumerate(self.columns):
            self.listbox.InsertItem(i, d, 0)

        self.tc1.text_ctrl.Clear()
        self.tc1.text_ctrl.SetItems(self.columns)
        self.tc1.text_ctrl.AutoComplete(self.columns)

        self.tc2.Clear()
        self.tc2.SetItems(self.columns)

    def init_more_data(self, file_name):
        self.file_list = []
        for idx, file in enumerate(os.listdir(opening_dict[os.getpid()]["path"])):
            if not file.endswith(".csv"):
                continue
            self.file_list.append(file)
            if file == file_name:
                self.select_idx = [idx]

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
            wx.MessageBox("请选择图表！")
            return

        if self.data is None:
            wx.MessageBox("请选择CSV文件！")
            return

        if self.data.empty:
            wx.MessageBox("请选择不为空的CSV文件！")
            return

        x_field = self.tc1.text_ctrl.GetValue()
        y_list = self.tc2.GetCheckedItems()

        if not all([x_field, y_list]):
            wx.MessageBox("X,Y轴不能为空")
            return

        df, x_field, y_fields = self.read_df(x_field, y_list)

        file_paths, file_name = simple_chart.build_html(x=df[x_field], y=df[y_fields],
                                                        title="", echart_type=self.tmp_chart, save_path=None)
        add_notebook_page(self.notebook_ctrl, self.html_ctrl, file_paths, file_name)

    def read_df(self, x_field, y_list):

        y_fields = []
        for sel in y_list:
            # 使用GetStringSelection获取选中项的文本
            y_fields.append(self.tc2.GetString(sel))

        if not self.select_idx:
            df = self.filter_df(self.data, self.tc1.data, x_field)
            return df, x_field, y_fields

        ret_df = pd.DataFrame()
        ret_y_fields = []
        for idx in self.select_idx:
            try:
                path = os.path.join(opening_dict[os.getpid()]["path"], self.file_list[idx])
                df = pd.read_csv(path, encoding=detect_encoding(path), low_memory=False)
                df = self.filter_df(df, self.tc1.data, x_field)
                if ret_df.empty:
                    ret_df[x_field] = df[x_field]
                df = df[y_fields]
                new_names = [f"{self.file_list[idx].split('.')[0]}_{field}" for field in y_fields]
                df.columns = new_names
                ret_y_fields.extend(new_names)
                ret_df = pd.concat([ret_df, df], axis=1)
            except Exception as e:
                logger.error(e)
        return ret_df, x_field, ret_y_fields

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
