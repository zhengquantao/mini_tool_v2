import os

import pandas as pd
import wx
import wx.grid
import wx.html2
import wx.lib.agw.aui as aui

# If MainFrame subclasses wx.Frame, uncomment the following lines
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from gui.main_frame import MainFrame
from common.common import read_file, remove_file, rename_file, get_file_info
from common import loggers
from models.compare_curve import compare_curve
from settings.resources import overview
from settings.settings import opening_dict, float_size, display_grid_count


class Singleton(type):
    """Singleton metaclass."""

    instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances:
            cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]


class GridCtrl(metaclass=Singleton):
    """Factory for a grid control."""

    # If MainFrame subclasses wx.Frame, replace the following line
    # frame: "MainFrame"
    frame: wx.Frame

    mgr: aui.AuiManager
    create_menu_id: wx.WindowIDRef
    counter: int = 0

    # If MainFrame subclasses wx.Frame, replace the following line
    # def __init__(self, frame: "MainFrame", mgr: aui.AuiManager,
    #              create_menu_id: wx.WindowIDRef) -> None:
    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager,
                 create_menu_id: wx.WindowIDRef) -> None:
        self.frame = frame
        self.mgr = mgr
        self.create_menu_id = create_menu_id
        frame.Bind(wx.EVT_MENU, self.OnCreate, id=self.create_menu_id)

    def start_position(self) -> wx.Point:
        return self.frame.ClientToScreen(wx.Point(0, 0)) + (wx.Point(20, 20) * self.__class__.counter)

    def create_ctrl(self, data_df=None) -> wx.grid.Grid:
        self.__class__.counter += 1
        grid = wx.grid.Grid(self.frame, wx.ID_ANY, wx.Point(0, 0), wx.Size(150, 250),
                            wx.NO_BORDER)

        grid.CreateGrid(100, 50)  # 创建一个n行n列的表格
        grid.EnableScrolling(True, True)
        # 边框颜色
        grid.SetGridLineColour(wx.LIGHT_GREY)

        # 渲染表格
        self.render_grid(data_df, grid)

        return grid

    def render_grid(self, data: pd.DataFrame(), grid):
        if not isinstance(data, pd.DataFrame):
            return
        # Clear old data
        grid.ClearGrid()

        # Get the current number of rows and columns
        num_rows = grid.GetNumberRows()
        num_cols = grid.GetNumberCols()

        # Calculate the number of additional rows and columns needed
        additional_rows = data.shape[0] - num_rows
        additional_cols = data.shape[1] - num_cols

        # Append additional rows and columns if needed
        if additional_rows > 0:
            grid.AppendRows(additional_rows)
        if additional_cols > 0:
            grid.AppendCols(additional_cols)

        for col, val in enumerate(data.columns):
            grid.SetCellValue(0, col, str(val))
            grid.SetCellAlignment(0, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        grid.BeginBatch()
        for row in range(1, min(data.shape[0], display_grid_count)):
            for col in range(data.shape[1]):
                grid.SetCellValue(row, col, str(data.iat[row, col]))
                grid.SetCellAlignment(row, col, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        grid.EndBatch()

    def OnCreate(self, _event: wx.CommandEvent) -> None:
        ctrl: wx.grid.Grid = self.create_ctrl()
        caption = "Grid"
        self.mgr.AddPane(ctrl, aui.AuiPaneInfo().Caption(caption).Float().
                         FloatingPosition(self.start_position()).FloatingSize(wx.Size(300, 200)).
                         CloseButton(False).MaximizeButton(True).MinimizeButton(True))
        self.mgr.Update()
        ctrl.Refresh()


class TextCtrl(metaclass=Singleton):
    """Factory for a text control."""

    # If MainFrame subclasses wx.Frame, replace the following line
    # frame: "MainFrame"
    frame: wx.Frame

    mgr: aui.AuiManager
    create_menu_id: wx.WindowIDRef
    counter: int = 0

    # If MainFrame subclasses wx.Frame, replace the following line
    # def __init__(self, frame: "MainFrame", mgr: aui.AuiManager,
    #              create_menu_id: wx.WindowIDRef) -> None:
    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager,
                 create_menu_id: wx.WindowIDRef) -> None:
        self.frame = frame
        self.mgr = mgr
        self.create_menu_id = create_menu_id
        frame.Bind(wx.EVT_MENU, self.OnCreate, id=self.create_menu_id)

    def start_position(self) -> wx.Point:
        return self.frame.ClientToScreen(wx.Point(0, 0)) + (wx.Point(20, 20) * self.__class__.counter)

    def create_ctrl(self, text: str = "", width: int = 500, height: int = 400, style=wx.TE_MULTILINE,
                    font=None) -> wx.TextCtrl:
        self.__class__.counter += 1
        ctrl = wx.TextCtrl(self.frame, wx.ID_ANY, text, wx.DefaultPosition,
                           wx.Size(width, height), style=style)
        if not font:
            font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
        ctrl.SetMargins(8)
        ctrl.SetFont(font)
        return ctrl

    def OnCreate(self, _event: wx.CommandEvent) -> None:
        ctrl: wx.TextCtrl = self.create_ctrl()
        caption = "Text Control"
        self.mgr.AddPane(ctrl, aui.AuiPaneInfo().Caption(caption).Float().
                         FloatingPosition(self.start_position()).MinimizeButton(True))
        self.mgr.Update()
        ctrl.Refresh()

        self.mgr.Update()


class TreeCtrl(metaclass=Singleton):
    """Factory for a tree control."""

    # If MainFrame subclasses wx.Frame, replace the following line
    # frame: "MainFrame"
    frame: wx.Frame

    mgr: aui.AuiManager
    create_menu_id: wx.WindowIDRef
    counter: int = 0

    # If MainFrame subclasses wx.Frame, replace the following line
    # def __init__(self, frame: "MainFrame", mgr: aui.AuiManager,
    #              create_menu_id: wx.WindowIDRef) -> None:
    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager,
                 create_menu_id: wx.WindowIDRef, notebook_ctrl=None, html_ctrl=None, grid_ctrl=None) -> None:
        self.frame = frame
        self.mgr = mgr
        self.create_menu_id = create_menu_id
        self.notebook_ctrl = notebook_ctrl
        self.html_ctrl = html_ctrl
        self.grid_ctrl = grid_ctrl
        self.now_file_list = []
        frame.Bind(wx.EVT_MENU, self.OnCreate, id=self.create_menu_id)
        frame.Bind(wx.EVT_ACTIVATE, self.on_update)

    def on_update(self, event):
        project_path = opening_dict[os.getpid()]["path"]
        if get_file_info(project_path) == self.now_file_list:
            return
        print("当前有文件改动")
        self.tree.DeleteChildren(self.root)
        self.build_tree(project_path, self.root)
        self.tree.SortChildren(self.root)
        self.tree.Expand(self.root)
        # self.tree.Refresh()

    def start_position(self) -> wx.Point:
        return self.frame.ClientToScreen(wx.Point(0, 0)) + (wx.Point(20, 20) * self.__class__.counter)

    def create_ctrl(self, path="./") -> wx.TreeCtrl:
        self.__class__.counter += 1
        self.tree: wx.TreeCtrl = wx.TreeCtrl(self.frame, wx.ID_ANY, wx.Point(0, 0), wx.Size(160, 250),
                                             wx.TR_DEFAULT_STYLE | wx.TR_TWIST_BUTTONS | wx.TR_NO_LINES | wx.NO_BORDER)
        self.tree.SetDoubleBuffered(True)
        imglist: wx.ImageList = wx.ImageList(16, 16, True, 2)
        icons = [wx.ART_FOLDER, wx.ART_FILE_OPEN, wx.ART_NORMAL_FILE]
        for icon in icons:
            imglist.Add(wx.ArtProvider.GetBitmap(icon, wx.ART_OTHER, wx.Size(16, 16)))
        self.tree.AssignImageList(imglist)
        root_name = path.split(os.sep)[-1]
        self.now_file_list = get_file_info(path)
        self.root: wx.TreeItemId = self.tree.AddRoot(root_name, 0)
        self.tree.SetItemImage(self.root, 0, wx.TreeItemIcon_Expanded)

        self.build_tree(path, self.root)
        self.tree.SortChildren(self.root)
        self.tree.Expand(self.root)

        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_right_click)
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_item_expanded)
        self.tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_item_collapsed)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGING, self.on_sel_changing)

        return self.tree

    def OnCreate(self, _event: wx.CommandEvent) -> None:
        ctrl: wx.TreeCtrl = self.create_ctrl()
        caption = "Tree Control"
        self.mgr.AddPane(ctrl, aui.AuiPaneInfo().Caption(caption).Float().
                         FloatingPosition(self.start_position()).CloseButton(True).
                         MaximizeButton(True).MinimizeButton(True))
        self.mgr.Update()
        ctrl.Refresh()

    def build_tree(self, dir_path, parent_item):
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                new_item = self.tree.AppendItem(parent_item, item)
                self.tree.SetItemImage(new_item, 0)
                self.tree.SetItemData(new_item, item_path)
                self.build_tree(item_path, new_item)
            else:
                new_item = self.tree.AppendItem(parent_item, item)
                self.tree.SetItemImage(new_item, 2)
                self.tree.SetItemData(new_item, item_path)

    def on_right_click(self, event):
        item = event.GetItem()
        path = self.tree.GetItemData(item)
        print(f"right clicked, path: {path}")

        menu = wx.Menu()
        sub_model_menu = wx.Menu()
        open_item = menu.Append(wx.ID_ANY, '打开')
        delete_item = menu.Append(wx.ID_ANY, '删除')
        rename_item = menu.Append(wx.ID_ANY, '重命名')

        # models
        menu.AppendSeparator()
        model_1 = sub_model_menu.Append(wx.ID_ANY, '能效等级总览')
        model_2 = sub_model_menu.Append(wx.ID_ANY, '能效评估结果总览')
        model_3 = sub_model_menu.Append(wx.ID_ANY, '能效排行')
        model_4 = sub_model_menu.Append(wx.ID_ANY, '理论与实际功率对比分析')
        model_5 = sub_model_menu.Append(wx.ID_ANY, '风资源对比')
        menu.AppendSubMenu(sub_model_menu, '模型图')

        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_open(event, path), open_item)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_delete(event, path), delete_item)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_rename(event, path), rename_item)

        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_1(event, path), model_1)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_2(event, path), model_2)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_3(event, path), model_3)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_4(event, path), model_4)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_5(event, path), model_5)

        self.tree.PopupMenu(menu)

    def on_delete(self, event, path):
        print(f"Delete clicked, file path: {path}")
        dlg = wx.MessageDialog(self.frame, f"你确认要删除文件 {path.split(os.sep)[-1]} 吗？",
                               "刪除文件", wx.OK | wx.ICON_WARNING)
        if dlg.ShowModal() != wx.ID_OK:
            return
        remove_file(path)

    def on_open(self, event, path):
        if not os.path.isfile(path):
            return

        loggers.logger.info(f"Open clicked, file path: {path}")
        page_bmp: wx.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
        ctrl = self.notebook_ctrl.notebook_object
        file_name = path.split(os.sep)[-1]
        text = read_file(path)

        pid = os.getpid()
        opening_dict[pid]["records"][file_name] = path

        if path.endswith(".html"):
            ctrl.AddPage(self.html_ctrl.create_ctrl(path=path), file_name, True, page_bmp)

        elif any([path.endswith(".csv"), path.endswith(".xlsx"), path.endswith(".xls")]):
            data_df = pd.read_csv(path)
            ctrl.AddPage(self.grid_ctrl.create_ctrl(data_df), file_name, True, page_bmp)

        elif any([path.endswith(".png"), path.endswith(".jpg"), path.endswith(".jpeg")]):
            image = wx.Bitmap(path)
            # size = self.mgr.GetPaneByName("notebook_content").window.GetSize()
            # image = image.Rescale(size[0], size[1])
            image_ctrl = wx.StaticBitmap(self.frame, wx.ID_ANY, image)
            ctrl.AddPage(image_ctrl, file_name, True, page_bmp)

        else:
            page = wx.TextCtrl(ctrl, wx.ID_ANY, text, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.NO_BORDER)
            page.SetMargins(8)
            font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
            page.SetFont(font)
            ctrl.AddPage(wx.TextCtrl(ctrl, wx.ID_ANY, text, wx.DefaultPosition,
                         wx.DefaultSize, wx.TE_MULTILINE | wx.NO_BORDER), file_name, True, page_bmp)

    def on_rename(self, event, path):
        print(f"Rename clicked, file path: {path}")
        dlg = wx.TextEntryDialog(self.frame, "请输入新文件名:", "文件重命名")
        if dlg.ShowModal() != wx.ID_OK:
            return

        directory_name: str = dlg.GetValue()
        file_list = path.split(os.sep)
        file_list[-1] = directory_name
        rename_file(path, os.sep.join(file_list))

    def on_model_1(self, event, path):

        print(f"model clicked, path: {path}")
        file_path = r"D:\project\mini_tool_v2\test.html"
        ID_HTMLCtrl: wx.WindowIDRef = wx.NewIdRef()
        HTMLCtrl(self.frame, self.mgr, ID_HTMLCtrl).OnCreate(wx.wxEVT_NULL, file_path, file_path)

    def on_model_2(self, event, path):
        print(f"model clicked, path: {path}")
        file_path = r"D:\project\mini_tool_v2\test.html"
        ID_HTMLCtrl: wx.WindowIDRef = wx.NewIdRef()
        HTMLCtrl(self.frame, self.mgr, ID_HTMLCtrl).OnCreate(wx.wxEVT_NULL, file_path, file_path)

    def on_model_3(self, event, path):
        print(f"model clicked, path: {path}")
        file_path = r"D:\project\mini_tool_v2\test.html"
        ID_HTMLCtrl: wx.WindowIDRef = wx.NewIdRef()
        HTMLCtrl(self.frame, self.mgr, ID_HTMLCtrl).OnCreate(wx.wxEVT_NULL, file_path, file_path)

    def on_model_4(self, event, path):
        """理论与实际功率对比分析"""
        loggers.logger.info(f"model clicked, path: {path}")
        if os.path.isdir(path):
            for ph in os.listdir(path):
                # file_paths = compare_curve(ph)
                pass
            return

        # 理论和实际功率曲线对比
        file_paths, file_name = compare_curve(path)
        page_bmp: wx.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
        ctrl = self.notebook_ctrl.notebook_object
        pid = os.getpid()
        opening_dict[pid]["records"][file_name] = file_paths
        ctrl.AddPage(self.html_ctrl.create_ctrl(path=file_paths), file_name, True, page_bmp)

    def on_model_5(self, event, path):
        """风资源对比图"""
        loggers.logger.info(f"model clicked, path: {path}")
        if os.path.isdir(path):
            for ph in os.listdir(path):
                # file_paths = compare_curve(ph)
                pass
            return

        # 理论和实际功率曲线对比
        file_paths, file_name = compare_curve(path, select=True)
        page_bmp: wx.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
        ctrl = self.notebook_ctrl.notebook_object
        opening_dict[os.getpid()]["records"][file_name] = file_paths
        ctrl.AddPage(self.html_ctrl.create_ctrl(path=file_paths), file_name, True, page_bmp)

    def on_item_expanded(self, event):
        print("Item expanded!")

    def on_item_collapsed(self, event):
        print("Item collapsed!")

    def on_sel_changed(self, event):
        print("Selection changed")

    def on_sel_changing(self, event):
        print("Selection changing")


