import os

import pandas as pd
import wx
from aui2 import svg_to_bitmap

from common.common import detect_encoding
from settings.settings import power_theoretical, convert_btn_svg


def convert_gui(call_func, save_path=""):
    app = wx.App(False)
    frame = wx.Frame(parent=None, title="")
    call_func(frame, save_path)
    # app.MainLoop()


class ScadaPanel:

    def __init__(self, parent, save_path=""):
        self.panel = panel = wx.Dialog(parent, id=wx.ID_ANY, title="SCADA数据转换", pos=wx.DefaultPosition,
                                       style=wx.DEFAULT_DIALOG_STYLE)
        self.filepath = None
        self.savepath = save_path
        self.data_df = None

        vbox = wx.BoxSizer(wx.VERTICAL)

        open_files_sizer = self.build_select_component(panel)

        fields_sizer = self.build_fields_component(panel)

        save_files_sizer = self.build_save_component(panel)

        button_sizer = self.build_button_component(panel)

        vbox.Add(open_files_sizer, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(fields_sizer, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(save_files_sizer, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(button_sizer, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(vbox)
        parent.Centre()
        panel.Fit()
        panel.ShowModal()

    def build_button_component(self, panel):
        button = wx.Button(panel, -1, " 开 始 转 换 ")
        button.Bind(wx.EVT_BUTTON, self.on_button)
        button.SetBitmapCurrent(svg_to_bitmap(convert_btn_svg, size=(20, 20)))
        return button

    def build_save_component(self, panel):
        save_files = wx.StaticBox(panel, -1, '3.保存转换后的文件:')
        save_files_sizer = wx.StaticBoxSizer(save_files, wx.VERTICAL)
        save_files_box = wx.BoxSizer(wx.HORIZONTAL)
        save_label1 = wx.StaticText(panel, -1, "请选择文件保存路径")
        self.save_file1 = wx.TextCtrl(panel, -1, size=(200, 30), style=wx.TE_READONLY,
                                      value=self.savepath.split(os.sep)[-1])
        self.save_file1.SetBackgroundColour("white")
        save_files_box.Add(save_label1, 5, wx.ALL | wx.CENTER, 5)
        save_files_box.Add(self.save_file1, 5, wx.ALL | wx.CENTER, 5)
        save_files_sizer.Add(save_files_box, 1, wx.ALL | wx.CENTER, 5)
        self.save_file1.Bind(wx.EVT_LEFT_DOWN, self.on_save_file)
        return save_files_sizer

    def build_select_component(self, panel):
        open_files = wx.StaticBox(panel, -1, '1.选择SCADA文件:')
        open_files_sizer = wx.StaticBoxSizer(open_files, wx.VERTICAL)
        open_files_box = wx.BoxSizer(wx.HORIZONTAL)
        file_label1 = wx.StaticText(panel, -1, "请选择SCADA文件(可多选)")
        self.file1 = wx.TextCtrl(panel, -1, size=(200, 30), style=wx.TE_READONLY)
        self.file1.SetBackgroundColour("white")
        open_files_box.Add(file_label1, 5, wx.ALL | wx.CENTER, 5)
        open_files_box.Add(self.file1, 5, wx.ALL | wx.CENTER, 5)
        open_files_sizer.Add(open_files_box, 1, wx.ALL | wx.CENTER, 5)
        self.file1.Bind(wx.EVT_LEFT_DOWN, self.on_select_file)
        return open_files_sizer

    def build_fields_component(self, panel):
        fields = wx.StaticBox(panel, -1, '2.字段转换:')
        fields_sizer = wx.StaticBoxSizer(fields, wx.VERTICAL)

        field1_box = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, -1, "时间(real_time)")
        self.field1 = wx.ComboBox(panel, -1, size=(200, 30))
        field1_box.Add(label1, 5, wx.ALL | wx.CENTER, 5)
        field1_box.Add(self.field1, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field1_box, 0, wx.ALL | wx.CENTER, 5)

        field2_box = wx.BoxSizer(wx.HORIZONTAL)
        label2 = wx.StaticText(panel, -1, "风机编号(turbine_code)")
        self.field2 = wx.ComboBox(panel, -1, size=(200, 30))
        field2_box.Add(label2, 5, wx.ALL | wx.CENTER, 5)
        field2_box.Add(self.field2, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field2_box, 0, wx.ALL | wx.CENTER, 5)

        field3_box = wx.BoxSizer(wx.HORIZONTAL)
        label3 = wx.StaticText(panel, -1, "桨叶角度(pitch_angle)")
        self.field3 = wx.ComboBox(panel, -1, size=(200, 30))
        field3_box.Add(label3, 5, wx.ALL | wx.CENTER, 5)
        field3_box.Add(self.field3, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field3_box, 0, wx.ALL | wx.CENTER, 5)

        field4_box = wx.BoxSizer(wx.HORIZONTAL)
        label4 = wx.StaticText(panel, -1, "发电机转速(generator_speed)")
        self.field4 = wx.ComboBox(panel, -1, size=(200, 30))
        field4_box.Add(label4, 5, wx.ALL | wx.CENTER, 5)
        field4_box.Add(self.field4, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field4_box, 0, wx.ALL | wx.CENTER, 5)

        field5_box = wx.BoxSizer(wx.HORIZONTAL)
        label5 = wx.StaticText(panel, -1, "机舱方向(nacelle_direction)")
        self.field5 = wx.ComboBox(panel, -1, size=(200, 30))
        field5_box.Add(label5, 5, wx.ALL | wx.CENTER, 5)
        field5_box.Add(self.field5, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field5_box, 0, wx.ALL | wx.CENTER, 5)

        field6_box = wx.BoxSizer(wx.HORIZONTAL)
        label6 = wx.StaticText(panel, -1, "风向(wind_direction)")
        self.field6 = wx.ComboBox(panel, -1, size=(200, 30))
        field6_box.Add(label6, 5, wx.ALL | wx.CENTER, 5)
        field6_box.Add(self.field6, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field6_box, 0, wx.ALL | wx.CENTER, 5)

        field7_box = wx.BoxSizer(wx.HORIZONTAL)
        label7 = wx.StaticText(panel, -1, "机舱温度(nacelle_temperature)")
        self.field7 = wx.ComboBox(panel, -1, size=(200, 30))
        field7_box.Add(label7, 5, wx.ALL | wx.CENTER, 5)
        field7_box.Add(self.field7, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field7_box, 0, wx.ALL | wx.CENTER, 5)

        field8_box = wx.BoxSizer(wx.HORIZONTAL)
        label8 = wx.StaticText(panel, -1, "空气密度(air_density)")
        self.field8 = wx.ComboBox(panel, -1, size=(200, 30))
        field8_box.Add(label8, 5, wx.ALL | wx.CENTER, 5)
        field8_box.Add(self.field8, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field8_box, 0, wx.ALL | wx.CENTER, 5)

        field9_box = wx.BoxSizer(wx.HORIZONTAL)
        label9 = wx.StaticText(panel, -1, "功率(power)")
        self.field9 = wx.ComboBox(panel, -1, size=(200, 30))
        field9_box.Add(label9, 5, wx.ALL | wx.CENTER, 5)
        field9_box.Add(self.field9, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field9_box, 0, wx.ALL | wx.CENTER, 5)

        field12_box = wx.BoxSizer(wx.HORIZONTAL)
        label12 = wx.StaticText(panel, -1, "风速(wind_speed)")
        self.field12 = wx.ComboBox(panel, -1, size=(200, 30))
        field12_box.Add(label12, 5, wx.ALL | wx.CENTER, 5)
        field12_box.Add(self.field12, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field12_box, 0, wx.ALL | wx.CENTER, 5)

        field10_box = wx.BoxSizer(wx.HORIZONTAL)
        label10 = wx.StaticText(panel, -1, "风机运行状态掩码(run_status)")
        self.field10 = wx.ComboBox(panel, -1, size=(200, 30))
        field10_box.Add(label10, 5, wx.ALL | wx.CENTER, 5)
        field10_box.Add(self.field10, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field10_box, 0, wx.ALL | wx.CENTER, 5)

        field11_box = wx.BoxSizer(wx.HORIZONTAL)
        label11 = wx.StaticText(panel, -1, "并网运行掩码值")
        self.field11 = wx.ComboBox(panel, -1, size=(200, 30))
        field11_box.Add(label11, 5, wx.ALL | wx.CENTER, 5)
        field11_box.Add(self.field11, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field11_box, 0, wx.ALL | wx.CENTER, 5)
        self.field11.Bind(wx.EVT_LEFT_DOWN, self.set_status_value)
        return fields_sizer

    def on_button(self, event):
        if not self.filepath:
            wx.MessageBox("请选择SCADA文件")
            return

        if not self.savepath:
            wx.MessageBox("请选择文件保存路径")
            return

        real_time = self.field1.GetStringSelection()
        if not real_time:
            wx.MessageBox("请选择时间字段")
            return

        self.handle_converts()
        wx.MessageBox(f"成功！转换路径为：\n"
                      f"{self.savepath}")

    def handle_converts(self):
        real_time = self.field1.GetStringSelection()
        turbine_code = self.field2.GetStringSelection()
        pitch_angle = self.field3.GetStringSelection()
        generator_speed = self.field4.GetStringSelection()
        nacelle_direction = self.field5.GetStringSelection()
        wind_direction = self.field6.GetStringSelection()
        nacelle_temperature = self.field7.GetStringSelection()
        air_density = self.field8.GetStringSelection()
        power = self.field9.GetStringSelection()
        run_status = self.field10.GetStringSelection()
        status_value = self.field11.GetStringSelection()
        wind_speed = self.field12.GetStringSelection()

        for file in self.filepath:
            try:
                output_df = pd.DataFrame()
                df = self.filter_df(file, run_status, status_value)
                output_df["real_time"] = df[real_time] if real_time in df.columns else ""
                output_df["wind_speed"] = df[wind_speed] if wind_speed in df.columns else ""
                output_df["pitch_angle"] = df[pitch_angle] if pitch_angle in df.columns else ""
                output_df["generator_speed"] = df[generator_speed] if generator_speed in df.columns else ""
                output_df["nacelle_direction"] = df[nacelle_direction] if nacelle_direction in df.columns else ""
                output_df["wind_direction"] = df[wind_direction] if wind_direction in df.columns else ""
                output_df["nacelle_temperature"] = df[nacelle_temperature] if nacelle_temperature in df.columns else ""
                output_df["air_density"] = df[air_density] if air_density in df.columns else ""
                output_df["power"] = df[power] if power in df.columns else ""
                output_df["turbine_code"] = df[turbine_code] if turbine_code in df.columns else self.get_file_name(file)
                output_df.to_csv(os.path.join(self.savepath, f"{self.get_file_name(file)}.csv"), index=False)
            except Exception as e:
                pass

    @staticmethod
    def get_file_name(filepath):
        return filepath.split(os.sep)[-1].split(".")[0]

    def filter_df(self, file, run_status, status_value):
        df = self.open_file(file)
        if not status_value:
            return df
        val = eval(status_value)
        if isinstance(val, (int, float, complex)):
            df = df[df[run_status] == val]
        else:
            df = df[df[run_status] == val]
        return df

    def set_status_value(self, event):

        if self.data_df is None:
            return

        field = self.field10.GetStringSelection()
        if not field:
            return

        values = pd.unique(self.data_df[field]).astype(str)
        self.field11.AutoComplete(values)
        self.field11.SetItems(values)
        event.Skip()

    def on_select_file(self, event):
        dialog = wx.FileDialog(self.panel, "请选择需要转换的文件",
                               wildcard="所有文件 (*.csv, *.xls, *.xlsx)|*.csv;*.xls;*.xlsx", style=wx.FD_MULTIPLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.filepath = dialog.GetPaths()  # 获取选择的文件路径
            self.file1.SetValue(",".join([i.split(os.sep)[-1] for i in self.filepath]))
            self.data_df = self.open_file(self.filepath[0])
            self.set_field_columns()
        dialog.Destroy()

    def on_save_file(self, event):
        dialog = wx.DirDialog(self.panel, "请选择转换后文件保存的路径", defaultPath=self.savepath)
        if dialog.ShowModal() == wx.ID_OK:
            self.savepath = dialog.GetPath()
            self.save_file1.SetValue(self.savepath.split(os.sep)[-1])
        dialog.Destroy()

    @staticmethod
    def open_file(filepath: str, **kwargs):
        if filepath.endswith(".csv"):
            df = pd.read_csv(filepath, encoding=detect_encoding(filepath), low_memory=False, **kwargs)
        else:
            df = pd.read_excel(filepath, **kwargs)
        return df

    def set_field_columns(self):
        self.field1.SetItems(self.data_df.columns)
        self.field1.AutoComplete(self.data_df.columns)
        self.field2.SetItems(self.data_df.columns)
        self.field2.AutoComplete(self.data_df.columns)
        self.field3.SetItems(self.data_df.columns)
        self.field3.AutoComplete(self.data_df.columns)
        self.field4.SetItems(self.data_df.columns)
        self.field4.AutoComplete(self.data_df.columns)
        self.field5.SetItems(self.data_df.columns)
        self.field5.AutoComplete(self.data_df.columns)
        self.field6.SetItems(self.data_df.columns)
        self.field6.AutoComplete(self.data_df.columns)
        self.field7.SetItems(self.data_df.columns)
        self.field7.AutoComplete(self.data_df.columns)
        self.field8.SetItems(self.data_df.columns)
        self.field8.AutoComplete(self.data_df.columns)
        self.field9.SetItems(self.data_df.columns)
        self.field9.AutoComplete(self.data_df.columns)
        self.field10.SetItems(self.data_df.columns)
        self.field10.AutoComplete(self.data_df.columns)
        self.field12.SetItems(self.data_df.columns)
        self.field12.AutoComplete(self.data_df.columns)


class PowerTheoreticalPanel:

    def __init__(self, parent, save_path=""):
        self.panel = panel = wx.Dialog(parent, id=wx.ID_ANY, title="理论功率数据转换", pos=wx.DefaultPosition,
                                       style=wx.DEFAULT_DIALOG_STYLE)
        self.filepath = None
        self.savepath = save_path
        self.data_df = None

        vbox = wx.BoxSizer(wx.VERTICAL)

        open_files_sizer = self.build_select_component(panel)

        fields_sizer = self.build_fields_component(panel)

        save_files_sizer = self.build_save_component(panel)

        button_sizer = self.build_button_component(panel)

        vbox.Add(open_files_sizer, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(fields_sizer, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(save_files_sizer, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(button_sizer, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(vbox)
        parent.Centre()
        panel.Fit()
        panel.ShowModal()

    def build_button_component(self, panel):
        button = wx.Button(panel, -1, " 开 始 转 换 ")
        button.Bind(wx.EVT_BUTTON, self.on_button)
        button.SetBitmapCurrent(svg_to_bitmap(convert_btn_svg, size=(20, 20)))
        return button

    def build_save_component(self, panel):
        save_files = wx.StaticBox(panel, -1, '3.保存转换后的文件:')
        save_files_sizer = wx.StaticBoxSizer(save_files, wx.VERTICAL)
        save_files_box = wx.BoxSizer(wx.HORIZONTAL)
        save_label1 = wx.StaticText(panel, -1, "请选择文件保存路径")
        self.save_file1 = wx.TextCtrl(panel, -1, size=(200, 30), style=wx.TE_READONLY,
                                      value=self.savepath.split(os.sep)[-1])
        self.save_file1.SetBackgroundColour("white")
        save_files_box.Add(save_label1, 5, wx.ALL | wx.CENTER, 5)
        save_files_box.Add(self.save_file1, 5, wx.ALL | wx.CENTER, 5)
        save_files_sizer.Add(save_files_box, 1, wx.ALL | wx.CENTER, 5)
        self.save_file1.Bind(wx.EVT_LEFT_DOWN, self.on_save_file)
        return save_files_sizer

    def build_select_component(self, panel):
        open_files = wx.StaticBox(panel, -1, '1.选择理论功率文件:')
        open_files_sizer = wx.StaticBoxSizer(open_files, wx.VERTICAL)
        open_files_box = wx.BoxSizer(wx.HORIZONTAL)
        file_label1 = wx.StaticText(panel, -1, "请选择理论功率文件")
        self.file1 = wx.TextCtrl(panel, -1, size=(200, 30), style=wx.TE_READONLY)
        self.file1.SetBackgroundColour("white")
        open_files_box.Add(file_label1, 5, wx.ALL | wx.CENTER, 5)
        open_files_box.Add(self.file1, 5, wx.ALL | wx.CENTER, 5)
        open_files_sizer.Add(open_files_box, 1, wx.ALL | wx.CENTER, 5)
        self.file1.Bind(wx.EVT_LEFT_DOWN, self.on_select_file)
        return open_files_sizer

    def build_fields_component(self, panel):
        fields = wx.StaticBox(panel, -1, '2.字段转换:')
        fields_sizer = wx.StaticBoxSizer(fields, wx.VERTICAL)

        field1_box = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, -1, "理论风速(WINDS_SPEED)")
        self.field1 = wx.ComboBox(panel, -1, size=(200, 30))
        field1_box.Add(label1, 5, wx.ALL | wx.CENTER, 5)
        field1_box.Add(self.field1, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field1_box, 0, wx.ALL | wx.CENTER, 5)

        field2_box = wx.BoxSizer(wx.HORIZONTAL)
        label2 = wx.StaticText(panel, -1, "理论功率(WINDS_POWER)")
        self.field2 = wx.ComboBox(panel, -1, size=(200, 30))
        field2_box.Add(label2, 5, wx.ALL | wx.CENTER, 5)
        field2_box.Add(self.field2, 5, wx.ALL | wx.CENTER, 5)
        fields_sizer.Add(field2_box, 0, wx.ALL | wx.CENTER, 5)

        return fields_sizer

    def on_button(self, event):
        if not self.filepath:
            wx.MessageBox("请选择理论功率文件")
            return

        if not self.savepath:
            wx.MessageBox("请选择文件保存路径")
            return

        wind_speed = self.field1.GetStringSelection()
        if not wind_speed:
            wx.MessageBox("请选择风速字段")
            return

        wind_power = self.field1.GetStringSelection()
        if not wind_power:
            wx.MessageBox("请选择功率字段")
            return

        self.handle_converts()
        wx.MessageBox(f"成功！转换路径为：\n{self.savepath}")

    def handle_converts(self):
        wind_speed = self.field1.GetStringSelection()
        power = self.field2.GetStringSelection()

        for file in self.filepath:
            try:
                output_df = pd.DataFrame()
                df = self.filter_df(file, "", "")
                output_df["WINDS_SPEED"] = df[wind_speed] if wind_speed in df.columns else ""
                output_df["WINDS_POWER"] = df[power] if power in df.columns else ""

                output_df.to_csv(os.path.join(self.savepath, power_theoretical), index=False)
            except Exception as e:
                pass

    @staticmethod
    def get_file_name(filepath):
        return filepath.split(os.sep)[-1].split(".")[0]

    def filter_df(self, file, run_status, status_value):
        df = self.open_file(file)
        if not status_value:
            return df
        if status_value.isdigit():
            df = df[df[run_status] == int(status_value)]
        else:
            df = df[df[run_status] == status_value]
        return df

    def on_select_file(self, event):
        dialog = wx.FileDialog(self.panel, "请选择需要转换的文件",
                               wildcard="所有文件 (*.csv, *.xls, *.xlsx)|*.csv;*.xls;*.xlsx", style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.filepath = dialog.GetPaths()  # 获取选择的文件路径
            self.file1.SetValue(",".join([i.split(os.sep)[-1] for i in self.filepath]))
            self.data_df = self.open_file(self.filepath[0])
            self.set_field_columns()
        dialog.Destroy()

    def on_save_file(self, event):
        dialog = wx.DirDialog(self.panel, "请选择转换后文件保存的路径", defaultPath=self.savepath)
        if dialog.ShowModal() == wx.ID_OK:
            self.savepath = dialog.GetPath()
            self.save_file1.SetValue(self.savepath.split(os.sep)[-1])
        dialog.Destroy()

    @staticmethod
    def open_file(filepath: str):
        if filepath.endswith(".csv"):
            df = pd.read_csv(filepath, encoding=detect_encoding(filepath), low_memory=False)
        else:
            df = pd.read_excel(filepath)
        return df

    def set_field_columns(self):
        self.field1.SetItems(self.data_df.columns)
        self.field1.AutoComplete(self.data_df.columns)
        self.field2.SetItems(self.data_df.columns)
        self.field2.AutoComplete(self.data_df.columns)
