import json
import os
import shutil

import wx
import wx.aui
import wx.lib.agw.aui as aui
from aui2 import svg_to_bitmap
from pubsub import pub as publisher

from settings import settings as cs
from common.loggers import logger
from common.common import read_file, new_app


# noinspection PyPep8Naming
from settings.settings import opening_dict, exit_svg, rop_svg


class FileManager:
    """Creates default panes."""

    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager, menubar, html_ctrl,
                 text_ctrl, tree_ctrl, grid_ctrl, notebook_ctrl, graph_ctrl, project_path=None) -> None:
        self.frame = frame
        self.mgr = mgr
        self.html_ctrl = html_ctrl
        self.text_ctrl = text_ctrl
        self.tree_ctrl = tree_ctrl
        self.grid_ctrl = grid_ctrl
        self.graph_ctrl = graph_ctrl
        self.notebook_ctrl = notebook_ctrl

        # self.timer = wx.Timer(frame)
        # frame.Bind(wx.EVT_TIMER, self.on_timer)
        # self.timer.Start(100)
        self.menubar = menubar
        self.mb_items = menubar.items
        self.item_ids = menubar.item_ids
        self.init = False
        # self.init_maps()
        # self.init_ui_state()
        self.bind_menu()
        wx.CallLater(500, self.load_recent_project, project_path)
        # self.load_recent_project(project_path)

    # def __del__(self):
    #     self.timer.Stop()

    def bind_menu(self):
        mb_items: dict = self.mb_items
        menu_refid: wx.WindowIDRef
        ctrl_key: str
        self.file_history()
        mb_items["File"].AppendSeparator()
        exit_menu = mb_items["File"].Append(wx.ID_EXIT, "退出\tAlt-F4")
        exit_menu.SetBitmap(svg_to_bitmap(exit_svg, size=(15, 15)))
        # File
        self.frame.Bind(wx.EVT_MENU, self.on_new_project, id=mb_items["NewProject"]["id"])
        self.frame.Bind(wx.EVT_MENU, self.on_open_project, id=mb_items["OpenProject"]["id"])
        self.frame.Bind(wx.EVT_MENU, self.on_open_file, id=mb_items["OpenFile"]["id"])
        self.frame.Bind(wx.EVT_MENU, self.on_save_project, id=mb_items["SaveProject"]["id"])
        self.frame.Bind(wx.EVT_MENU_RANGE, self.recent_project, id=wx.ID_FILE1, id2=wx.ID_FILE9)
        self.frame.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)

    def file_history(self):
        # 创建 FileHistory 对象
        self.filehistory = wx.FileHistory(8)
        self.config = wx.Config(cs.main_title, style=wx.CONFIG_USE_LOCAL_FILE)
        self.filehistory.Load(self.config)
        recent = wx.Menu()
        self.filehistory.UseMenu(recent)
        self.filehistory.AddFilesToMenu()
        rop_menu = self.mb_items["File"].Append(wx.ID_ANY, '&最近打开项目', recent)
        rop_menu.SetBitmap(svg_to_bitmap(rop_svg, size=(15, 15)))

    def add_history(self, path: str):
        # 将项目路径添加到 FileHistory 中
        self.filehistory.AddFileToHistory(path)
        self.filehistory.Save(self.config)
        self.config.Flush()

    def open_project(self, path: str, init_project=False):
        pid = os.getpid()
        logger.info(f"当前进程号：{pid}")
        opening_dict[pid] = {"path": path, "records": {}}
        self.mgr.AddPane(self.tree_ctrl.create_ctrl(path, init_project=init_project),
                         aui.AuiPaneInfo().Name("ProjectTree").Caption("" if init_project else path).
                         CloseButton(False).MaximizeButton(False).Layer(2).Position(1).Left().
                         MinimizeButton(True).Movable(False).Floatable(False).
                         Icon(svg_to_bitmap(cs.tree_svg, size=(13, 13))))
        self.mgr.AddPane(self.graph_ctrl.create_ctrl(), aui.AuiPaneInfo().
                         Name("Graph").Caption("Graph").Layer(1).Position(1).
                         Left().Floatable(False).CloseButton(False).Hide().Minimize().
                         MaximizeButton(False).MinimizeButton(True).Icon(svg_to_bitmap(cs.graph_svg, size=(13, 13))))
        self.mgr.Update()

        data = read_file(os.path.join(path, ".mini"))
        if not data:
            return
        try:
            history_obj = json.loads(data)
            for file_path in history_obj.get("file_path", []):
                self.tree_ctrl.on_open("", file_path)
        except:
            pass

    def load_recent_project(self, path):
        if path:
            wx.CallAfter(publisher.sendMessage, "send_project_path", path=path)
            self.open_project(path)
            return
        recent_project_path = self.get_recent_project_path()
        if recent_project_path:
            try:
                wx.CallAfter(publisher.sendMessage, "send_project_path", path=recent_project_path)
                self.open_project(recent_project_path)
                return
            except Exception as e:
                pass
        self.init = True
        project_path = os.getcwd()
        wx.CallAfter(publisher.sendMessage, "send_project_path", path=project_path)
        self.open_project(project_path, init_project=True)

    def get_recent_project_path(self) -> str:

        if not self.filehistory.GetCount():
            self.project_path = os.getcwd()
            return ""

        self.project_path = self.filehistory.GetHistoryFile(0)
        return self.project_path

    def on_new_project(self, event: wx.CommandEvent) -> None:
        dlg = wx.TextEntryDialog(self.frame, "请输入项目名:", "新建项目")
        if dlg.ShowModal() != wx.ID_OK:
            return

        directory_name: str = dlg.GetValue()
        select_dialog = wx.DirDialog(self.frame, "请选择项目保存路径：", style=wx.DD_DEFAULT_STYLE)
        if select_dialog.ShowModal() != wx.ID_OK:
            return

        path = os.path.join(select_dialog.GetPath(), directory_name)
        logger.info(f"Chosen directory: {path}")
        os.makedirs(path)
        self.add_history(path)

        new_app(path)
        # self.open_project(path)
        if self.init:
            # self.frame.Close(True)
            self.frame.Destroy()

    def on_open_project(self, event: wx.CommandEvent) -> None:
        select_dialog = wx.DirDialog(self.frame, "请选择要打开的项目：", style=wx.DD_DEFAULT_STYLE)
        if select_dialog.ShowModal() != wx.ID_OK:
            return

        path = select_dialog.GetPath()
        logger.info(f"Chosen directory: {path}")
        self.add_history(path)
        new_app(path)

        if self.init:
            # self.frame.Close(True)
            self.frame.Destroy()

        # self.open_project(path)

    def on_open_file(self, event: wx.CommandEvent) -> None:
        select_dialog = wx.FileDialog(self.frame, "请选择要打开的文件：", style=wx.DD_DEFAULT_STYLE)
        if select_dialog.ShowModal() != wx.ID_OK:
            return

        path = select_dialog.GetPath()
        logger.info(f"Chosen directory: {path}")
        self.tree_ctrl.on_open(event, path)

    def on_save_project(self, event: wx.CommandEvent) -> None:
        select_dialog = wx.DirDialog(self.frame, "请选择要保存的路径：", style=wx.DD_DEFAULT_STYLE)
        if select_dialog.ShowModal() != wx.ID_OK:
            return

        path = select_dialog.GetPath()
        logger.info(f"Chosen directory: {path}")
        filepath = self.project_path.split(os.sep)[-1]
        path = os.path.join(path, filepath)
        shutil.copytree(self.project_path, path, dirs_exist_ok=True)

    def recent_project(self, event: wx.CommandEvent) -> None:
        file_num = event.GetId() - wx.ID_FILE1
        path = self.filehistory.GetHistoryFile(file_num)
        self.filehistory.AddFileToHistory(path)
        self.add_history(path)
        # reopen project
        new_app(path)
        # self.open_project(path)

    def on_exit(self, _event: wx.CommandEvent) -> None:
        # save_mini_file(self.mgr)
        # dlg = wx.MessageDialog(self.frame, f"你确认要退出吗？", "警告", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        # if dlg.ShowModal() != wx.ID_YES:
        #     return
        self.frame.Close(True)

    def on_timer(self, _event: wx.TimerEvent) -> None:
        try:
            self.gauge.Pulse()
        except:
            self.timer.Stop()
            raise