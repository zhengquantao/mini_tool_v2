import datetime
from functools import wraps
import wx
import wx.svg


def random_name(f_type="html"):
    return f"date{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.{f_type}"


def check_graph_df(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        if not hasattr(self, "data_df"):
            wx.MessageBox("缺数据支撑画图，请选择文件", "错误", wx.YES_NO | wx.ICON_WARNING)
            return

        return func(self, *args, **kwargs)
    return inner


def read_file(file_path) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()

    return data
