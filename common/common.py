import datetime
import json
import os
import shutil
import time
from functools import wraps

import numpy as np
import pandas as pd
import psutil
import wx
import wx.svg
import wx.lib.agw.aui as aui
from dateutil import parser

from settings.settings import opening_dict, cols_titles


def new_app(path):
    from multiprocessing import Process
    from main import run_gui
    app = Process(target=run_gui, args=(path,))
    app.start()


def daemon_app(app):
    current_process = psutil.Process()

    while len(current_process.children()) > 3:
        time.sleep(3)

    app.terminate()


def random_name(turbine, desc, f_type="html"):
    return f"{turbine}-{desc}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.{f_type}"


def check_graph_df(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        if not hasattr(self, "data_df"):
            wx.MessageBox("缺数据支撑画图，请选择文件", "错误", wx.YES_NO | wx.ICON_WARNING)
            return

        return func(self, *args, **kwargs)
    return inner


def read_file(file_path) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8', errors="ignore") as file:
            data = file.read()

        return data
    except:
        return ""


def write_file(file_path, data, file_name='.mini'):
    with open(f"{os.path.join(file_path, file_name)}", 'w', encoding='utf-8', errors="ignore") as file:
        if not isinstance(data, (str, bytes)):
            data = json.dumps(data)
        file.write(data)


def remove_file(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
            return

        shutil.rmtree(path)
    except:
        pass


def rename_file(old_name, new_name):
    os.renames(old_name, new_name)


def save_mini_file(mgr):
    pid = os.getpid()
    opening_dicts = opening_dict[pid]
    opening_list = []
    for pane in mgr.GetAllPanes():
        if not isinstance(pane.window, aui.AuiNotebook):
            continue
        for i in range(pane.window.GetPageCount()):
            # print(pane.window.GetPage(i).GetName())
            # print(pane.window.GetPageInfo(i).caption)
            path = opening_dicts["records"].get(pane.window.GetPageInfo(i).caption)
            path and opening_list.append(path)

    write_file(opening_dicts["path"], {"file_path": opening_list})


def get_file_info(directory='.'):
    res = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # file_size = os.path.getsize(file_path)
            # print(f'文件名: {file}, 路径: {file_path}, 大小: {file_size} bytes')
            res.append(file_path)
    return res


def add_notebook_page(notebook_ctrl, html_ctrl, file_paths, file_name):
    page_bmp: wx.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
    ctrl = notebook_ctrl.notebook_object
    pid = os.getpid()
    opening_dict[pid]["records"][file_name] = file_paths
    ctrl.AddPage(html_ctrl.create_ctrl(path=file_paths), file_name, True, page_bmp)
    return ctrl


def common_cut(target_data, label, bin_label, start=0, step=0.25):
    bins = np.arange(start, np.ceil(target_data[label].max()), step)
    bins_labels = [x for x in bins[1:]]

    target_data[bin_label] = pd.cut(target_data[label], bins=bins, labels=bins_labels)
    return target_data


def is_second_data(data_df):
    """
    判断是否是秒级数据
    """
    time_one, time_two = data_df[0], data_df[1]
    time_one_obj = parser.parse(time_one)
    time_two_obj = parser.parse(time_two)
    timestamp = int(time_two_obj.timestamp()) - int(time_one_obj.timestamp())
    if timestamp > 1:
        return True

    return False


def read_file(file):
    cols_list = cols_titles.keys()
    data_frame = pd.read_csv(file, usecols=cols_list)
    select_col_df = data_frame[cols_list]

    for col in select_col_df.columns:
        if np.issubdtype(select_col_df[col], np.float16) or np.issubdtype(select_col_df[col], np.int16):
            select_col_df.loc[:, col] = select_col_df.loc[:, col].astype("float")

    if is_second_data(select_col_df["real_time"].head(2)):
        normal_data = select_col_df.set_index("real_time")
        normal_data.index = pd.to_datetime(normal_data.index)
        if len(select_col_df) > 60 * 60 * 24 * 30 * 3:
            # 从秒级降为10分钟级
            normal_data = normal_data.resample("10min").mean()

        elif len(select_col_df) > 60 * 60 * 24 * 30:
            # 从秒级降为1分钟级
            normal_data = normal_data.resample("1min").mean()

        elif len(select_col_df) > 60 * 60 * 24 * 7:
            # 从秒级降为30秒级
            normal_data = normal_data.resample("30S").mean()

        return normal_data

    return select_col_df

