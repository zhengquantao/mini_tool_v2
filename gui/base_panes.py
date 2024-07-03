import wx
import wx.aui
import wx.lib.agw.aui as aui

# If MainFrame subclasses wx.Frame, uncomment the following lines
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from gui.main_frame import MainFrame

from gui.aui_notebook_options_res import agw_tabart_provider

from gui.controls import SizeReportCtrl, TextCtrl, TreeCtrl, HTMLCtrl, GridCtrl
from gui.aui_notebook import Notebook
from gui.progress import ProgressGauge
from gui.base_panes_res import content_ctrls


# noinspection PyPep8Naming
from settings.settings import float_size


class PaneManager:
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
    mb_items: dict                       # menubar.items
    item_ids: dict[wx.WindowIDRef, str]  # menubar.item_ids

    # If MainFrame subclasses wx.Frame, replace the following line
    # def __init__(self, frame: "MainFrame", mgr: aui.AuiManager,
    #              menu_ids: dict[str, wx.WindowIDRef], html_ctrl: HTMLCtrl,
    #              text_ctrl: TextCtrl, tree_ctrl: TreeCtrl, grid_ctrl: GridCtrl,
    #              size_reporter: SizeReportCtrl, notebook_ctrl: Notebook) -> None:
    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager, mb_items: dict,
                 item_ids: dict[wx.WindowIDRef, str], html_ctrl: HTMLCtrl,
                 text_ctrl: TextCtrl, tree_ctrl: TreeCtrl, grid_ctrl: GridCtrl,
                 notebook_ctrl: Notebook) -> None:
        self.frame = frame
        self.mgr = mgr
        self.html_ctrl = html_ctrl
        self.text_ctrl = text_ctrl
        self.tree_ctrl = tree_ctrl
        self.grid_ctrl = grid_ctrl
        self.notebook_ctrl = notebook_ctrl

        self.mb_items = mb_items
        self.item_ids = item_ids

        self.bind_menu()

    def build_panes(self):
        notebook_ctrl: Notebook = self.notebook_ctrl
        # add a bunch of panes
        self.mgr.AddPane(notebook_ctrl.create_ctrl(), aui.AuiPaneInfo().Name("notebook_content").
                         CenterPane().PaneBorder(False).
                         FloatingSize(wx.Size(*float_size)).BestSize(*float_size).MinSize(*float_size))

        # Show how to add a control inside a tab
        notebook = self.mgr.GetPane("notebook_content").window
        # self.gauge = ProgressGauge(notebook, size=wx.Size(55, 15))
        # notebook.AddControlToPage(4, self.gauge)

        notebook_ctrl.main_notebook = notebook
        self.mgr.Update()

    def bind_menu(self):
        mb_items: dict = self.mb_items
        menu_refid: wx.WindowIDRef
        self.themes = {self.mb_items[key]["id"]: agw_tabart_provider[key] for key in agw_tabart_provider}
        for menu_refid in self.themes:
            self.frame.Bind(wx.EVT_MENU, self.on_notebook_theme, menu_refid)

        self.frame.Bind(wx.EVT_MENU, self.on_preview, id=mb_items["NotebookPreview"]["id"])

        self.frame.Bind(aui.EVT_AUI_PANE_CLOSE, self.on_pane_close)
        self.frame.Bind(aui.EVT_AUI_PANE_MINIMIZE, self.on_pane_min)

    def default_layout(self):
        self.mgr.GetPane("notebook_content").Show()
        self.mgr.Update()

    def on_preview(self, _event: wx.CommandEvent) -> None:
        nb: aui.AuiNotebook = self.mgr.GetPane("notebook_content").window
        nb.NotebookPreview()
        self.mgr.Update()

    def on_notebook_theme(self, event: wx.CommandEvent) -> None:
        """Update notebook theme (TabArt provider)."""
        event_id: wx.WindowIDRef = event.GetId()
        if self.notebook_ctrl.notebook_theme == self.themes[event_id]["rowid"]:
            return
        self.notebook_ctrl.notebook_theme = self.themes[event_id]["rowid"]
        art_provider = self.themes[event_id]["provider"]()

        nb: aui.AuiNotebook
        for nb in self.notebook_ctrl.all_notebooks():
            nb.SetArtProvider(art_provider)
            nb.Refresh()
            nb.Update()

    def on_delete(self, _event: wx.CommandEvent) -> None:
        pass

    def on_change_content_pane(self, event: wx.CommandEvent) -> None:
        ctrl_key: str
        pane_key: str
        ref_id: wx.WindowIDRef = event.GetId()
        for pane_key, ctrl_key in content_ctrls.items():
            self.mgr.GetPane(pane_key).Show(ref_id == self.mb_items[ctrl_key]["id"])
        self.mgr.Update()

    def on_pane_min(self, event: aui.AuiManagerEvent) -> None:

        if event.pane.name in ["ProjectTree", "Console", "Graph"]:
            event.pane.Hide()
            self.mgr.Update()
            event.Veto()
            return

    def on_pane_close(self, event: aui.AuiManagerEvent) -> None:
        # print(event.pane.name, event.GetEventType())
        # if not event.pane.name == "test10":
        #     return
        # self.mgr.GetPane(event.GetPane().window)
        # self.mgr.Update()
        if event.pane.name not in ["ProjectTree_min", "Console_min", "Graph_min"]:
            return

        # pane_info = event.GetPane()
        # self.mgr.Update()

        if event.GetEventType() == aui.wxEVT_AUI_PANE_MINIMIZE:
            action = "minimize"
        else:
            action = "close/hide"

        result = wx.MessageBox(f"Are you sure you want to {action} this pane?",
                               "MINI-TOOL", wx.YES_NO, self.frame)
        if result != wx.YES:
            event.Veto()
