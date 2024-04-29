import datetime
import json
import os
import shutil
import time
from functools import wraps

import psutil
import wx
import wx.svg
import wx.lib.agw.aui as aui

from settings.settings import opening_dict


def new_app(path):
    from multiprocessing import Process
    from main import main
    app = Process(target=main, args=(path,))
    app.start()


def daemon_app():
    current_process = psutil.Process()

    while len(current_process.children()) > 2:
        time.sleep(3)


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
    if os.path.isfile(path):
        os.remove(path)
        return

    shutil.rmtree(path)


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


