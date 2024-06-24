import wx
import wx.aui
import wx.lib.agw.aui as aui
from aui2 import svg_to_bitmap

# If MainFrame subclasses wx.Frame, uncomment the following lines
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from gui.main_frame import MainFrame


# TODO: Update code, replace .AddSimpleTool with .AddTool (full version). See:
#       https://docs.wxpython.org/wx.aui.AuiToolBar.html#wx.aui.AuiToolBar.AddTool
#       https://wxpython.org/Phoenix/docs/html/wx.ToolBar.html#wx.ToolBar.AddTool
#       "demo~Core Windows/Controls~Toolbar" (and other tutorials)
# TODO: Each toolbar probably should be handled by a dedicated method.
from settings import settings as cs


class ToolBarManager:
    # If MainFrame subclasses wx.Frame, replace the following line
    # frame: "MainFrame"
    frame: wx.Frame

    mgr: aui.AuiManager
    toolbar_ids: dict[int, str]  # wx.NewRefId -> Toolbar string id
    toolbars: dict[str, dict]  # {"<key>": {"id": <ref_id>, "item": <aui.AuiToolBar>}}
    item_ids: dict[int, str]  # wx.NewRefId -> Control string id
    items: dict[str, dict]  # {"<key>": {"id": <ref_id>, "item": <aui.AuiToolBarItem>}}
    # of_svg = svg_to_bitmap(cs.of_svg)
    # op_svg = svg_to_bitmap(cs.op_svg)
    # save_svg = svg_to_bitmap(cs.save_svg)
    # back_svg = svg_to_bitmap(cs.back_svg)
    # exit_svg = svg_to_bitmap(cs.exit_svg)
    # copy_svg = svg_to_bitmap(cs.copy_svg)
    # paste_svg = svg_to_bitmap(cs.paste_svg)
    # cut_svg = svg_to_bitmap(cs.cut_svg)
    tree_nav_svg = svg_to_bitmap(cs.tree_nav_svg, size=(13, 13))
    # database_svg = svg_to_bitmap(cs.database_svg, size=(13, 13))
    console_svg = svg_to_bitmap(cs.console_svg, size=(12, 12))
    gripe_svg = svg_to_bitmap(cs.gripe_svg, size=(13, 13))

    # If MainFrame subclasses wx.Frame, replace the following line
    # def __init__(self, frame: "MainFrame", mgr: aui.AuiManager) -> None:
    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager) -> None:
        self.frame = frame
        self.mgr = mgr
        self.toolbar_ids = {}
        self.toolbars = {}
        self.item_ids = {}
        self.items = {}
        self.init_toolbars()
        # self.frame.Bind()

    def init_toolbars(self):
        # If MainFrame subclasses wx.Frame, replace the following line
        # frame: "MainFrame" = self.frame
        frame: wx.Frame = self.frame
        mgr: aui.AuiManager = self.mgr

        # min size for the frame itself isn't completely done.
        # see the end up AuiManager.Update() for the test
        # code. For now, just hard code a frame minimum size
        # frame.SetMinSize(wx.Size(400, 300))

        # prepare a few custom overflow elements for the toolbars' overflow buttons
        # append_items: list[aui.AuiToolBarItem] = []
        # item = aui.AuiToolBarItem()
        # item.SetKind(wx.ITEM_SEPARATOR)
        # append_items.append(item)
        #
        # item_id: int = wx.NewIdRef()
        # item = aui.AuiToolBarItem()
        # self.item_ids[item_id] = "CustomizeToolbar"
        # self.items["CustomizeToolbar"] = {"id": item_id, "item": item}
        # item.SetKind(wx.ITEM_NORMAL)
        # item.SetId(item_id)
        # item.SetLabel("Customize...")
        # append_items.append(item)
        # frame.Bind(wx.EVT_MENU, self.on_customize_toolbar, id=self.items["CustomizeToolbar"]["id"])

        # Popup menu id
        # The same popup menu is displayed for multiple toolbars, so
        # a single ref_id is associated with multiple toolbar items.
        # item_id: int = wx.NewIdRef()
        # self.item_ids[item_id] = "DropDownToolbarItem"
        # self.items["DropDownToolbarItem"] = {"id": item_id, "item": None}
        # noinspection PyPep8Naming
        # ID_DropDownToolbarItem: int = item_id

        # # create some toolbars
        # tb_id: int = wx.NewIdRef()
        # tb1 = aui.AuiToolBar(frame, tb_id, wx.DefaultPosition, wx.DefaultSize,
        #                      agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        # self.toolbar_ids[tb_id] = "tb1"
        # self.toolbars["tb1"] = {"id": tb_id, "item": tb1}
        # tb1.SetToolBitmapSize(wx.Size(48, 48))
        # tb1.AddSimpleTool(wx.NewIdRef(), "Test", wx.ArtProvider.GetBitmap(wx.ART_ERROR))
        # tb1.AddSeparator()
        # tb1.AddSimpleTool(wx.NewIdRef(), "Test", wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
        # tb1.AddSimpleTool(wx.NewIdRef(), "Test", wx.ArtProvider.GetBitmap(wx.ART_INFORMATION))
        # tb1.AddSimpleTool(wx.NewIdRef(), "Test", wx.ArtProvider.GetBitmap(wx.ART_WARNING))
        # tb1.AddSimpleTool(wx.NewIdRef(), "Test", wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE))
        # tb1.SetCustomOverflowItems([], append_items)
        # tb1.Realize()
        # mgr.AddPane(tb1, aui.AuiPaneInfo().Name("tb1").Caption("Big Toolbar").ToolbarPane().Top())

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

        # tb_id: int = wx.NewIdRef()
        # tb3 = aui.AuiToolBar(frame, tb_id, wx.DefaultPosition, wx.DefaultSize,
        #                      agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        # self.toolbar_ids[tb_id] = "tb3"
        # self.toolbars["tb3"] = {"id": tb_id, "item": tb3}
        # tb3.SetToolBitmapSize(wx.Size(16, 16))
        # tb3_bmp1 = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16, 16))
        # tb3.AddSimpleTool(wx.NewIdRef(), "Check 1", tb3_bmp1, "Check 1", aui.ITEM_CHECK)
        # tb3.AddSimpleTool(wx.NewIdRef(), "Check 2", tb3_bmp1, "Check 2", aui.ITEM_CHECK)
        # tb3.AddSimpleTool(wx.NewIdRef(), "Check 3", tb3_bmp1, "Check 3", aui.ITEM_CHECK)
        # tb3.AddSimpleTool(wx.NewIdRef(), "Check 4", tb3_bmp1, "Check 4", aui.ITEM_CHECK)
        # tb3.AddSeparator()
        # tb3.AddSimpleTool(wx.NewIdRef(), "Radio 1", tb3_bmp1, "Radio 1", aui.ITEM_RADIO)
        # tb3.AddSimpleTool(wx.NewIdRef(), "Radio 2", tb3_bmp1, "Radio 2", aui.ITEM_RADIO)
        # tb3.AddSimpleTool(wx.NewIdRef(), "Radio 3", tb3_bmp1, "Radio 3", aui.ITEM_RADIO)
        # tb3.AddSeparator()
        # tb3.AddSimpleTool(wx.NewIdRef(), "Radio 1 (Group 2)", tb3_bmp1, "Radio 1 (Group 2)", aui.ITEM_RADIO)
        # tb3.AddSimpleTool(wx.NewIdRef(), "Radio 2 (Group 2)", tb3_bmp1, "Radio 2 (Group 2)", aui.ITEM_RADIO)
        # tb3.AddSimpleTool(wx.NewIdRef(), "Radio 3 (Group 2)", tb3_bmp1, "Radio 3 (Group 2)", aui.ITEM_RADIO)
        # tb3.SetCustomOverflowItems([], append_items)
        # tb3.Realize()
        # mgr.AddPane(tb3, aui.AuiPaneInfo().Name("tb3").Caption("Toolbar 3").ToolbarPane().Top().Row(1).Position(1))

        # tb_id: int = wx.NewIdRef()
        # tb4 = aui.AuiToolBar(frame, tb_id, wx.DefaultPosition, wx.DefaultSize,
        #                      agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_TEXT | aui.AUI_TB_HORZ_TEXT)
        # self.toolbar_ids[tb_id] = "tb4"
        # self.toolbars["tb4"] = {"id": tb_id, "item": tb4}
        # tb4.SetToolBitmapSize(wx.Size(16, 16))
        # tb4_bmp1 = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
        # tb4.AddSimpleTool(ID_DropDownToolbarItem, "Item 1", tb4_bmp1)
        # tb4.AddSimpleTool(wx.NewIdRef(), "Item 2", tb4_bmp1)
        # tb4.AddSimpleTool(wx.NewIdRef(), "Item 3", tb4_bmp1)
        # tb4.AddSimpleTool(wx.NewIdRef(), "Item 4", tb4_bmp1)
        # tb4.AddSeparator()
        # tb4.AddSimpleTool(wx.NewIdRef(), "Item 5", tb4_bmp1)
        # tb4.AddSimpleTool(wx.NewIdRef(), "Item 6", tb4_bmp1)
        # tb4.AddSimpleTool(wx.NewIdRef(), "Item 7", tb4_bmp1)
        # tb4.AddSimpleTool(wx.NewIdRef(), "Item 8", tb4_bmp1)
        # choice = wx.Choice(tb4, -1, choices=["One choice", "Another choice"])
        # tb4.AddControl(choice)
        # tb4.SetToolDropDown(ID_DropDownToolbarItem, True)
        # tb4.Realize()
        # mgr.AddPane(tb4, aui.AuiPaneInfo().Name("tb4").Caption("Bookmark Toolbar").ToolbarPane().Top().Row(2))

        project_tb_id: int = wx.NewIdRef()
        tb5 = aui.AuiToolBar(frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_VERTICAL | aui.AUI_TB_VERT_TEXT |
                                      aui.AUI_TB_PLAIN_BACKGROUND)

        self.toolbar_ids[project_tb_id] = "toolbar_left"
        self.toolbars["toolbar_left"] = {"id": project_tb_id, "item": tb5}
        tb5.AddSimpleTool(project_tb_id, "Project", self.tree_nav_svg,)
        # tb5.AddSeparator()
        gripe_tb_id: int = wx.NewIdRef()
        tb5.AddSimpleTool(gripe_tb_id, "Gripe", self.gripe_svg)
        # tb5.AddSimpleTool(wx.NewIdRef(), "Test", wx.ArtProvider.GetBitmap(wx.ART_INFORMATION))
        # tb5.AddSimpleTool(wx.NewIdRef(), "Test", wx.ArtProvider.GetBitmap(wx.ART_WARNING))
        # tb5.AddSimpleTool(wx.NewIdRef(), "Test", wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE))
        # tb5.SetCustomOverflowItems([], append_items)
        tb5.Realize()
        mgr.AddPane(tb5, aui.AuiPaneInfo().Name("toolbar_left").Caption("左边栏").ToolbarPane().Floatable(False)
                    .Dockable(False).Left())

        # tb_id: int = wx.NewIdRef()
        # tb6 = aui.AuiToolBar(frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
        #                      agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_VERT_TEXT | aui.AUI_TB_PLAIN_BACKGROUND)
        # self.toolbar_ids[tb_id] = "toolbar_right"
        # self.toolbars["toolbar_right"] = {"id": tb_id, "item": tb6}
        # tb6.SetToolBitmapSize(wx.Size(16, 16))
        # database: int = wx.NewIdRef()
        # tb6.AddSimpleTool(database, "Database", self.database_svg)
        # tb6.EnableTool(database, False)
        # tb6.AddSeparator()
        # tb6.AddSimpleTool(wx.NewIdRef(), "Clockwise 2",
        #                   wx.ArtProvider.GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, wx.Size(16, 16)))
        # tb6.AddSimpleTool(ID_DropDownToolbarItem, "Clockwise 3",
        #                   wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_OTHER, wx.Size(16, 16)))
        # tb6.SetCustomOverflowItems([], append_items)
        # tb6.SetToolDropDown(ID_DropDownToolbarItem, True)
        # tb6.Realize()
        # mgr.AddPane(tb6, aui.AuiPaneInfo().Name("toolbar_right").Caption("右边栏").
        #             ToolbarPane().Right().TopDockable(False).Floatable(False).Dockable(False))

        # mgr.AddPane(wx.Button(frame, wx.ID_ANY, "Test Button"),
        #             aui.AuiPaneInfo().Name("tb7").ToolbarPane().Top().Row(2).Position(1))

        # Show how to get a custom minimizing behaviour, i.e., to minimize a pane
        # inside an existing AuiToolBar
        # tree = self.mgr.GetPane("ProjectTree")
        # tree.MinimizeMode(aui.AUI_MINIMIZE_POS_TOOLBAR)
        # toolbar_pane = self.mgr.GetPane(tb2)
        # tree.MinimizeTarget(toolbar_pane)

        console_tb_id: int = wx.NewIdRef()
        tb7 = aui.AuiToolBar(frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_HORZ_TEXT | aui.AUI_TB_PLAIN_BACKGROUND)
        self.toolbar_ids[console_tb_id] = "toolbar_bottom"
        self.toolbars["toolbar_bottom"] = {"id": console_tb_id, "item": tb7}
        tb7.AddSimpleTool(console_tb_id, "Console", self.console_svg, )
        tb7.Realize()
        mgr.AddPane(tb7, aui.AuiPaneInfo().Name("toolbar_bottom").Caption("底边栏").ToolbarPane().Floatable(False)
                    .Dockable(False).Bottom())

        # "commit" all changes made to AuiManager
        frame.Bind(wx.EVT_MENU, self.on_project_nav, project_tb_id)
        frame.Bind(wx.EVT_MENU, self.on_gripe_nav, gripe_tb_id)
        frame.Bind(wx.EVT_MENU, self.on_console_nav, console_tb_id)
        # self.mgr.Update()

    def on_project_nav(self, _event: wx.CommandEvent):
        pane = self.mgr.GetPane("ProjectTree")
        self.is_display(pane)

    def on_gripe_nav(self, _event: wx.CommandEvent):
        pane = self.mgr.GetPane("Gripe")
        self.is_display(pane)

    def on_console_nav(self, _event: wx.CommandEvent):
        pane = self.mgr.GetPane("Console")
        self.is_display(pane)

    def is_display(self, pane):
        if pane.IsShown():
            pane.Hide()
        else:
            pane.Show(True)
        self.mgr.Update()

    def on_customize_toolbar(self, _event: wx.CommandEvent) -> None:
        wx.MessageBox("Customize Toolbar clicked", "Test")
