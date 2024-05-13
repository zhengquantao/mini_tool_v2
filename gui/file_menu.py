import json
import os
import shutil

import wx
import wx.aui
import wx.lib.agw.aui as aui
from aui2 import svg_to_bitmap

from settings import settings as cs
from common.common import read_file, new_app, save_mini_file
from gui.controls import SizeReportCtrl, TextCtrl, TreeCtrl, HTMLCtrl, GridCtrl
from gui.aui_notebook import Notebook
from gui.main_menu import MainMenu
from gui.progress import ProgressGauge


# noinspection PyPep8Naming
from settings.settings import opening_dict


class FileManager:
    """Creates default panes."""

    # If MainFrame subclasses wx.Frame, replace the following line
    # frame: "MainFrame"
    frame: wx.Frame

    mgr: aui.AuiManager
    html_ctrl: HTMLCtrl
    text_ctrl: TextCtrl
    tree_ctrl: TreeCtrl
    grid_ctrl: GridCtrl
    size_reporter: SizeReportCtrl
    notebook_ctrl: Notebook
    timer: wx.Timer
    gauge: ProgressGauge
    min_mode: int = aui.AUI_MINIMIZE_POS_SMART
    veto_tree: bool = False
    veto_text: bool = False
    transparency: int = 255
    snapped: bool = False
    captions: dict
    req_pane_ids: dict[wx.WindowIDRef, str]
    flags: dict[wx.WindowIDRef, int]     # <menu_ref_id> -> min mode flag
    menubar: MainMenu
    mb_items: dict                       # menubar.items
    item_ids: dict[wx.WindowIDRef, str]  # menubar.item_ids

    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager, menubar: MainMenu, html_ctrl: HTMLCtrl,
                 text_ctrl: TextCtrl, tree_ctrl: TreeCtrl, grid_ctrl: GridCtrl, notebook_ctrl: Notebook,
                 size_reporter: SizeReportCtrl, project_path=None) -> None:
        self.frame = frame
        self.mgr = mgr
        self.html_ctrl = html_ctrl
        self.text_ctrl = text_ctrl
        self.tree_ctrl = tree_ctrl
        self.grid_ctrl = grid_ctrl
        self.notebook_ctrl = notebook_ctrl
        self.size_reporter = size_reporter

        # self.timer = wx.Timer(frame)
        # frame.Bind(wx.EVT_TIMER, self.OnTimer)
        # self.timer.Start(100)
        self.menubar = menubar
        self.mb_items = menubar.items
        self.item_ids = menubar.item_ids
        # self.init_maps()
        # self.init_ui_state()
        self.bind_menu()
        self.load_recent_project(project_path)

    # def __del__(self):
    #     self.timer.Stop()

    def bind_menu(self):
        mb_items: dict = self.mb_items
        menu_refid: wx.WindowIDRef
        ctrl_key: str
        self.file_history()
        mb_items["File"].Append(wx.ID_EXIT, "E&xit\tAlt-F4")

        # File
        self.frame.Bind(wx.EVT_MENU, self.OnNewProject, id=mb_items["NewProject"]["id"])
        self.frame.Bind(wx.EVT_MENU, self.OnOpenProject, id=mb_items["OpenProject"]["id"])
        self.frame.Bind(wx.EVT_MENU, self.OnOpenFile, id=mb_items["OpenFile"]["id"])
        self.frame.Bind(wx.EVT_MENU, self.OnSaveProject, id=mb_items["SaveProject"]["id"])
        self.frame.Bind(wx.EVT_MENU_RANGE, self.RecentProject, id=wx.ID_FILE1, id2=wx.ID_FILE9)
        self.frame.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)

    def file_history(self):
        # 创建 FileHistory 对象
        self.filehistory = wx.FileHistory(8)
        self.config = wx.Config(cs.main_title, style=wx.CONFIG_USE_LOCAL_FILE)
        self.filehistory.Load(self.config)
        recent = wx.Menu()
        self.filehistory.UseMenu(recent)
        self.filehistory.AddFilesToMenu()
        self.mb_items["File"].Append(wx.ID_ANY, '&Recent Project', recent)

    def add_history(self, path: str):
        # 将项目路径添加到 FileHistory 中
        self.filehistory.AddFileToHistory(path)
        self.filehistory.Save(self.config)
        self.config.Flush()

    def open_project(self, path: str):
        pid = os.getpid()
        print(f"当前进程号：{pid}")
        opening_dict[pid] = {"path": path, "records": {}}
        self.mgr.AddPane(self.tree_ctrl.create_ctrl(path), aui.AuiPaneInfo().Name("ProjectTree").Caption(path).
                         CloseButton(False).MaximizeButton(False).
                         MinimizeButton(True).Movable(False).Floatable(False).
                         Icon(svg_to_bitmap(cs.tree_svg, size=(20, 20))))
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
            self.open_project(path)
            return
        recent_project_path = self.get_recent_project_path()
        if recent_project_path:
            try:
                self.open_project(recent_project_path)
                return
            except Exception as e:
                pass
        self.open_project(os.getcwd())

    def get_recent_project_path(self) -> str:

        if not self.filehistory.GetCount():
            self.project_path = os.getcwd()
            return self.project_path

        self.project_path = self.filehistory.GetHistoryFile(0)
        return self.project_path

    def OnNewProject(self, event: wx.CommandEvent) -> None:
        dlg = wx.TextEntryDialog(self.frame, "请输入项目名:", "新建项目")
        if dlg.ShowModal() != wx.ID_OK:
            return

        directory_name: str = dlg.GetValue()
        select_dialog = wx.DirDialog(self.frame, "请选择文件保存路径：", style=wx.DD_DEFAULT_STYLE)
        if select_dialog.ShowModal() != wx.ID_OK:
            return

        path = os.path.join(select_dialog.GetPath(), directory_name)
        print(f"Chosen directory: {path}")
        os.makedirs(path)
        self.add_history(path)

        new_app(path)
        # self.open_project(path)

    def OnOpenProject(self, event: wx.CommandEvent) -> None:
        select_dialog = wx.DirDialog(self.frame, "请选择要打开的项目：", style=wx.DD_DEFAULT_STYLE)
        if select_dialog.ShowModal() != wx.ID_OK:
            return

        path = select_dialog.GetPath()
        print(f"Chosen directory: {path}")
        self.add_history(path)
        new_app(path)
        # self.open_project(path)

    def OnOpenFile(self, event: wx.CommandEvent) -> None:
        select_dialog = wx.FileDialog(self.frame, "请选择要打开的文件：", style=wx.DD_DEFAULT_STYLE)
        if select_dialog.ShowModal() != wx.ID_OK:
            return

        path = select_dialog.GetPath()
        print(f"Chosen directory: {path}")
        self.tree_ctrl.on_open(event, path)

    def OnSaveProject(self, event: wx.CommandEvent) -> None:
        select_dialog = wx.DirDialog(self.frame, "请选择要保存的路径：", style=wx.DD_DEFAULT_STYLE)
        if select_dialog.ShowModal() != wx.ID_OK:
            return

        path = select_dialog.GetPath()
        print(f"Chosen directory: {path}")
        filepath = self.project_path.split(os.sep)[-1]
        path = os.path.join(path, filepath)
        shutil.copytree(self.project_path, path, dirs_exist_ok=True)

    def RecentProject(self, event: wx.CommandEvent) -> None:
        file_num = event.GetId() - wx.ID_FILE1
        path = self.filehistory.GetHistoryFile(file_num)
        self.filehistory.AddFileToHistory(path)
        self.add_history(path)
        # reopen project
        new_app(path)
        # self.open_project(path)

    def OnExit(self, _event: wx.CommandEvent) -> None:
        save_mini_file(self.mgr)
        dlg = wx.MessageDialog(self.frame, f"你确认要退出吗？", "警告", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        if dlg.ShowModal() != wx.ID_YES:
            return

        self.frame.Destroy()

    def OnTimer(self, _event: wx.TimerEvent) -> None:
        try:
            self.gauge.Pulse()
        except:
            self.timer.Stop()
            raise