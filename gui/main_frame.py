"""Creates application main frame.

When not subclassing wx.Frame, this code can be merged into main.py. Otherwise,
this module should remain separate to let other components import it for type
checking purposes.
"""

import wx
import wx.aui
import wx.lib.agw.aui as aui


# noinspection PyPep8Naming
from common.common import save_mini_file


class MainFrame:

    def __init__(self, parent: wx.Window, win_id: wx.WindowIDRef = wx.ID_ANY,
                 title: str = "", pos: wx.Point = wx.DefaultPosition, size: wx.Size = wx.DefaultSize,
                 style: int = wx.DEFAULT_FRAME_STYLE) -> None:
        # If subclassing wx.Frame, uncomment the next line
        # super().__init__(parent, win_id, title, pos, size, style)
        # If subclassing wx.Frame, remove the next line or set it to self
        self.frame = wx.Frame(parent, win_id, title, pos, size, style)
        self.frame.Maximize(True)
        self.frame.Bind(wx.EVT_CLOSE, self.on_exit)

    def init_man(self, mgr: aui.AuiManager) -> None:
        self.mgr = mgr
        self.frame.Bind(wx.EVT_SIZE, self.on_size)

        # ----- STATUSBAR ----- #
        # If subclassing wx.Frame, remove .frame, if self.frame is not set to self
        statusbar: wx.StatusBar = self.frame.CreateStatusBar(2, wx.STB_SIZEGRIP)
        statusbar.SetStatusWidths([-2, -3])
        statusbar.SetStatusText("Ready", 0)
        statusbar.SetStatusText("Welcome To MINI-TOOL!", 1)

    def on_size(self, event):
        wx.CallLater(100, self.frame.Update)
        wx.CallLater(300, self.mgr.Update)
        # event.Skip(False)
        return

    # If subclassing wx.Frame, uncomment the following lines and
    # remove .frame, if self.frame is not set to self
    def on_exit(self, _event: wx.CloseEvent) -> None:
        save_mini_file(self.mgr)
        dlg = wx.MessageDialog(self.frame, f"你确认要退出吗？", "警告", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        if dlg.ShowModal() != wx.ID_YES:
            _event.Veto()
            return
        self.frame.Destroy()
        # import sys
        # sys.exit()
        # self.frame.Close(True)
