import wx
import wx.aui
import wx.lib.agw.aui as aui
from aui2 import svg_to_bitmap

from settings import settings as cs


class ToolBarManager:

    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager) -> None:
        self.frame = frame
        self.mgr = mgr
        self.item_ids = {}
        self.items = {}
        self.init_toolbars()
        # self.frame.Bind()

    def init_toolbars(self):
        # If MainFrame subclasses wx.Frame, replace the following line
        # frame: "MainFrame" = self.frame
        frame: wx.Frame = self.frame
        mgr: aui.AuiManager = self.mgr

        # tb_id: int = wx.NewIdRef()
        # tb2 = aui.AuiToolBar(frame, tb_id, wx.DefaultPosition, wx.DefaultSize,
        #                      agwStyle=aui.AUI_TB_TEXT | aui.AUI_TB_VERTICAL | aui.AUI_TB_PLAIN_BACKGROUND)
        # self.toolbar_ids[tb_id] = "toolbar_top"
        # self.toolbars["toolbar_top"] = {"id": tb_id, "item": tb2}
        # tb2.SetToolBitmapSize(wx.Size(20, 20))
        # tb2.AddSimpleTool(wx.ID_FILE, "File", self.of_svg, short_help_string="打开文件",)
        # # tb2.AddSpacer(5)
        # tb2.AddSimpleTool(wx.ID_OPEN, "Project", self.op_svg, short_help_string="打开项目")
        # tb2.AddSimpleTool(wx.ID_SAVE, "Save", self.save_svg, short_help_string="保存", )
        # tb2.AddSimpleTool(wx.ID_EXIT, "Exit", self.exit_svg, short_help_string="退出", )

        # tb2.AddSeparator()
        # tb2.AddSimpleTool(wx.ID_BACKWARD, "Back", self.back_svg, short_help_string="返回", )
        # tb2.AddSimpleTool(wx.ID_COPY, "Copy", self.copy_svg, short_help_string="复制",)
        # tb2.AddSimpleTool(wx.ID_PASTE, "Paste", self.paste_svg, short_help_string="粘贴")
        # tb2.AddSimpleTool(wx.ID_CUT, "Cut", self.cut_svg, short_help_string="剪切")
        # tb2.SetCustomOverflowItems([], append_items)
        # tb2.Realize()
        # tb2.EnableTool(wx.ID_BACKWARD, False)

        # mgr.AddPane(tb2, aui.AuiPaneInfo().Name("toolbar_top").Caption("导航栏").ToolbarPane().Floatable(False)
        #             .Dockable(False).Top())

        project_tb_id: int = wx.NewIdRef()
        tb5 = aui.AuiToolBar(frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_VERTICAL | aui.AUI_TB_VERT_TEXT |
                                      aui.AUI_TB_PLAIN_BACKGROUND)

        tb5.AddSimpleTool(project_tb_id, "项目", svg_to_bitmap(cs.tree_nav_svg, size=(13, 13)),)
        # tb5.AddSeparator()
        gripe_tb_id: int = wx.NewIdRef()
        tb5.AddSimpleTool(gripe_tb_id, "图表", svg_to_bitmap(cs.graph_svg, size=(13, 13)))
        tb5.Realize()
        mgr.AddPane(tb5, aui.AuiPaneInfo().Name("toolbar_left").Caption("左边栏").ToolbarPane().Floatable(False)
                    .Dockable(False).Left())

        tb6 = aui.AuiToolBar(frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_VERT_TEXT | aui.AUI_TB_PLAIN_BACKGROUND)
        tb6.SetToolBitmapSize(wx.Size(16, 16))
        database: int = wx.NewIdRef()
        tb6.AddSimpleTool(database, "数据库", svg_to_bitmap(cs.database_svg, size=(13, 13)))
        tb6.EnableTool(database, False)
        tb6.Realize()
        mgr.AddPane(tb6, aui.AuiPaneInfo().Name("toolbar_right").Caption("右边栏").
                    ToolbarPane().Right().Floatable(False).Dockable(False))

        # Show how to get a custom minimizing behaviour, i.e., to minimize a pane
        # inside an existing AuiToolBar
        # tree = self.mgr.GetPane("ProjectTree")
        # tree.MinimizeMode(aui.AUI_MINIMIZE_POS_TOOLBAR)
        # toolbar_pane = self.mgr.GetPane(tb2)
        # tree.MinimizeTarget(toolbar_pane)

        console_tb_id: int = wx.NewIdRef()
        tb7 = aui.AuiToolBar(frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_HORZ_TEXT | aui.AUI_TB_PLAIN_BACKGROUND)
        tb7.AddSimpleTool(console_tb_id, "监控", svg_to_bitmap(cs.console_svg, size=(12, 12)), )
        tb7.Realize()
        mgr.AddPane(tb7, aui.AuiPaneInfo().Name("toolbar_bottom").Caption("底边栏").ToolbarPane().Floatable(False)
                    .Dockable(False).Bottom())

        # "commit" all changes made to AuiManager
        frame.Bind(wx.EVT_MENU, self.on_project_nav, project_tb_id)
        frame.Bind(wx.EVT_MENU, self.on_graph_nav, gripe_tb_id)
        frame.Bind(wx.EVT_MENU, self.on_console_nav, console_tb_id)
        mgr.Update()

    def on_project_nav(self, _event: wx.CommandEvent):
        pane = self.mgr.GetPane("ProjectTree")
        self.is_display(pane)

    def on_graph_nav(self, _event: wx.CommandEvent):
        pane = self.mgr.GetPane("Graph")
        self.is_display(pane)

    def on_console_nav(self, _event: wx.CommandEvent):
        pane = self.mgr.GetPane("Console")
        self.is_display(pane)

    def is_display(self, pane):
        if pane.IsShown():
            pane.Minimize()
            pane.Hide()
        else:
            pane.Show(True)
        self.mgr.Update()
