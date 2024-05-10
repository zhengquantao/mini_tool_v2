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
