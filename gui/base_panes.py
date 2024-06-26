import random
# import keyboard
import wx
import wx.aui
import wx.lib.agw.aui as aui
import wx.lib.embeddedimage as ei
from aui2 import svg_to_bitmap
from wx.lib.agw.aui import aui_switcherdialog as asd

# If MainFrame subclasses wx.Frame, uncomment the following lines
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from gui.main_frame import MainFrame
from common import loggers
# from common.common import add_notebook_page
# from graph import simple_chart
from gui.aui_notebook_options_res import agw_tabart_provider
# from gui.simple_dialog import SimpleDialog
from settings import resources as res
from settings import settings as cs
from gui.controls import SizeReportCtrl, TextCtrl, TreeCtrl, HTMLCtrl, GridCtrl
from gui.aui_notebook import Notebook
from gui.progress import ProgressGauge
from gui.base_panes_res import (
    minimize_mode_flags as min_mode_flags, minimize_mode_flag_masks as min_mode_masks,
    default_checked_menus as checked_menus, content_ctrls)


# noinspection PyPep8Naming
from settings.settings import float_size, opening_dict


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

        # self.timer = wx.Timer(frame)
        # frame.Bind(wx.EVT_TIMER, self.OnTimer)
        # self.timer.Start(100)

        self.mb_items = mb_items
        self.item_ids = item_ids
        # self.init_maps()
        # self.init_ui_state()
        self.bind_menu()

    # def __del__(self):
    #     self.timer.Stop()

    def init_maps(self):
        """Generate mappings for source identification in event handlers."""
        key: str
        self.flags = {self.mb_items[key]["id"]: min_mode_flags[key] for key in min_mode_flags}

    def init_ui_state(self):
        """Sets menu items according to default startup state."""
        key: str
        menu_item: wx.MenuItem
        for key in checked_menus:
            menu_item = self.mb_items[key]["item"]
            menu_item.Check()

    def build_panes(self):
        tree_ctrl: TreeCtrl = self.tree_ctrl
        html_ctrl: HTMLCtrl = self.html_ctrl
        text_ctrl: TextCtrl = self.text_ctrl
        grid_ctrl: GridCtrl = self.grid_ctrl
        notebook_ctrl: Notebook = self.notebook_ctrl
        # add a bunch of panes
        # self.mgr.AddPane(size_reporter.create_ctrl(), aui.AuiPaneInfo().
        #                  Name("test1").Caption("Pane Caption").Top().MinimizeButton(True))
        #
        # self.mgr.AddPane(size_reporter.create_ctrl(), aui.AuiPaneInfo().
        #                  Name("test2").Caption("Client Size Reporter").
        #                  Bottom().Position(1).CloseButton(True).MaximizeButton(True).
        #                  MinimizeButton(True).CaptionVisible(True, left=True))
        #
        # self.mgr.AddPane(size_reporter.create_ctrl(), aui.AuiPaneInfo().
        #                  Name("test3").Caption("Client Size Reporter").
        #                  Bottom().CloseButton(True).MaximizeButton(True).MinimizeButton(True).
        #                  CaptionVisible(True, left=True))
        #
        # self.mgr.AddPane(size_reporter.create_ctrl(), aui.AuiPaneInfo().
        #                  Name("test4").Caption("Pane Caption").Left())
        #
        # self.mgr.AddPane(size_reporter.create_ctrl(), aui.AuiPaneInfo().
        #                  Name("test5").Caption("No Close Button").Right().CloseButton(False))
        #
        # self.mgr.AddPane(size_reporter.create_ctrl(), aui.AuiPaneInfo().
        #                  Name("test6").Caption("Client Size Reporter").Right().Row(1).
        #                  CloseButton(True).MaximizeButton(True).MinimizeButton(True))
        #
        # self.mgr.AddPane(size_reporter.create_ctrl(), aui.AuiPaneInfo().
        #                  Name("test7").Caption("Client Size Reporter").Left().Layer(1).
        #                  CloseButton(True).MaximizeButton(True).MinimizeButton(True))

        # self.mgr.AddPane(tree_ctrl.create_ctrl(), aui.AuiPaneInfo().Name("test8").Caption("Project").
        #                  Left().Layer(1).Position(1).CloseButton(False).MaximizeButton(True).
        #                  MinimizeButton(True))

        # self.mgr.AddPane(size_reporter.create_ctrl(), aui.AuiPaneInfo().
        #                  Name("test9").Caption("Min Size 200x100").
        #                  BestSize(wx.Size(200, 100)).MinSize(wx.Size(200, 100)).Bottom().Layer(1).
        #                  CloseButton(True).MaximizeButton(True).MinimizeButton(True))

        self.mgr.AddPane(loggers.logger_frame, aui.AuiPaneInfo().
                         Name("Console").Caption("Console").Hide().
                         Bottom().Layer(1).Position(1).Floatable(False).CloseButton(False).
                         MaximizeButton(False).MinimizeButton(True).Icon(svg_to_bitmap(cs.console_svg, size=(20, 18))))

        # wnd10 = text_ctrl.create_ctrl("This pane will prompt the user before hiding.")
        # self.mgr.AddPane(wnd10, aui.AuiPaneInfo().
        #                  Name("test10").Caption("Text Pane with Hide Prompt").
        #                  Bottom().MinimizeButton(True), target=self.mgr.GetPane("Console"))

        # self.mgr.AddPane(tree_ctrl.create_ctrl(), aui.AuiPaneInfo().
        #                  Name("thirdauto").Caption("A Third Auto-NB Pane").
        #                  Bottom().CloseButton(False).MaximizeButton(True).MinimizeButton(True),
        #                  target=self.mgr.GetPane("Console"))

        # self.mgr.AddPane(size_reporter.create_ctrl(), aui.AuiPaneInfo().
        #                  Name("test11").Caption("Fixed Pane").
        #                  Bottom().Layer(1).Position(2).Fixed().MinimizeButton(True))

        # create some center panes
        # self.mgr.AddPane(grid_ctrl.create_ctrl(), aui.AuiPaneInfo().Name("grid_content").
        #                  CenterPane().Hide().MinimizeButton(True))
        #
        # self.mgr.AddPane(tree_ctrl.create_ctrl(), aui.AuiPaneInfo().Name("tree_content").
        #                  CenterPane().Hide().MinimizeButton(True))
        #
        # self.mgr.AddPane(size_reporter.create_ctrl(), aui.AuiPaneInfo().Name("sizereport_content").
        #                  CenterPane().Hide().MinimizeButton(True))

        # self.mgr.AddPane(text_ctrl.create_ctrl(), aui.AuiPaneInfo().Name("text_content").
        #                  CenterPane().Hide().MinimizeButton(True))

        # self.mgr.AddPane(html_ctrl.create_ctrl(), aui.AuiPaneInfo().Name("html_content").
        #                  CenterPane().Hide().MinimizeButton(True))

        self.mgr.AddPane(notebook_ctrl.create_ctrl(), aui.AuiPaneInfo().Name("notebook_content").
                         CenterPane().PaneBorder(False).
                         FloatingSize(wx.Size(*float_size)).BestSize(*float_size).MinSize(*float_size))

        # Show how to add a control inside a tab
        notebook = self.mgr.GetPane("notebook_content").window
        # self.gauge = ProgressGauge(notebook, size=wx.Size(55, 15))
        # notebook.AddControlToPage(4, self.gauge)

        notebook_ctrl.main_notebook = notebook
        self.mgr.Update()

    def request_menu(self) -> None:
        self.collect_panes()
        self.build_request_menu()

    def collect_panes(self):
        pane: aui.AuiPaneInfo
        panes: list[aui.AuiPaneInfo] = []
        for pane in self.mgr.GetAllPanes():
            if not pane.IsToolbar() and pane.caption and pane.name:
                panes.append(pane)
        ref_ids: list[wx.WindowIDRef] = [wx.NewIdRef(len(panes))] if len(panes) <= 1 else wx.NewIdRef(len(panes))
        ref_id: wx.WindowIDRef
        self.req_pane_ids = {}
        for ref_id, pane in zip(ref_ids, panes):
            self.req_pane_ids[ref_id] = pane.name

    def build_request_menu(self):
        menu: wx.Menu = self.mb_items["UserAttention"]
        menu_item: wx.MenuItem
        for menu_item in menu.GetMenuItems():
            menu_item.Destroy()
        ref_id: wx.WindowIDRef
        pane_name: str
        for ref_id, pane_name in self.req_pane_ids.items():
            menu.Append(ref_id, self.mgr.GetPane(pane_name).caption)

        menu.Bind(wx.EVT_MENU_OPEN, self.on_menu_open_user_attention)

    def bind_menu(self):
        mb_items: dict = self.mb_items
        menu_refid: wx.WindowIDRef
        self.themes = {self.mb_items[key]["id"]: agw_tabart_provider[key] for key in agw_tabart_provider}
        for menu_refid in self.themes:
            self.frame.Bind(wx.EVT_MENU, self.on_notebook_theme, menu_refid)

        self.frame.Bind(wx.EVT_MENU, self.on_preview, id=mb_items["NotebookPreview"]["id"])
        # ctrl_key: str
        # for ctrl_key in content_ctrls.values():
        #     self.frame.Bind(wx.EVT_MENU, self.on_change_content_pane, id=self.mb_items[ctrl_key]["id"])
        self.frame.Bind(aui.EVT_AUI_PANE_CLOSE, self.on_pane_close)
        self.frame.Bind(aui.EVT_AUI_PANE_MINIMIZE, self.on_pane_min)
        # self.frame.Bind(wx.EVT_MENU, self.OnVetoTree, id=self.mb_items["VetoTree"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.OnVetoText, id=self.mb_items["VetoText"]["id"])
        self.frame.Bind(aui.EVT_AUI_PANE_FLOATING, self.on_float_dock)
        self.frame.Bind(aui.EVT_AUI_PANE_FLOATED, self.on_float_dock)
        self.frame.Bind(aui.EVT_AUI_PANE_DOCKING, self.on_float_dock)
        self.frame.Bind(aui.EVT_AUI_PANE_DOCKED, self.on_float_dock)
        # for menu_refid in self.flags:
        #     self.frame.Bind(wx.EVT_MENU, self.on_minimize_mode_flag, menu_refid)
        # self.frame.Bind(wx.EVT_MENU, self.on_minimize_mode_flag, id=mb_items["MinimizeCaptHide"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.on_seticons_onpanes, id=mb_items["PaneIcons"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.on_transparent_pane, id=mb_items["TransparentPane"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.on_dockart, id=mb_items["DefaultDockArt"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.on_dockart, id=mb_items["ModernDockArt"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.on_snap_to_screen, id=mb_items["SnapToScreen"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.on_snap_panes, id=mb_items["SnapPanes"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.on_flyout, id=mb_items["FlyOut"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.on_custom_pane_buttons, id=mb_items["CustomPaneButtons"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.on_switch_pane, id=mb_items["SwitchPane"]["id"])

        # self.frame.Bind(wx.EVT_MENU, self.on_delete, id=wx.ID_DELETE)
        # self.frame.Bind(wx.EVT_MENU, self.on_back, id=wx.ID_BACKWARD)
        # self.frame.Bind(wx.EVT_MENU, self.on_cut, id=wx.ID_CUT)
        # self.frame.Bind(wx.EVT_MENU, self.on_paste, id=wx.ID_PASTE)
        # self.frame.Bind(wx.EVT_MENU, self.on_copy, id=wx.ID_COPY)

        # self.frame.Bind(wx.EVT_MENU, self.on_line_plot, id=mb_items["LinePlot"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.on_bar_plot, id=mb_items["BarPlot"]["id"])
        # self.frame.Bind(wx.EVT_MENU, self.on_scatter_plot, id=mb_items["ScatterPlot"]["id"])

    def default_layout(self):
        # all_panes: list[aui.AuiPaneInfo] = self.mgr.GetAllPanes()
        # pane: aui.AuiPaneInfo
        # for pane in all_panes:
        #     if not pane.IsToolbar():
        #         pane.Hide()

        # self.mgr.GetPane("tb1").Hide()
        # self.mgr.GetPane("tb7").Hide()

        # self.mgr.GetPane("test8").Show().Left().Layer(0).Row(0).Position(0)
        # self.mgr.GetPane(f"__notebook_{self.mgr.GetPane('test10').notebook_id}"
        #                  ).Show().Bottom().Layer(0).Row(0).Position(0)
        self.mgr.GetPane("Console").Hide()
        # self.mgr.GetPane("thirdauto").Show()
        # self.mgr.GetPane("test10").Show()
        self.mgr.GetPane("notebook_content").Show()
        self.mgr.Update()

    def on_preview(self, _event: wx.CommandEvent) -> None:
        nb: aui.AuiNotebook = self.mgr.GetPane("notebook_content").window
        nb.NotebookPreview()

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

    # def on_line_plot(self, _event: wx.CommandEvent):
    #     self.echarts_show("Line Chart", "Line")
    #
    # def on_bar_plot(self, _event: wx.CommandEvent):
    #     self.echarts_show("Bar Chart", "Bar")
    #
    # def on_scatter_plot(self, _event: wx.CommandEvent):
    #     self.echarts_show("Scatter Chart", "Scatter")

    # def on_bar_plot(self, _event: wx.CommandEvent):
    #     self.echarts_show("Bar Chart", "Bar")
    #
    # def on_scatter_plot(self, _event: wx.CommandEvent):
    #     self.echarts_show("Scatter Chart", "Scatter")
    #
    # def echarts_show(self, title, echart_type, save_path=None):
    #     dlg = SimpleDialog(self.frame, title=title)
    #     result = dlg.ShowModal()
    #     if result != wx.ID_OK:
    #         dlg.Destroy()
    #         return
    #     y_list = dlg.ylist.GetSelections()
    #     checks = dlg.ylist.GetCheckedItems()
    #     x_num = dlg.xlist.GetSelection()
    #     y_list.extend(checks)
    #     selected_items = []
    #     for sel in y_list:
    #         # 使用GetStringSelection获取选中项的文本
    #         selected_items.append(dlg.ylist.GetString(sel))
    #     dlg.Destroy()
    #
    #     file_paths, file_name = simple_chart.build_html(x=dlg.data_df.iloc[:, x_num], y=dlg.data_df.iloc[:, y_list],
    #                                                     title=title, echart_type=echart_type, save_path=save_path)
    #     add_notebook_page(self.notebook_ctrl, self.html_ctrl, file_paths, file_name)
    #
    # def on_copy(self, _event: wx.CommandEvent) -> None:
    #     # 模拟按键ctrl+c
    #     keyboard.send('ctrl+c')
    #
    # def on_paste(self, _event: wx.CommandEvent) -> None:
    #     keyboard.send('ctrl+v')
    #
    # def on_cut(self, _event: wx.CommandEvent) -> None:
    #     keyboard.send('ctrl+x')

    def on_delete(self, _event: wx.CommandEvent) -> None:
        pass

    # def on_back(self, _event: wx.CommandEvent) -> None:
    #     keyboard.send('ctrl+z')

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
        if event.pane.name not in ["ProjectTree_min", "Console_min", "Console_min"]:
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

    def OnTimer(self, _event: wx.TimerEvent) -> None:
        try:
            self.gauge.Pulse()
        except:
            self.timer.Stop()
            raise

    def OnVetoTree(self, event: wx.CommandEvent) -> None:
        self.veto_tree = event.IsChecked()

    def OnVetoText(self, event: wx.CommandEvent) -> None:
        self.veto_text = event.IsChecked()

    def on_float_dock(self, event: aui.AuiManagerEvent) -> None:

        event_type = event.GetEventType()

        if event_type == aui.wxEVT_AUI_PANE_FLOATING:
            if event.pane.name == "test8" and self.veto_tree:
                event.Veto()
        elif event_type == aui.wxEVT_AUI_PANE_FLOATED:
            pass  # "The pane has been floated."
        elif event_type == aui.wxEVT_AUI_PANE_DOCKING:
            if event.pane.name == "test11" and self.veto_text:
                event.Veto()
        elif event_type == aui.wxEVT_AUI_PANE_DOCKED:
            pass  # The pane has been docked.

    def on_minimize_mode_flag(self, event: wx.CommandEvent) -> None:
        """Updates minimize mode state based on menu events."""
        min_mode: int = self.min_mode
        event_id: wx.WindowIDRef = event.GetId()
        menu_key: str = self.item_ids[event_id]
        # If menu item is a part of a RADIO group, clear all associated group flags.
        if menu_key in min_mode_masks:
            min_mode &= ~min_mode_masks[menu_key]
        """
        Note that a click toggles the state of a CHECK flag and sets a RADIO flag
        on. The code above checks if the flag is a part of RADIO group and clears
        the group before setting the target flag (only one member of a RADIO
        group can be set at a time). This way, for a RADIO flag, it must be set
        from the pre-cleared state, that is, its state is toggled. Thus, after
        pre-clearing the state of the affected RADIO group, if appropriate, the
        new state is set by toggling the old, but pre-cleared state below. If the
        item is a CHECK flag, its state is also toggled.
        Some RADIO groups use all-cleared-flags state as a separate base state
        (flags are just bits, but RADIO items are menu items, so there is no
        conflict here). This state is not part of the <flags> dict and will set
        the flag_mask to 0. In this case, the previous clear-group operation
        updates the state completely, and no other flag requires updating.   
        """
        flag_mask: int = self.flags.get(event_id, 0)
        if flag_mask:  # Toggle flag state.
            old_flag_state: int = min_mode & flag_mask
            new_flag_state: int = ~old_flag_state & flag_mask
            min_mode = min_mode & ~flag_mask | new_flag_state
        self.min_mode = min_mode

        all_panes: list[aui.AuiPaneInfo] = self.mgr.GetAllPanes()
        pane: aui.AuiPaneInfo
        for pane in all_panes:
            pane.MinimizeMode(min_mode)

    def on_seticons_onpanes(self, event: wx.CommandEvent) -> None:
        all_panes: list[aui.AuiPaneInfo] = self.mgr.GetAllPanes()
        pane: aui.AuiPaneInfo
        checked = event.IsChecked()
        for pane in all_panes:
            pane.Icon(res.rand_art_bitmap() if checked else None)
        self.mgr.Update()

    # For some reason, only works when the Transparent Drag Flag is set.
    def on_transparent_pane(self, _event: wx.CommandEvent) -> None:
        dlg = wx.TextEntryDialog(self.frame, "Enter a transparency value (0-255):", "Pane transparency")
        dlg.SetValue(str(self.transparency))
        if dlg.ShowModal() != wx.ID_OK:
            return

        try:
            transparency: int = int(dlg.GetValue())
            dlg.Destroy()
        except:
            dlg.Destroy()
            dlg = wx.MessageDialog(self.frame, 'Invalid transparency value. Transparency'
                                               ' should be an integer between 0 and 255.',
                                   'Error',
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if transparency < 0 or transparency > 255:
            dlg = wx.MessageDialog(self.frame, 'Invalid transparency value. Transparency'
                                               ' should be an integer between 0 and 255.',
                                   'Error',
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        self.transparency = transparency
        pane: aui.AuiPaneInfo
        for pane in self.mgr.GetAllPanes():
            pane.Transparent(transparency)

        self.mgr.Update()

    def on_dockart(self, event: wx.CommandEvent) -> None:
        if event.GetId() == self.mb_items["DefaultDockArt"]["id"]:
            self.mgr.SetArtProvider(aui.AuiDefaultDockArt())
        elif self.mgr.CanUseModernDockArt():
            self.mgr.SetArtProvider(aui.ModernDockArt(self))
        self.mgr.Update()
        self.frame.Update()

    def on_snap_to_screen(self, _event: wx.CommandEvent) -> None:
        self.mgr.SnapToScreen(True, monitor=0, hAlign=wx.RIGHT, vAlign=wx.TOP)

    def on_snap_panes(self, _event: wx.CommandEvent) -> None:
        all_panes: list[aui.AuiPaneInfo] = self.mgr.GetAllPanes()
        pane: aui.AuiPaneInfo

        if not self.snapped:
            self.captions = {}
            for pane in all_panes:
                if pane.IsToolbar() or isinstance(pane.window, aui.AuiNotebook):
                    continue

                self.captions[pane.name] = pane.caption
                snap: int = random.randrange(5)
                if snap == 0:
                    # Snap everywhere
                    pane.Caption(pane.caption + " (Snap Everywhere)")
                    pane.Snappable(True)
                elif snap == 1:
                    # Snap left
                    pane.Caption(pane.caption + " (Snap Left)")
                    pane.LeftSnappable(True)
                elif snap == 2:
                    # Snap right
                    pane.Caption(pane.caption + " (Snap Right)")
                    pane.RightSnappable(True)
                elif snap == 3:
                    # Snap top
                    pane.Caption(pane.caption + " (Snap Top)")
                    pane.TopSnappable(True)
                elif snap == 4:
                    # Snap bottom
                    pane.Caption(pane.caption + " (Snap Bottom)")
                    pane.BottomSnappable(True)
        else:
            for pane in all_panes:
                if pane.IsToolbar() or isinstance(pane.window, aui.AuiNotebook):
                    continue
                pane.Caption(self.captions[pane.name])
                pane.Snappable(False)

        self.snapped = not self.snapped
        self.mgr.Update()
        self.frame.Refresh()

    def on_flyout(self, event: wx.CommandEvent) -> None:
        pane: aui.AuiPaneInfo = self.mgr.GetPane("test8")

        if event.IsChecked():
            dlg = wx.MessageDialog(self.frame, 'The tree pane will have fly-out'
                                               ' behaviour when floating.',
                                   'Message',
                                   wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            pane.FlyOut(True)
        else:
            pane.FlyOut(False)

        self.mgr.Update()

    def on_custom_pane_buttons(self, event: wx.CommandEvent) -> None:
        art_provider: aui.AuiDefaultDockArt = self.mgr.GetArtProvider()

        bmp: ei.PyEmbeddedImage
        button: int
        active: bool
        maximize: bool
        if event.IsChecked():
            for bmp, button, active, maximize in res.CUSTOM_PANE_BITMAPS:
                art_provider.SetCustomPaneBitmap(bmp.GetBitmap(), button, active, maximize)
        else:
            art_provider.SetDefaultPaneBitmaps(wx.Platform == "__WXMAC__")

        self.mgr.Update()
        self.frame.Refresh()

    def on_switch_pane(self, _event: wx.CommandEvent) -> None:
        # Add the main windows and toolbars, in two separate columns
        # We'll use the item 'id' to store the notebook selection, or -1 if not a page
        # [("<caption>", "<name>", <idx>, <bitmap>, <window>)]
        TSwitcherPane = tuple[str, str, int, wx.Bitmap, wx.Window]
        spane: TSwitcherPane
        main_windows: list[TSwitcherPane] = []
        toolbars: list[TSwitcherPane] = []
        nbpages: list[TSwitcherPane] = []

        name: str
        nb: aui.AuiNotebook
        bitmap: wx.Bitmap
        idx: int
        pane: aui.AuiPaneInfo
        for pane in self.mgr.GetAllPanes():
            if isinstance(pane.window, aui.AuiNotebook):
                nb = pane.window
                nbpages.extend([
                    (nb.GetPageText(j), nb.GetPageText(j), j, nb.GetPageBitmap(j), nb.GetPage(j))
                    for j in range(nb.GetPageCount())
                ])
            elif isinstance(pane.window, wx.ToolBar | aui.AuiToolBar):
                if not pane.caption: continue
                bitmap = pane.icon.IsOk() and pane.icon or wx.NullBitmap
                toolbars.append((pane.name, pane.caption, -1, bitmap, pane.window))
            else:
                if not pane.caption or not pane.IsShown(): continue
                bitmap = pane.icon.IsOk() and pane.icon or wx.NullBitmap
                main_windows.append((pane.name, pane.caption, -1, bitmap, pane.window))

        items: asd.SwitcherItems = asd.SwitcherItems()
        items.SetRowCount(12)
        #            "<caption>", "<name>",    <idx>, <bitmap>            <window>
        # items.AddItem(spane[0], spane[1], spane[2], spane[3]).SetWindow(spane[4])
        items.AddGroup("Main Windows", "mainwindows")
        for spane in main_windows:
            items.AddItem(spane[0], spane[1], spane[2], spane[3]).SetWindow(spane[4])
        items.AddGroup("Toolbars", "toolbars").BreakColumn()
        for spane in toolbars:
            items.AddItem(spane[0], spane[1], spane[2], spane[3]).SetWindow(spane[4])
        items.AddGroup("Notebook Pages", "pages").BreakColumn()
        for spane in nbpages:
            items.AddItem(spane[0], spane[1], spane[2], spane[3]).SetWindow(spane[4])

        idx = items.GetIndexForFocus()
        if idx != wx.NOT_FOUND:
            items.SetSelection(idx)

        if wx.Platform == "__WXMAC__":
            items.SetBackgroundColour(wx.WHITE)

        # Show the switcher dialog
        dlg: asd.SwitcherDialog = asd.SwitcherDialog(items, self.frame, self.mgr)

        # In GTK+ we can't use Ctrl+Tab; we use Ctrl+/ instead and tell
        # the switcher to treat "/" as Tab (i.e. cycle through the names)
        if wx.Platform == "__WXGTK__":
            dlg.SetExtraNavigationKey('/')
        elif wx.Platform == "__WXMAC__":
            dlg.SetBackgroundColour(wx.WHITE)
            dlg.SetModifierKey(wx.WXK_ALT)

        if dlg.ShowModal() == wx.ID_OK and dlg.GetSelection() != -1:
            item: asd.SwitcherItem = items.GetItem(dlg.GetSelection())
            if item.GetId() == -1:
                pane = self.mgr.GetPane(item.GetName())
                pane.window.SetFocus()
                pane.Show()

            else:
                nb = item.GetWindow().GetParent()
                if isinstance(nb, aui.AuiNotebook):
                    nb.SetSelection(item.GetId())
                    item.GetWindow().SetFocus()

    def on_request_user_attention(self, event: wx.CommandEvent) -> None:
        ref_id: wx.WindowIDRef = event.GetId()
        if ref_id not in self.req_pane_ids: return
        pane: aui.AuiPaneInfo = self.mgr.GetPane(self.req_pane_ids[ref_id])
        self.mgr.RequestUserAttention(pane.window)

    def on_menu_open_user_attention(self, event: wx.MenuEvent) -> None:
        menu: wx.Menu = event.GetMenu()
        menu_item: wx.MenuItem
        for menu_item in menu.MenuItems:
            pane: aui.AuiPaneInfo = self.mgr.GetPane(self.req_pane_ids[menu_item.Id])
            menu_item.Enable(pane.IsShown())
