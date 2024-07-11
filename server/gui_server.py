import wx
import wx.lib.agw.aui as aui
from aui2 import svg_to_bitmap

from gui.graph_panel import GraphPanel
from gui.toolbars import ToolBarManager

from gui.file_menu import FileManager
from gui.main_frame import MainFrame
from gui.main_menu import MainMenu
from gui.controls import TextCtrl, TreeCtrl, HTMLCtrl, GridCtrl, LogCtrl
from gui.aui_notebook import Notebook
from gui.base_panes import PaneManager
from gui.gui import SettingsPanel
from settings.settings import main_title, window_size, icon_svg, log_path


class MainApp:

    def __init__(self, project_path=None):
        self.app = wx.App(True, log_path)
        self.on_init(project_path)

    # If subclassing wx.App, remove this method.
    def main_loop(self):
        self.app.MainLoop()

    def on_init(self, project_path=None):
        # If subclassing wx.App, this methods is envoked automatically by the framework.
        mgr: aui.AuiManager = aui.AuiManager()

        # If MainFrame subclasses wx.Frame and MainFrame().frame is not set to self,
        # remove the second line and rename main_frame -> frame.
        main_frame: MainFrame = MainFrame(None, wx.ID_ANY, main_title, size=wx.Size(*window_size))

        # set icon
        icon = wx.Icon()
        icon.CopyFromBitmap(svg_to_bitmap(icon_svg))
        main_frame.frame.SetIcon(icon)
        frame: wx.Frame = main_frame.frame

        mgr.SetManagedWindow(frame)  # tell FrameManager to manage this frame

        menubar = MainMenu(frame, mgr)
        # 注释侧边栏
        tbman: ToolBarManager = ToolBarManager(frame, mgr)
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
        log_ctrl: LogCtrl = LogCtrl(frame, mgr)
        paneman: PaneManager = PaneManager(
            frame, mgr, menubar.items, menubar.item_ids, html_ctrl, text_ctrl,
            tree_ctrl, grid_ctrl, notebook_ctrl)
        setman: SettingsPanel = SettingsPanel(frame, mgr)
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