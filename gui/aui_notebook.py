import os

import wx
import wx.aui
import wx.lib.agw.aui as aui

from typing import TYPE_CHECKING, Type

from aui2 import svg_to_bitmap

from settings.settings import float_size, left_svg, top_svg, new_page_svg

if TYPE_CHECKING:
    # If MainFrame subclasses wx.Frame, uncomment the following line
    # from gui.main_frame import MainFrame
    from controls import HTMLCtrl


class Singleton(type):
    """Singleton metaclass."""

    instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances:
            cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]


class Notebook:
    """Factory for a notebook control."""

    # If MainFrame subclasses wx.Frame, replace the following line
    # frame: "MainFrame"
    frame: wx.Frame

    mgr: aui.AuiManager
    create_menu_id: wx.WindowIDRef
    html_ctrl: "HTMLCtrl"
    notebook_style: int = aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER | aui.AUI_NB_TAB_FLOAT
    notebook_theme: int = 0
    custom_tab_buttons: bool
    main_notebook: aui.AuiNotebook
    counter: int = 0

    # If MainFrame subclasses wx.Frame, replace the following line
    # def __init__(self, frame: "MainFrame", mgr: aui.AuiManager,
    #              create_menu_id: wx.WindowIDRef,
    #              html_ctrl: "HTMLCtrl") -> None:
    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager,
                 create_menu_id: wx.WindowIDRef,
                 html_ctrl: "HTMLCtrl") -> None:
        self.frame = frame
        self.mgr = mgr
        self.html_ctrl = html_ctrl
        self.create_menu_id = create_menu_id
        self.notebook_object = None
        frame.Bind(wx.EVT_MENU, self.on_create, id=self.create_menu_id)

    def start_position(self) -> wx.Point:
        return self.frame.ClientToScreen(wx.Point(0, 0)) + (wx.Point(20, 20) * self.__class__.counter)

    def all_notebooks(self) -> list[aui.AuiNotebook]:
        """Returns a list of existing AGW AuiNotebook objects."""
        nbs: list[aui.AuiNotebook] = []
        pane: aui.AuiPaneInfo
        for pane in self.mgr.GetAllPanes():
            if isinstance(pane.window, aui.AuiNotebook):
                nbs.append(pane.window)
        return nbs

    def create_ctrl(self) -> aui.AuiNotebook:
        # If MainFrame subclasses wx.Frame, replace the following line
        # frame: "MainFrame" = self.frame
        frame: wx.Frame = self.frame
        self.__class__.counter += 1

        # create the notebook off-window to avoid flicker
        client_size: wx.Size = frame.GetClientSize()
        ctrl: aui.AuiNotebook = aui.AuiNotebook(frame, wx.ID_ANY, wx.Point(*client_size),
                                                wx.Size(*client_size), agwStyle=self.notebook_style)
        # type: list[Type[wx.aui.AuiTabArt]]
        arts = [aui.AuiDefaultTabArt, aui.AuiSimpleTabArt, aui.VC71TabArt,
                aui.FF2TabArt, aui.VC8TabArt, aui.ChromeTabArt]

        ctrl.SetArtProvider(arts[self.notebook_theme]())

        page_bmp: wx.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE,
                                                       wx.ART_OTHER, wx.Size(16, 16))

        # page = wx.TextCtrl(ctrl, wx.ID_ANY, overview, wx.DefaultPosition, wx.Size(*float_size),
        #                    wx.TE_MULTILINE | wx.NO_BORDER, name='Welcome to MINI-TOOL')
        # page.SetMargins(20)
        # font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
        # page.SetFont(font)
        # ctrl.AddPage(page, "Welcome to MINI-TOOL", False, page_bmp)

        file_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "static", "js",
                                 "introduce.html")
        ctrl.AddPage(self.html_ctrl.create_ctrl(path=file_path), "Welcome to MINI-TOOL", True, page_bmp)

        # panel: wx.Panel = wx.Panel(ctrl, wx.ID_ANY)
        # flex: wx.FlexGridSizer = wx.FlexGridSizer(rows=0, cols=2, vgap=2, hgap=2)
        # flex.Add((5, 5))
        # flex.Add((5, 5))
        # flex.Add(wx.StaticText(panel, wx.ID_ANY, "wxTextCtrl:"), 0, wx.ALL | wx.ALIGN_CENTRE, 5)
        # flex.Add(wx.TextCtrl(panel, wx.ID_ANY, "", wx.DefaultPosition, wx.Size(100, -1)),
        #          1, wx.ALL | wx.ALIGN_CENTRE, 5)
        # flex.Add(wx.StaticText(panel, wx.ID_ANY, "wxSpinCtrl:"), 0, wx.ALL | wx.ALIGN_CENTRE, 5)
        # flex.Add(wx.SpinCtrl(panel, wx.ID_ANY, "5", wx.DefaultPosition, wx.DefaultSize,
        #                      wx.SP_ARROW_KEYS, 5, 50, 5), 0, wx.ALL | wx.ALIGN_CENTRE, 5)
        # flex.Add((5, 5))
        # flex.Add((5, 5))
        # flex.AddGrowableRow(0)
        # flex.AddGrowableRow(3)
        # flex.AddGrowableCol(1)
        # panel.SetSizer(flex)
        # ctrl.AddPage(panel, "Disabled", False, page_bmp)

        # ctrl.AddPage(wx.TextCtrl(ctrl, wx.ID_ANY, "Some more text", wx.DefaultPosition,
        #                          wx.Size(*float_size), wx.TE_MULTILINE | wx.NO_BORDER), "Blue Tab")
        # ctrl.AddPage(wx.TextCtrl(ctrl, wx.ID_ANY, "Some more text", wx.DefaultPosition,
        #                          wx.Size(*float_size), wx.TE_MULTILINE | wx.NO_BORDER), "A Control")
        # ctrl.AddPage(wx.TextCtrl(ctrl, wx.ID_ANY, "Some more text", wx.DefaultPosition,
        #                          wx.Size(*float_size), wx.TE_MULTILINE | wx.NO_BORDER), "wxTextCtrl 4")
        # ctrl.AddPage(wx.TextCtrl(ctrl, wx.ID_ANY, "Some more text", wx.DefaultPosition,
        #                          wx.DefaultSize, wx.TE_MULTILINE | wx.NO_BORDER), "wxTextCtrl 5")
        # ctrl.AddPage(wx.TextCtrl(ctrl, wx.ID_ANY, "Some more text", wx.DefaultPosition,
        #                          wx.Size(*float_size), wx.TE_MULTILINE | wx.NO_BORDER), "wxTextCtrl 6")
        # ctrl.AddPage(wx.TextCtrl(ctrl, wx.ID_ANY, "Some more text", wx.DefaultPosition, wx.Size(*float_size),
        #                          wx.TE_MULTILINE | wx.NO_BORDER), "wxTextCtrl 7 (longer title)")
        # ctrl.AddPage(wx.TextCtrl(ctrl, wx.ID_ANY, "Some more text", wx.DefaultPosition,
        #                          wx.Size(*float_size), wx.TE_MULTILINE | wx.NO_BORDER), "wxTextCtrl 8")

        # Demonstrate how to disable a tab
        # if self.__class__.counter == 1:
        #     ctrl.EnableTab(0, True)

        # ctrl.SetPageTextColour(2, wx.RED)
        # ctrl.SetPageTextColour(1, wx.BLUE)
        # ctrl.SetRenamable(1, True)
        ctrl.Bind(aui.EVT_AUINOTEBOOK_TAB_RIGHT_DOWN, self.on_right_click_up)
        self.notebook_object = ctrl
        return ctrl

    def on_right_click_up(self, event):

        page_index = event.GetSelection()

        print(f"right clicked, tab_id: {page_index}")

        menu = wx.Menu()
        close_item = menu.Append(wx.ID_ANY, '关闭')
        all_close_item = menu.Append(wx.ID_ANY, '全部关闭')
        menu.AppendSeparator()
        left_split_item = menu.Append(wx.ID_ANY, '左右分屏')
        top_split_item = menu.Append(wx.ID_ANY, '上下分屏')
        close_split_item = menu.Append(wx.ID_ANY, '关闭分屏')
        menu.AppendSeparator()
        float_item = menu.Append(wx.ID_ANY, '新窗口')
        left_split_item.SetBitmap(svg_to_bitmap(left_svg, size=(13, 13)))
        top_split_item.SetBitmap(svg_to_bitmap(top_svg, size=(13, 13)))
        float_item.SetBitmap(svg_to_bitmap(new_page_svg, size=(13, 13)))
        self.notebook_object.Bind(wx.EVT_MENU, lambda event: self.on_close(event, page_index), close_item)
        self.notebook_object.Bind(wx.EVT_MENU, lambda event: self.on_all_close(event, page_index), all_close_item)
        self.notebook_object.Bind(wx.EVT_MENU, lambda event: self.on_left_split(event, page_index), left_split_item)
        self.notebook_object.Bind(wx.EVT_MENU, lambda event: self.on_top_split(event, page_index), top_split_item)
        self.notebook_object.Bind(wx.EVT_MENU, lambda event: self.on_close_split(event, page_index), close_split_item)
        self.notebook_object.Bind(wx.EVT_MENU, lambda event: self.on_float(event, page_index), float_item)
        self.notebook_object.PopupMenu(menu)

    def on_close(self, event, page_index):
        self.notebook_object.DeletePage(page_index)

    def on_all_close(self, event, page_index):
        while self.notebook_object.GetPageCount() > 0:
            self.notebook_object.DeletePage(0)

    def on_left_split(self, event, page_index):
        self.notebook_object.Split(page_index, wx.LEFT)

    def on_top_split(self, event, page_index):
        self.notebook_object.Split(page_index, wx.TOP)

    def on_close_split(self, event, page_index):
        self.notebook_object.UnSplit()

    def on_float(self, event, page_index):
        self.notebook_object.FloatPage(page_index)

    def on_create(self, _event: wx.CommandEvent) -> None:
        ctrl: aui.AuiNotebook = self.create_ctrl()
        caption = "Notebook"
        self.mgr.AddPane(ctrl, aui.AuiPaneInfo().Caption(caption).
                         Float().FloatingPosition(self.start_position()).
                         CloseButton(True).MaximizeButton(True).MinimizeButton(True).Movable(True).Floatable(True).
                         BestSize(*float_size).MinSize(*float_size))

        self.mgr.Update()
        ctrl.Refresh()

