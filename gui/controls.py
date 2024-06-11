import datetime
import os
from threading import Thread

import pandas as pd
import wx
import wx.grid
import wx.html2
import wx.lib.agw.customtreectrl as CT
import wx.lib.agw.aui as aui
from pubsub import pub as publisher

# If MainFrame subclasses wx.Frame, uncomment the following lines
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from gui.main_frame import MainFrame
from aui2 import svg_to_bitmap

from common.common import read_file, remove_file, rename_file, get_file_info, add_notebook_page, detect_encoding
from common import loggers
from gui.gauge_panel import GaugePanel
from models.bin_main import bin_main
from models.compare_curve import compare_curve, compare_curve_all
from models.dswe_main import iec_main
from models.geo_main import geo_main
# from settings.resources import overview
from settings.settings import opening_dict, float_size, display_grid_count, model2_svg, model1_svg, result_dir


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
        frame.Bind(wx.EVT_MENU, self.on_create, id=self.create_menu_id)

    def start_position(self) -> wx.Point:
        return self.frame.ClientToScreen(wx.Point(0, 0)) + (wx.Point(2, 2) * self.__class__.counter)

    def create_ctrl(self, parent=None, data_df=None) -> wx.Panel:
        if not parent:
            parent = self.frame
        self.__class__.counter += 1

        panel = wx.Panel(parent, -1)
        grid = wx.grid.Grid(panel, wx.ID_ANY, wx.Point(0, 0), size=wx.Size(*float_size),
                            style=wx.NO_BORDER)

        grid.CreateGrid(100, 50)  # 创建一个n行n列的表格
        grid.EnableScrolling(True, True)
        # 边框颜色
        grid.SetGridLineColour(wx.LIGHT_GREY)

        # 渲染表格
        self.render_grid(data_df, grid)

        # 设置panel自适应屏幕
        sizer = wx.BoxSizer(wx.VERTICAL)
        # 1 自动铺满窗口
        sizer.Add(grid, 1, wx.ALL | wx.EXPAND, 0)
        panel.SetSizer(sizer)
        return panel

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

    def on_create(self, _event: wx.CommandEvent) -> None:
        ctrl: wx.Panel = self.create_ctrl()
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
        frame.Bind(wx.EVT_MENU, self.on_create, id=self.create_menu_id)

    def start_position(self) -> wx.Point:
        return self.frame.ClientToScreen(wx.Point(0, 0)) + (wx.Point(2, 2) * self.__class__.counter)

    def create_ctrl(self, parent=None, text: str = "", width: int = 500, height: int = 400, style=wx.TE_MULTILINE,
                    font=None) -> wx.TextCtrl:
        if not parent:
            parent = self.frame
        self.__class__.counter += 1
        ctrl = wx.TextCtrl(parent, wx.ID_ANY, text, wx.DefaultPosition,
                           wx.Size(width, height), style=style)
        if not font:
            font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
        ctrl.SetMargins(8)
        ctrl.SetFont(font)
        return ctrl

    def on_create(self, _event: wx.CommandEvent) -> None:
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
        frame.Bind(wx.EVT_MENU, self.on_create, id=self.create_menu_id)
        publisher.subscribe(self.add_page, "add_page")

        self.result_dir = None
        self.gauge = None

    def add_page(self, msg):
        file_paths, file_name = msg
        add_notebook_page(self.notebook_ctrl, self.html_ctrl, file_paths, file_name)
        if not self.gauge:
            return
        self.gauge.destroy()
        self.gauge = None

        if not self.result_dir:
            self.result_dir = self.tree.AppendItem(self.root, result_dir, image=0, data=os.path.dirname(file_paths))
            self.tree.EnsureVisible(self.result_dir)
        new_item = self.tree.AppendItem(self.result_dir, file_name, image=2, data=file_paths)
        self.tree.EnsureVisible(new_item)

    def update_file_tree(self, event, path=None):
        project_path = opening_dict[os.getpid()]["path"]
        new_file_list = get_file_info(project_path)
        if new_file_list == self.now_file_list:
            return

        self.tree.DeleteChildren(self.root)
        self.build_tree(project_path, self.root)
        self.tree.SortChildren(self.root)
        self.tree.Expand(self.root)
        self.now_file_list = new_file_list
        loggers.logger.info("当前有文件改动")
        # self.tree.Refresh()

    def start_position(self) -> wx.Point:
        return self.frame.ClientToScreen(wx.Point(0, 0)) + (wx.Point(2, 2) * self.__class__.counter)

    def create_ctrl(self, path="./", init_project=False) -> CT.CustomTreeCtrl:
        self.__class__.counter += 1
        # self.tree: wx.TreeCtrl = wx.TreeCtrl(self.frame, wx.ID_ANY, wx.Point(0, 0), wx.Size(160, 250),
        #                                      wx.TR_DEFAULT_STYLE | wx.TR_TWIST_BUTTONS | wx.TR_NO_LINES | wx.NO_BORDER)
        self.tree = CT.CustomTreeCtrl(self.frame, wx.ID_ANY, wx.Point(-1, -1), wx.Size(160, 500),
                                      agwStyle=wx.TR_HAS_BUTTONS | wx.TR_TWIST_BUTTONS | wx.TR_NO_LINES | wx.NO_BORDER)
        self.tree.SetDoubleBuffered(True)

        if init_project:
            return self.tree

        imglist: wx.ImageList = wx.ImageList(16, 16, True, 2)
        icons = [wx.ART_FOLDER, wx.ART_FILE_OPEN, wx.ART_NORMAL_FILE]
        for icon in icons:
            imglist.Add(wx.ArtProvider.GetBitmap(icon, wx.ART_OTHER, wx.Size(16, 16)))
        self.tree.AssignImageList(imglist)
        root_name = path.split(os.sep)[-1]
        self.now_file_list = get_file_info(path)
        self.root: wx.TreeItemId = self.tree.AddRoot(root_name, 0, data=path)
        self.tree.SetItemImage(self.root, 0, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, 0, wx.TreeItemIcon_Expanded)

        self.build_tree(path, self.root)
        self.tree.SortChildren(self.root)
        self.tree.Expand(self.root)

        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_right_click_up)
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_item_expanded)
        self.tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_item_collapsed)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGING, self.on_sel_changing)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_open)

        return self.tree

    def on_create(self, _event: wx.CommandEvent) -> None:
        ctrl: CT.CustomTreeCtrl = self.create_ctrl()
        caption = "Tree Control"
        self.mgr.AddPane(ctrl, aui.AuiPaneInfo().Caption(caption).
                         FloatingPosition(self.start_position()).CloseButton(False).
                         MaximizeButton(True).MinimizeButton(True).Floatable(False).Dockable(False))
        self.mgr.Update()
        ctrl.Refresh()

    def build_tree(self, dir_path, parent_item):
        for item in os.listdir(dir_path):
            if item.endswith(".mini"):
                continue

            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                new_item = self.tree.AppendItem(parent_item, item)
                self.tree.SetItemImage(new_item, 0)
                self.tree.SetItemData(new_item, item_path)
                if item == result_dir and not self.result_dir:
                    self.result_dir = new_item
                self.build_tree(item_path, new_item)
            else:
                new_item = self.tree.AppendItem(parent_item, item)
                self.tree.SetItemImage(new_item, 2)
                self.tree.SetItemData(new_item, item_path)

    def on_right_click_up(self, event):
        item = event.GetItem()

        if not item:
            event.Skip()
            return

        if not self.tree.IsItemEnabled(item):
            event.Skip()
            return

        self.current = item

        path = self.tree.GetItemData(item)
        print(f"right clicked, path: {path}")

        menu = wx.Menu()
        open_item = menu.Append(wx.ID_ANY, '打开')

        delete_item = menu.Append(wx.ID_ANY, '删除')
        rename_item = menu.Append(wx.ID_ANY, '重命名')
        # 文件夹才能创建文件夹
        if os.path.isdir(path):
            dir_item = menu.Append(wx.ID_ANY, '新建文件夹')
            flush_item = menu.Append(wx.ID_ANY, '刷新')
            self.tree.Bind(wx.EVT_MENU, lambda event: self.on_new_dir(event, path), dir_item)
            self.tree.Bind(wx.EVT_MENU, lambda event: self.update_file_tree(event, path), flush_item)

        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_open(event, path), open_item)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_delete(event, path), delete_item)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_rename(event, path), rename_item)

        # 能效分析
        self.menu_model1(menu, path)
        # 控制曲线分析（Bin分仓）
        self.menu_model2(menu, path)

        self.tree.PopupMenu(menu)

    def menu_model1(self, menu, path):
        sub_model_menu1 = wx.Menu()
        if os.path.isdir(path):
            menu.AppendSeparator()
            model_1 = sub_model_menu1.Append(wx.ID_ANY, '能效等级总览')
            model_2 = sub_model_menu1.Append(wx.ID_ANY, '能效评估结果总览')
            model_3 = sub_model_menu1.Append(wx.ID_ANY, '能效排行总览')
            model_6 = sub_model_menu1.Append(wx.ID_ANY, '风资源对比总览')
            model_12 = sub_model_menu1.Append(wx.ID_ANY, "赛马排行总览")
            self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_1(event, path), model_1)
            self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_2(event, path), model_2)
            self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_3(event, path), model_3)
            self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_6(event, path), model_6)
            self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_12(event, path), model_12)
            menu.AppendSubMenu(sub_model_menu1, '能效分析').SetBitmap(svg_to_bitmap(model1_svg, size=(13, 13)))

        elif path.endswith(".csv"):
            menu.AppendSeparator()
            model_4 = sub_model_menu1.Append(wx.ID_ANY, '理论与实际功率对比分析')
            model_5 = sub_model_menu1.Append(wx.ID_ANY, '风资源对比')
            self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_4(event, path), model_4)
            self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_5(event, path), model_5)
            menu.AppendSubMenu(sub_model_menu1, '能效分析').SetBitmap(svg_to_bitmap(model1_svg, size=(13, 13)))

    def menu_model2(self, menu, path):
        """
        # 控制曲线分析（Bin分仓）
        """
        if not all([os.path.isfile(path), path.endswith(".csv")]):
            return

        sub_model_menu2 = wx.Menu()
        # 控制曲线分析（Bin分仓）
        model_7 = sub_model_menu2.Append(wx.ID_ANY, '风速-风能利用系数分析')
        model_8 = sub_model_menu2.Append(wx.ID_ANY, '风速-桨距角分析')
        model_9 = sub_model_menu2.Append(wx.ID_ANY, '桨距角-功率分析')
        model_10 = sub_model_menu2.Append(wx.ID_ANY, '风速-转速分析')
        model_11 = sub_model_menu2.Append(wx.ID_ANY, '转速-功率分析')

        menu.AppendSubMenu(sub_model_menu2, '控制曲线分析').SetBitmap(svg_to_bitmap(model2_svg, size=(13, 13)))
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_7(event, path), model_7)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_8(event, path), model_8)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_9(event, path), model_9)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_10(event, path), model_10)
        self.tree.Bind(wx.EVT_MENU, lambda event: self.on_model_11(event, path), model_11)

    def on_delete(self, event, path):
        loggers.logger.info(f"Delete clicked, file path: {path}")
        dlg = wx.MessageDialog(self.frame, f"你确认要删除文件 {path.split(os.sep)[-1]} 吗？",
                               "刪除文件", wx.YES_NO | wx.ICON_WARNING)
        if dlg.ShowModal() != wx.ID_YES:
            return

        self.tree.DeleteChildren(self.current)
        self.tree.Delete(self.current)
        self.current = None

        remove_file(path)

    def on_open(self, event, path=None):

        if not path:
            path = self.tree.GetItemData(event.GetItem())

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
            ctrl.AddPage(self.html_ctrl.create_ctrl(parent=ctrl, path=path), file_name, True, page_bmp)

        elif any([path.endswith(".csv"), path.endswith(".xlsx"), path.endswith(".xls")]):
            data_df = pd.read_csv(path, encoding=detect_encoding(path))
            ctrl.AddPage(self.grid_ctrl.create_ctrl(ctrl, data_df), file_name, True, page_bmp)

        elif any([path.endswith(".png"), path.endswith(".jpg"), path.endswith(".jpeg")]):
            image = wx.Bitmap(path)
            # size = self.mgr.GetPaneByName("notebook_content").window.GetSize()
            # image = image.Rescale(size[0], size[1])
            image_ctrl = wx.StaticBitmap(ctrl, wx.ID_ANY, image)
            ctrl.AddPage(image_ctrl, file_name, True, page_bmp)

        else:
            page = wx.TextCtrl(ctrl, wx.ID_ANY, text, wx.DefaultPosition, wx.DefaultSize,
                               wx.TE_MULTILINE | wx.NO_BORDER)
            page.SetMargins(5, top=3)
            font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
            page.SetFont(font)
            ctrl.AddPage(page, file_name, True, page_bmp)

    def on_new_dir(self, event, path):
        dlg = wx.TextEntryDialog(self.frame, "请输入文件夹名称:", "新建文件夹")
        if dlg.ShowModal() != wx.ID_OK:
            return

        directory_name: str = dlg.GetValue()
        if os.path.isfile(path):
            path = os.path.dirname(path)

        os.makedirs(os.path.join(path, directory_name), exist_ok=True)

        new_item = self.tree.AppendItem(self.current, directory_name, image=0, data=os.path.join(path, directory_name))
        self.tree.EnsureVisible(new_item)

    def on_rename(self, event, path):
        loggers.logger.info(f"Rename clicked, file path: {path}")
        file_list = path.split(os.sep)
        dlg = wx.TextEntryDialog(self.frame, "请输入新文件名:", "文件重命名", value=file_list[-1])
        if dlg.ShowModal() != wx.ID_OK:
            return

        directory_name: str = dlg.GetValue()
        file_list[-1] = directory_name
        rename_file(path, os.sep.join(file_list))
        self.tree.SetItemText(self.current, directory_name)
        self.tree.SetPyData(self.current, os.sep.join(file_list))

    def on_model_1(self, event, path):
        """能效等级总览"""
        loggers.logger.info(f"能效等级总览 clicked, path: {path}")

        if self.open_history_html_file(path, "能效等级总览"):
            return

        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(geo_main, path, project_path))
        thread.start()
        self.gauge = GaugePanel(self.frame, "能效等级总览", thread.ident)

    def on_model_2(self, event, path):
        """能效评估结果总览"""
        loggers.logger.info(f"能效评估结果总览 clicked, path: {path}")

        if self.open_history_html_file(path, "能效评估结果总览"):
            return

        # 能效评估结果总览
        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(iec_main, path, project_path))
        thread.start()
        self.gauge = GaugePanel(self.frame, "能效评估结果总览", thread.ident)

    def on_model_3(self, event, path):
        """能效排行总览"""
        loggers.logger.info(f"能效排行总览 clicked, path: {path}")

        if self.open_history_html_file(path, "能效排行总览"):
            return

        # 能效评估结果总览
        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(iec_main, path, project_path, True))
        thread.start()
        self.gauge = GaugePanel(self.frame, "能效排行总览", thread.ident)

    def on_model_4(self, event, path):
        """理论与实际功率对比分析"""
        loggers.logger.info(f"理论与实际功率对比分析 clicked, path: {path}")

        if self.open_history_html_file(path, "理论与实际功率对比分析"):
            return

        # 理论和实际功率曲线对比
        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(compare_curve, path, project_path))
        thread.start()
        self.gauge = GaugePanel(self.frame, "理论与实际功率对比分析", thread.ident)

    def on_model_5(self, event, path):
        """风资源对比"""
        loggers.logger.info(f"风资源对比 clicked, path: {path}")

        if self.open_history_html_file(path, "风资源对比"):
            return

        # 风资源对比
        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(compare_curve, path, project_path, 1, True))
        thread.start()
        self.gauge = GaugePanel(self.frame, "风资源对比", thread.ident)

    def on_model_6(self, event, path):
        """风资源对比总览"""
        loggers.logger.info(f"风资源对比总览 clicked, path: {path}")

        if self.open_history_html_file(path, "风资源对比总览"):
            return

        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(compare_curve_all, path, project_path, 1, True))
        thread.start()
        self.gauge = GaugePanel(self.frame, "风资源对比总览", thread.ident)

    def on_model_7(self, event, path):
        """风速-风能利用系数分析"""
        loggers.logger.info(f"风速-风能利用系数分析 clicked, path: {path}")
        if self.open_history_html_file(path, "风速-风能利用系数分析"):
            return

        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(bin_main, path, project_path, False, ["cp_windspeed"]))
        thread.start()
        self.gauge = GaugePanel(self.frame, "风速-风能利用系数分析", thread.ident)

    def on_model_8(self, event, path):
        """风速-桨距角分析"""
        loggers.logger.info(f"风速-桨距角分析 clicked, path: {path}")
        if self.open_history_html_file(path, "风速-桨距角分析"):
            return

        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(bin_main, path, project_path, False, ["pitch_windspeed"]))
        thread.start()
        self.gauge = GaugePanel(self.frame, "风速-桨距角分析", thread.ident)

    def on_model_9(self, event, path):
        """桨距角-功率分析"""
        loggers.logger.info(f"桨距角-功率分析 clicked, path: {path}")
        if self.open_history_html_file(path, "桨距角-功率分析"):
            return

        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(bin_main, path, project_path, False, ["power_pitch"]))
        thread.start()
        self.gauge = GaugePanel(self.frame, "桨距角-功率分析", thread.ident)

    def on_model_10(self, event, path):
        """风速-转速分析"""
        loggers.logger.info(f"风速-转速分析 clicked, path: {path}")
        if self.open_history_html_file(path, "风速-转速分析"):
            return

        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(bin_main, path, project_path, False, ["gen_wind_speed"]))
        thread.start()
        self.gauge = GaugePanel(self.frame, "风速-转速分析", thread.ident)

    def on_model_11(self, event, path):
        """转速-功率分析"""
        loggers.logger.info(f"转速-功率分析 clicked, path: {path}")
        if self.open_history_html_file(path, "转速-功率分析"):
            return

        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(bin_main, path, project_path, False, ["power_genspeed"]))
        thread.start()
        self.gauge = GaugePanel(self.frame, "转速-功率分析", thread.ident)

    def on_model_12(self, event, path):
        """赛马排行总览"""
        loggers.logger.info(f"能效评估结果总览 clicked, path: {path}")

        if self.open_history_html_file(path, "赛马排行总览"):
            return

        # 能效评估结果总览
        project_path = opening_dict[os.getpid()]["path"]
        thread = Thread(target=self.async_model, args=(iec_main, path, project_path, False, True))
        thread.start()
        self.gauge = GaugePanel(self.frame, "赛马排行总览", thread.ident)

    def open_history_html_file(self, path, operation_type) -> bool:
        """
        当前打开的文件已经存在结果，且文件最后编辑时间<结果创建时间，则直接打开结果
        """
        last_updated_time = os.path.getmtime(path)
        project_path = opening_dict[os.getpid()]["path"]
        if os.path.isfile(path):
            name = path.split(os.sep)[-1][:-4]
        else:
            name = path.split(os.sep)[-1]

        result_dir_path = os.path.join(project_path, result_dir)
        results_path_lists = os.listdir(result_dir_path)
        file_name = ""
        for result_path in results_path_lists:
            # result_path: 30057008-风速-桨距角分析 30057008-20240524103450.html
            if not result_path.startswith(f"{name}-{operation_type}") or not result_path.endswith(".html"):
                continue
            file_time = result_path.split("-")[-1].split(".")[0]
            create_time = datetime.datetime.strptime(file_time, "%Y%m%d%H%M%S").timestamp()
            if create_time < last_updated_time:
                continue
            file_name = result_path
            break

        if not file_name:
            return False

        self.on_open(wx.Event, os.path.join(result_dir_path, file_name))
        return True

    def on_item_expanded(self, event):
        print("Item expanded!")

    def on_item_collapsed(self, event):
        print("Item collapsed!")

    def on_sel_changed(self, event):
        print("Selection changed")

    def on_sel_changing(self, event):
        print("Selection changing")

    def async_model(self, callable_func, *args):
        file_paths, file_name = callable_func(*args)
        # 防止多线程操作主进程页面导致异常崩溃
        wx.CallAfter(publisher.sendMessage, "add_page", msg=(file_paths, file_name))


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
        frame.Bind(wx.EVT_MENU, self.on_create, id=self.create_menu_id)

    def start_position(self) -> wx.Point:
        return self.frame.ClientToScreen(wx.Point(0, 0)) + (wx.Point(2, 2) * self.__class__.counter)

    def create_ctrl(self, parent: wx.Frame = None, path: str = "") -> wx.html2.WebView:
        self.__class__.counter += 1
        if not parent:
            parent = self.frame
        # wx.html2仅支持到echarts<=3.7.0的版本
        ctrl = wx.html2.WebView.New(parent, size=wx.Size(*float_size))
        # print(ctrl.GetBackendVersionInfo().Name)
        ctrl.LoadURL(f"file:///{path}")
        # ctrl = CefFrame(parent, f"file:///{path}")
        return ctrl

    def on_create(self, _event: wx.CommandEvent, caption="HTML Control", path="", width=700, height=400) -> None:
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
        frame.Bind(wx.EVT_MENU, self.on_create, id=self.create_menu_id)

    def create_ctrl(self, parent=None, width: int = 80, height: int = 80) -> wx.Control:
        self.__class__.counter += 1
        if not parent:
            parent = self.frame
        ctrl = wx.Control(parent, wx.ID_ANY, wx.DefaultPosition,
                          wx.Size(width, height), style=wx.NO_BORDER)
        ctrl.Bind(wx.EVT_PAINT, self.OnPaint)
        ctrl.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        ctrl.Bind(wx.EVT_SIZE, self.OnSize)
        return ctrl

    def start_position(self) -> wx.Point:
        return self.frame.ClientToScreen(wx.Point(0, 0)) + (wx.Point(2, 2) * self.__class__.counter)

    def on_create(self, _event: wx.CommandEvent) -> None:
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
