import ctypes
import datetime
import inspect
import json
import logging
import os
import shutil
import time
from functools import wraps
import chardet

import numpy as np
import pandas as pd
import psutil
import wx
import wx.svg
import wx.lib.agw.aui as aui

from settings.settings import opening_dict, cols_titles, result_dir


def async_raise(thread_id, exctype, logger=logging):
    """
    通过C语言的库抛出异常
    :param thread_id:
    :param exctype:
    :return:
    """
    # 在子线程内部抛出一个异常结束线程
    thread_id = ctypes.c_long(thread_id)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(exctype))

    if res == 0:
        logger.info("线程id违法")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, None)
        logger.info("异常抛出失败")
    else:
        logger.info(f"线程：{thread_id},已停止")


def new_app(path):
    from multiprocessing import Process
    from main import run_gui
    app = Process(target=run_gui, args=(path,))
    app.start()


def daemon_app(app):
    current_process = psutil.Process()

    while len(current_process.children()) > 3:
        print("------------------")
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


def create_dir(factor_path):
    ret = os.path.join(factor_path, result_dir)
    os.makedirs(ret, exist_ok=True)
    return ret


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


def get_file_info(directory="."):
    res = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            res.append(os.path.join(root, name))
        for name in dirs:
            res.append(os.path.join(root, name))
    return res


def add_notebook_page(notebook_ctrl, html_ctrl, file_paths, file_name):
    page_bmp: wx.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
    ctrl = notebook_ctrl.notebook_object
    pid = os.getpid()
    opening_dict[pid]["records"][file_name] = file_paths
    ctrl.AddPage(html_ctrl.create_ctrl(parent=ctrl, path=file_paths), file_name, True, page_bmp)
    return ctrl


def common_cut(target_data, label, bin_label, start=0, step=0.25):
    bins = np.arange(start, np.ceil(target_data[label].max()), step)
    bins_labels = [x for x in bins[1:]]

    target_data[bin_label] = pd.cut(target_data[label], bins=bins, labels=bins_labels)
    return target_data


def detect_encoding(filename):
    with open(filename, 'rb') as file:
        rawdata = file.read(1000)
        encoding = chardet.detect(rawdata)['encoding']
        return encoding


def find_file_path(start_file, file_name=None, level=5):
    # 获取当前文件的路径
    current_path = os.path.dirname(start_file)
    i = 0
    while i < level:
        # 列出当前路径下的所有文件和文件夹
        files_and_dirs = os.listdir(current_path)

        # 检查是否存在名为'test.txt'的文件
        if file_name in files_and_dirs:
            return os.path.join(current_path, file_name)

        # 如果已经到达了根目录，则停止查找
        if os.path.dirname(current_path) == current_path:
            return None

        # 否则，继续在上一级目录中查找
        current_path = os.path.dirname(current_path)
        i += 1


def is_second_data(data_df):
    """
    判断是否是秒级数据
    """
    time_one, time_two = data_df[0], data_df[1]
    timestamp = int(time_two.timestamp()) - int(time_one.timestamp())
    if timestamp > 1:
        return False

    return True


def field_type_transform(data):
    # ** 3.4 数值类型转换 **
    data = data.set_index("real_time")
    data.index = pd.to_datetime(data.index)
    data.loc[:, "wind_speed"] = data.loc[:, "wind_speed"].astype("float")
    data.loc[:, "wind_direction"] = data.loc[:, "wind_direction"].astype("float")

    data.loc[:, "air_density"] = data.loc[:, "air_density"].astype("float")
    data.loc[:, "pitch_angle"] = data.loc[:, "pitch_angle"].astype("float")

    # data.loc[:, "nacelle_temperature"] = data.loc[:, "nacelle_temperature"].apply(lambda x: str(x).replace(",", ""))
    data.loc[:, "nacelle_temperature"] = data.loc[:, "nacelle_temperature"].astype("float")

    # data.loc[:, "power"] = data.loc[:, "power"].apply(lambda x: str(x).replace(",", ""))
    data.loc[:, "power"] = data.loc[:, "power"].astype("float")

    # data.loc[:, "generator_speed"] = data.loc[:, "generator_speed"].apply(lambda x: str(x).replace(",", ""))
    data.loc[:, "generator_speed"] = data.loc[:, "generator_speed"].astype("float")

    data["power"] = pd.to_numeric(data["power"])
    data["generator_speed"] = pd.to_numeric(data["generator_speed"])
    data["nacelle_temperature"] = pd.to_numeric(data["nacelle_temperature"])

    return data


def data_cleaning_by_pitchangle(dataset, power_value):
    """
    简单数据清洗
        功率与额定功率的比值< 0.7时，桨叶角度 <2;
        功率比值0,7-0.8，桨叶角度< 4;
        功率比值0.8-0.9，桨叶角度<6;
    """
    # *** ---------- 功率与额定功率的比值< 0.7时，桨叶角度 <2;----------
    dataset = dataset.drop(dataset[(dataset["power"] < power_value * 0.7) & (dataset["pitch_angle"] < 2)].index)
    # *** ---------- 功率比值0,7-0.8，桨叶角度< 4; ----------
    dataset = dataset.drop(dataset[(dataset["power"] >= power_value * 0.7) & (dataset["power"] < power_value * 0.8) &
                                   (dataset["pitch_angle"] < 4)].index)

    # *** ---------- 功率比值0.8-0.9，桨叶角度<6; ----------
    dataset = dataset.drop(dataset[(dataset["power"] >= power_value * 0.8) & (dataset["power"] < power_value * 0.9) &
                                   (dataset["pitch_angle"] < 6)].index)

    return dataset


def read_csv_file(file):
    cols_list = cols_titles.keys()
    data_frame = pd.read_csv(file, usecols=cols_list, encoding=detect_encoding(file))
    select_col_df = data_frame[cols_list]

    select_col_df = field_type_transform(select_col_df)

    # turbine_code是字符串，需要去掉turbine_code列，才能resample
    turbine_code = select_col_df["turbine_code"][0]
    select_col_df = select_col_df.iloc[:, 1:]

    if is_second_data(select_col_df.index):

        if len(select_col_df) > 60 * 60 * 24 * 30 * 3:
            # 从3个月秒级降为10分钟级
            select_col_df = select_col_df.resample("10min").mean()

        elif len(select_col_df) > 60 * 60 * 24 * 30:
            # 从30天秒级降为1分钟级
            select_col_df = select_col_df.resample("1min").mean()

        elif len(select_col_df) > 60 * 60 * 24 * 7:
            # 从7天秒级降为30秒级
            select_col_df = select_col_df.resample("30S").mean()

    else:
        if len(select_col_df) > 60 * 24 * 365:
            # 一年分钟级将为10分钟级
            select_col_df = select_col_df.resample("10min").mean()
    # 加上turbine_code列
    select_col_df.insert(loc=0, column='turbine_code', value=turbine_code)
    return select_col_df