class HTMLCtrl(metaclass=Singleton):
    """Factory for an html control."""

    # If MainFrame subclasses wx.Frame, replace the following line
    # frame: "MainFrame"
    frame: wx.Frame

    mgr: aui.AuiManager
    create_menu_id: wx.WindowIDRef
    counter: int = 0

    # If MainFrame subclasses wx.Frame, replace the following line
    # def __init__(self, frame: "MainFrame", mgr: aui.AuiManager,
    #              create_menu_id: wx.WindowIDRef) -> None:
    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager,
                 create_menu_id: wx.WindowIDRef) -> None:
        self.frame = frame
        self.mgr = mgr
        self.create_menu_id = create_menu_id
        frame.Bind(wx.EVT_MENU, self.OnCreate, id=self.create_menu_id)

    def start_position(self) -> wx.Point:
        return self.frame.ClientToScreen(wx.Point(0, 0)) + (wx.Point(20, 20) * self.__class__.counter)

    def create_ctrl(self, parent: wx.Frame = None, path: str = "") -> wx.html2.WebView:
        self.__class__.counter += 1
        if not parent:
            parent = self.frame
        ctrl = wx.html2.WebView.New(parent, size=wx.Size(*float_size))
        ctrl.LoadURL(f"file:///{path}")
        return ctrl

    def OnCreate(self, _event: wx.CommandEvent, caption="HTML Control", path=overview, width=700, height=400) -> None:
        ctrl: wx.html2.WebView = self.create_ctrl(path=path)
        self.mgr.AddPane(ctrl, aui.AuiPaneInfo().Caption(caption).Float().Name("html_content").
                         FloatingPosition(self.start_position()).BestSize(wx.Size(width, height)).
                         CloseButton(True).MaximizeButton(True).MinimizeButton(True))

        self.mgr.Update()
        ctrl.Refresh()


