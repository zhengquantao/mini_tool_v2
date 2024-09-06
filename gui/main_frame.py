"""Creates application main frame.

When not subclassing wx.Frame, this code can be merged into main.py. Otherwise,
this module should remain separate to let other components import it for type
checking purposes.
"""
import os

import wx
import wx.aui
import wx.lib.agw.aui as aui
from pubsub import pub as publisher
import psutil


# noinspection PyPep8Naming
from common.common import save_mini_file


class MainFrame:

    def __init__(self, parent: wx.Window, win_id: wx.WindowIDRef = wx.ID_ANY,
                 title: str = "", pos: wx.Point = wx.DefaultPosition, size: wx.Size = wx.DefaultSize,
                 style: int = wx.DEFAULT_FRAME_STYLE, app=None) -> None:
        # If subclassing wx.Frame, uncomment the next line
        # super().__init__(parent, win_id, title, pos, size, style)
        # If subclassing wx.Frame, remove the next line or set it to self
        self.frame = wx.Frame(parent, win_id, title, pos, size, style)
        publisher.subscribe(self.send_future, "send_future")
        self.frame.Maximize(True)
        self.frame.Bind(wx.EVT_CLOSE, self.on_exit)
        self.future_pid_list = []
        self.app = app

    def send_future(self, msg):
        self.future_pid_list.extend(msg)

    def init_man(self, mgr: aui.AuiManager) -> None:
        self.mgr = mgr
        self.frame.Bind(wx.EVT_SIZE, self.on_size)

        # ----- STATUSBAR ----- #
        # If subclassing wx.Frame, remove .frame, if self.frame is not set to self
        statusbar: wx.StatusBar = self.frame.CreateStatusBar(2, wx.STB_SIZEGRIP)
        statusbar.SetStatusWidths([-2, -3])
        statusbar.SetStatusText("开始", 0)
        statusbar.SetStatusText("欢迎使用能效评估助手!", 1)

    def on_size(self, event):
        wx.CallLater(100, self.frame.Update)
        wx.CallLater(300, self.mgr.Update)
        # event.Skip(False)
        return

    def kill_process(self):
        parent_process_name = psutil.Process(os.getpid()).name()
        for future_pid in self.future_pid_list:
            try:
                process = psutil.Process(future_pid)
                process.name() == parent_process_name and process.terminate()
            except:
                pass

    # If subclassing wx.Frame, uncomment the following lines and
    # remove .frame, if self.frame is not set to self
    def on_exit(self, _event: wx.CloseEvent) -> None:
        save_mini_file(self.mgr)
        dlg = wx.MessageDialog(self.frame, f"你确认要退出吗？", "警告", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        if dlg.ShowModal() != wx.ID_YES:
            _event.Veto()
            return
        self.kill_process()
        self.frame.Destroy()
        self.app.OnExit()
        # import sys
        # sys.exit()
        # self.frame.Close(True)
