import os
from multiprocessing import freeze_support, Process

import wx
import wx.lib.agw.aui as aui
from aui2 import svg_to_bitmap

from common.common import daemon_app
from common import loggers
from gui.graph_panel import GraphPanel
from html_server import run_server
from gui.toolbars import ToolBarManager
from settings import settings as cs
from gui.file_menu import FileManager
from gui.main_frame import MainFrame
from gui.main_menu import MainMenu
from gui.controls import TextCtrl, TreeCtrl, HTMLCtrl, GridCtrl, LogCtrl
from gui.aui_notebook import Notebook
# from gui.aui_notebook_options import NotebookOptions
# from gui.aui_manager_options import ManagerOptions
# from gui.aui_dockart_options import DockArtOptions
from gui.base_panes import PaneManager
# from gui.perspective import LayoutManager
from gui.gui import SettingsPanel


class MainApp:

    def __init__(self, project_path=None):
        self.app = wx.App(False)
        self.on_init(project_path)

    # If subclassing wx.App, remove this method.
    def main_loop(self):
        self.app.MainLoop()

    def on_init(self, project_path=None):
        # If subclassing wx.App, this methods is envoked automatically by the framework.
        mgr: aui.AuiManager = aui.AuiManager()

        # If MainFrame subclasses wx.Frame and MainFrame().frame is not set to self,
        # remove the second line and rename main_frame -> frame.
        main_frame: MainFrame = MainFrame(None, wx.ID_ANY, cs.main_title, size=wx.Size(*cs.window_size))

        # set icon
        icon = wx.Icon()
        icon.CopyFromBitmap(svg_to_bitmap(cs.icon_svg))
        main_frame.frame.SetIcon(icon)
        frame: wx.Frame = main_frame.frame

        mgr.SetManagedWindow(frame)  # tell FrameManager to manage this frame

        menubar = MainMenu(frame, mgr)
        # 注释侧边栏
        tbman: ToolBarManager = ToolBarManager(frame, mgr)
        # popup: PopupMenu = PopupMenu(frame)
        # popup.bind_DropDownToolbarItem(tbman.items["DropDownToolbarItem"]["id"])

        # id_size_report_ctrl: wx.WindowIDRef = wx.WindowIDRef()
        # size_reporter: SizeReportCtrl = SizeReportCtrl(frame, mgr, id_size_report_ctrl)
        id_text_ctrl: wx.WindowIDRef = wx.WindowIDRef()
        text_ctrl: TextCtrl = TextCtrl(frame, mgr, id_text_ctrl)
        id_html_ctrl: wx.WindowIDRef = wx.WindowIDRef()
        html_ctrl: HTMLCtrl = HTMLCtrl(frame, mgr, id_html_ctrl)
        id_grid_ctrl: wx.WindowIDRef = wx.WindowIDRef()
        grid_ctrl: GridCtrl = GridCtrl(frame, mgr, id_grid_ctrl)
        id_notebook_ctrl: wx.WindowIDRef = wx.WindowIDRef()
        notebook_ctrl: Notebook = Notebook(frame, mgr, id_notebook_ctrl, html_ctrl)
        id_tree_ctrl: wx.WindowIDRef = wx.WindowIDRef()
        graph_ctrl = GraphPanel(frame, notebook_ctrl, html_ctrl)
        tree_ctrl: TreeCtrl = TreeCtrl(frame, mgr, id_tree_ctrl, notebook_ctrl, html_ctrl, grid_ctrl, graph_ctrl)
        # init log
        loggers.logger = loggers.init_log(LogCtrl(frame, mgr))
        loggers.logger.info("正在运行中....")
        # _notebook_options: NotebookOptions = NotebookOptions(
        #     frame, mgr, notebook_ctrl, menubar.items, menubar.item_ids)
        # _manager_options: ManagerOptions = ManagerOptions(
        #     frame, mgr, menubar.items, menubar.item_ids)
        # _dockart_options: DockArtOptions = DockArtOptions(
        #     frame, mgr, menubar.items, menubar.item_ids)

        paneman: PaneManager = PaneManager(
            frame, mgr, menubar.items, menubar.item_ids, html_ctrl, text_ctrl,
            tree_ctrl, grid_ctrl, notebook_ctrl)
        paneman.build_panes()
        # paneman.request_menu()
        # layman: LayoutManager = LayoutManager(frame, mgr, menubar.items)
        # layman.save("All Panes")
        # paneman.default_layout()
        # layman.save("Default Startup")
        setman: SettingsPanel = SettingsPanel(frame, mgr)
        # setman.build_panel(menubar.items)

        file_manager: FileManager = FileManager(
            frame, mgr, menubar, html_ctrl, text_ctrl,
            tree_ctrl, grid_ctrl, notebook_ctrl, graph_ctrl, project_path)

        main_frame.init_man(mgr)
        frame.CenterOnScreen()
        frame.Show()
        return True


def run_gui(project_path=None):
    app = MainApp(project_path)
    app.main_loop()


def main():
    web = Process(target=run_server)
    web.start()
    Process(target=run_gui).start()
    daemon_app(web, ppid=os.getpid())


if __name__ == "__main__":
    freeze_support()
    main()