# noinspection PyPep8Naming
class SizeReportCtrl(metaclass=Singleton):
    """Factory for a utility control reporting its client size."""

    # If MainFrame subclasses wx.Frame, replace the following line
    # frame: "MainFrame"
    frame: wx.Frame

    mgr: aui.AuiManager
    create_menu_id: wx.WindowIDRef
    counter: int = 0

    # If MainFrame subclasses wx.Frame, replace the following line
    # def __init__(self, frame: "MainFrame", mgr: aui.AuiManager,
    #              create_menu_id: wx.WindowIDRef) -> None:
    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager,
                 create_menu_id: wx.WindowIDRef) -> None:
        self.frame = frame
        self.mgr = mgr
        self.create_menu_id = create_menu_id
        frame.Bind(wx.EVT_MENU, self.OnCreate, id=self.create_menu_id)

    def create_ctrl(self, width: int = 80, height: int = 80) -> wx.Control:
        self.__class__.counter += 1
        ctrl = wx.Control(self.frame, wx.ID_ANY, wx.DefaultPosition,
                          wx.Size(width, height), style=wx.NO_BORDER)
        ctrl.Bind(wx.EVT_PAINT, self.OnPaint)
        ctrl.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        ctrl.Bind(wx.EVT_SIZE, self.OnSize)
        return ctrl

    def start_position(self) -> wx.Point:
        return self.frame.ClientToScreen(wx.Point(0, 0)) + (wx.Point(20, 20) * self.__class__.counter)

    def OnCreate(self, _event: wx.CommandEvent) -> None:
        ctrl: wx.Control = self.create_ctrl()
        caption = "Client Size Reporter"
        self.mgr.AddPane(ctrl, aui.AuiPaneInfo().Caption(caption).Float().
                         FloatingPosition(self.start_position()).CloseButton(True).
                         MaximizeButton(True).MinimizeButton(True))
        self.mgr.Update()
        ctrl.Refresh()

    def OnEraseBackground(self, _event: wx.EraseEvent) -> None:
        pass  # intentionally empty

    def OnSize(self, event: wx.SizeEvent) -> None:
        ctrl: wx.Control = event.GetEventObject()
        ctrl.Refresh()

    def OnPaint(self, event: wx.PaintEvent) -> None:
        ctrl: wx.Control = event.GetEventObject()
        dc = wx.PaintDC(ctrl)
        dc.SetFont(wx.NORMAL_FONT)
        dc.SetBrush(wx.WHITE_BRUSH)

        size = ctrl.GetClientSize()
        dc.SetPen(wx.WHITE_PEN)
        dc.DrawRectangle(0, 0, size.x, size.y)
        dc.SetPen(wx.LIGHT_GREY_PEN)
        dc.DrawLine(0, 0, size.x, size.y)
        dc.DrawLine(0, size.y, size.x, 0)

        pi = self.mgr.GetPane(self)

        s = f"Size: {size.x} x {size.y}"
        w, height = dc.GetTextExtent(s)
        height += 3
        dc.DrawText(s, (size.x - w) // 2, (size.y - height * 5) // 2)

        s = f"Layer: {pi.dock_layer}"
        w, h = dc.GetTextExtent(s)
        dc.DrawText(s, (size.x - w) // 2, (size.y - height * 5) // 2 + height * 1)

        s = f"Dock: {pi.dock_direction} Row: {pi.dock_row}"
        w, h = dc.GetTextExtent(s)
        dc.DrawText(s, (size.x - w) // 2, (size.y - height * 5) // 2 + height * 2)

        s = f"Position: {pi.dock_pos}"
        w, h = dc.GetTextExtent(s)
        dc.DrawText(s, (size.x - w) // 2, (size.y - height * 5) // 2 + height * 3)

        s = f"Proportion: {pi.dock_proportion}"
        w, h = dc.GetTextExtent(s)
        dc.DrawText(s, (size.x - w) // 2, (size.y - height * 5) // 2 + height * 4)
