"""Builds menubar.

This class relies on the order-preserving behavior of the stock Python
dictionary for both top-level menu labels and menu items.
"""
import os
import datetime
from multiprocessing import Process

import wx
import wx.lib.agw.aui as aui
from aui2 import svg_to_bitmap
from pubsub import pub as publisher

from common.common import new_app
from gui.convert_panel import ScadaPanel, PowerTheoreticalPanel, convert_gui
from gui.main_menu_res import main_menu_items
from settings.settings import main_title, __version__, icon_svg, contact_svg, web_svg, convert_svg, about_svg, doc_svg, \
    show_svg


# If MainFrame subclasses wx.Frame, uncomment the following lines
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from gui.main_frame import MainFrame


# noinspection PyPep8Naming
class MainMenu:

    # If MainFrame subclasses wx.Frame, replace the following line
    # def __init__(self, frame: "MainFrame", mgr: aui.AuiManager) -> None:
    def __init__(self, frame: wx.Frame, mgr: aui.AuiManager) -> None:
        self.frame = frame
        self.mgr = mgr
        self.menubar = wx.MenuBar()
        self.item_ids = {}
        self.items = {}
        self.project_path = ""
        self.build()
        frame.SetMenuBar(self.menubar)
        publisher.subscribe(self.send_project_path, "send_project_path")

    def art_provider(self) -> aui.AuiDefaultDockArt:
        return self.mgr.GetArtProvider()

    def build(self) -> wx.MenuBar:
        menubar = self.menubar
        for child_key, child in main_menu_items.items():
            menu = self.build_menu(child["children"])
            self.items[child_key] = menu
            menubar.Append(menu, child["label"])
        self.build_standard()
        return menubar

    def build_menu(self, children: dict) -> wx.Menu:
        """Builds wx.Menu, including submenus (recursively)

        Args:
          children: {"<child_key>": {"type": "<type>", "label": "<label>", "children": "<children>"}}

        Returns:
          wx.Menu tree.
        """
        menu: wx.Menu = wx.Menu()
        child_key: str
        child: dict
        submenu: wx.Menu
        for child_key, child in children.items():
            child_label: str = child["label"]
            child_type: str = child.get("type", "basic")
            item_id: wx.WindowIDRef = child.get("id") or wx.ID_ANY
            if child_type == "submn":
                submenu = self.build_menu(child["children"])
                self.items[child_key] = submenu
                menu.AppendSubMenu(submenu, child_label)
            else:
                self.append_menu_line(menu, child_key, child_label, child_type, item_id, child.get("icon"))
        return menu

    def append_menu_line(self, menu: wx.Menu, item_key: str, item_label: str,
                         item_type: str, item_id: wx.WindowIDRef = wx.ID_ANY, icon=None) -> None:
        menu_item: wx.MenuItem
        if not item_label:
            menu_item = menu.AppendSeparator()
            self.items[item_key] = {"id": 0, "type": item_type, "item": menu_item}
            return
        if item_id == wx.ID_ANY:
            item_id = wx.NewIdRef()
        if item_type == "basic":
            menu_item = menu.Append(item_id, item_label)
        elif item_type == "radio":
            menu_item = menu.AppendRadioItem(item_id, item_label)
        elif item_type == "check":
            menu_item = menu.AppendCheckItem(item_id, item_label)
        else:
            raise ValueError(f"Unknown menu item type: <{item_type}>")
        icon and menu_item.SetBitmap(svg_to_bitmap(icon, size=(16, 16)))
        self.item_ids[item_id] = item_key
        self.items[item_key] = {"id": item_id, "type": item_type, "item": menu_item}

    def build_standard(self):
        # self.items["Edit"].Append(wx.ID_COPY, "Copy")
        # self.items["Edit"].Append(wx.ID_PASTE, "Paste")
        # self.items["Edit"].Append(wx.ID_CUT, "Cut")
        # self.items["Edit"].Append(wx.ID_BACKWARD, "Back")
        # self.items["Edit"].Enable(wx.ID_BACKWARD, False)
        # delete_menu = self.items["Edit"].Append(wx.ID_DELETE, "Delete")
        # delete_menu.SetBitmap(svg_to_bitmap(delete_svg, size=(16, 16)))
        # self.items["Edit"].Enable(wx.ID_DELETE, False)

        id_covert_data = wx.NewId()
        id_covert_power = wx.NewId()
        scada_menu = self.items["Tools"].Append(id_covert_power, "转换理论功率数据")
        scada_menu.SetBitmap(svg_to_bitmap(convert_svg, size=(15, 15)))
        self.frame.Bind(wx.EVT_MENU, self.on_convert_power, id=id_covert_power)
        scada_menu = self.items["Tools"].Append(id_covert_data, "转换SCADA数据")
        scada_menu.SetBitmap(svg_to_bitmap(convert_svg, size=(15, 15)))
        self.frame.Bind(wx.EVT_MENU, self.on_convert_scada, id=id_covert_data)

        doc_menu = self.items["Help"].Append(wx.ID_HELP, "文档")
        doc_menu.SetBitmap(svg_to_bitmap(doc_svg, size=(15, 15)))

        self.frame.Bind(wx.EVT_MENU, self.on_help, id=wx.ID_HELP)
        contact_menu = self.items["Help"].Append(wx.ID_HELP_CONTEXT, "联系我们")
        contact_menu.SetBitmap(svg_to_bitmap(contact_svg, size=(15, 15)))
        self.frame.Bind(wx.EVT_MENU, self.on_contact, id=wx.ID_HELP_CONTEXT)
        about_menu = self.items["Help"].Append(wx.ID_ABOUT, "关于我们")
        about_menu.SetBitmap(svg_to_bitmap(about_svg, size=(15, 15)))
        self.frame.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        web_menu = self.items["Help"].Append(wx.ID_HELP_CONTENTS, "官网")
        web_menu.SetBitmap(svg_to_bitmap(web_svg, size=(15, 15)))
        self.frame.Bind(wx.EVT_MENU, self.on_web_home, id=wx.ID_HELP_CONTENTS)
        self.items["Help"].AppendSeparator()
        show_menu = self.items["Help"].Append(wx.ID_HELP_PROCEDURES, "演示项目")
        show_menu.SetBitmap(svg_to_bitmap(show_svg, size=(15, 15)))
        self.frame.Bind(wx.EVT_MENU, self.on_test_project, id=wx.ID_HELP_PROCEDURES)

    def on_about(self, _event: wx.CommandEvent) -> None:
        # msg = "wx.aui Demo\nAn advanced library for wxWidgets"
        # dlg = wx.MessageDialog(self.frame, msg, "About wx.aui Demo", wx.OK | wx.ICON_INFORMATION)
        # dlg.ShowModal()
        # dlg.Destroy()

        """show about dialog"""
        dlg = AboutDialog(self.frame)
        dlg.ShowModal()
        dlg.Destroy()

    def send_project_path(self, path):
        self.project_path = path

    def on_help(self, _event: wx.CommandEvent) -> None:
        wx.CallAfter(publisher.sendMessage, "add_pdf")

    def on_contact(self, _event: wx.CommandEvent):
        msg = """
        公司: 深圳量云能源网络科技有限公司\n
        网址: https://www.quant-cloud.cn\n
        电话: 0755-86523057\n
        Email: quant-cloud@mywind.com.cn\n 
        地址: 深圳市前海深港合作区南山街道梦海大道5033号前海卓越金融中心3号楼L10-01
        """
        dlg = wx.MessageDialog(self.frame, msg, "联系我们", wx.OK | wx.ICON_NONE)
        dlg.ShowModal()
        dlg.Destroy()

    def on_web_home(self, _event: wx.CommandEvent):
        """go to web homepage"""
        web_url = "https://www.quant-cloud.cn/home.html"
        try:
            wx.BeginBusyCursor()
            import webbrowser
            webbrowser.open(web_url)
            wx.EndBusyCursor()
        except:
            wx.MessageBox(web_url, "量云官网",  wx.OK | wx.ICON_NONE)

    def on_test_project(self, _event: wx.CommandEvent):
        """open test project"""
        test_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "static", "js", "演示项目")
        new_app(test_path)

    def on_convert_scada(self, _event: wx.CommandEvent):
        Process(target=convert_gui, args=(ScadaPanel, self.project_path)).start()

    def on_convert_power(self, _event: wx.CommandEvent):
        Process(target=convert_gui, args=(PowerTheoreticalPanel, self.project_path)).start()


class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self,
                           parent,
                           title=f"关于 {main_title}",
                           style=wx.DEFAULT_DIALOG_STYLE)

        szAll = wx.BoxSizer(wx.VERTICAL)

        self.panel = wx.Panel(self, style=wx.TAB_TRAVERSAL)
        self.panel.SetBackgroundColour(wx.WHITE)

        szPanelAll = wx.BoxSizer(wx.HORIZONTAL)

        self.header = wx.StaticBitmap(self.panel)
        self.header.SetBitmap(svg_to_bitmap(icon_svg, size=(128, 128), win=self))
        szPanelAll.Add(self.header, 0, wx.EXPAND | wx.LEFT, 4)

        szPanel = wx.BoxSizer(wx.VERTICAL)
        szPanel.AddStretchSpacer(1)
        max_size = 300
        caption = f'{main_title} {__version__}'
        self.stCaption = wx.StaticText(self.panel, wx.ID_ANY, caption)
        self.stCaption.SetMaxSize((max_size, -1))
        self.stCaption.Wrap(max_size)
        self.stCaption.SetFont(wx.Font(pointSize=16, family=wx.FONTFAMILY_DEFAULT,
                                       style=wx.FONTSTYLE_NORMAL,
                                       weight=wx.FONTWEIGHT_NORMAL,
                                       underline=False))

        szPanel.Add(self.stCaption, 0, wx.ALL | wx.EXPAND, 5)

        strCopyright = f'(c)2015-{datetime.datetime.now().year} Shenzhen Quant-Cloud Energy Network Technology Co., Ltd.'
        self.stCopyright = wx.StaticText(self.panel, wx.ID_ANY, strCopyright)
        self.stCopyright.SetMaxSize((max_size, -1))
        self.stCopyright.Wrap(max_size)
        self.stCopyright.SetFont(wx.Font(pointSize=10, family=wx.FONTFAMILY_DEFAULT,
                                         style=wx.FONTSTYLE_NORMAL,
                                         weight=wx.FONTWEIGHT_NORMAL,
                                         underline=False))
        szPanel.Add(self.stCopyright, 0, wx.ALL | wx.EXPAND, 5)

        build = wx.GetOsDescription() + '; wxWidgets ' + wx.version()
        self.stBuild = wx.StaticText(self.panel, wx.ID_ANY, build)
        self.stBuild.SetMaxSize((max_size, -1))
        self.stBuild.Wrap(max_size)
        self.stBuild.SetFont(wx.Font(pointSize=10, family=wx.FONTFAMILY_DEFAULT,
                                     style=wx.FONTSTYLE_NORMAL,
                                     weight=wx.FONTWEIGHT_NORMAL,
                                     underline=False))
        szPanel.Add(self.stBuild, 0, wx.ALL | wx.EXPAND, 5)

        stLine = wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL)
        szPanel.Add(stLine, 0, wx.EXPAND | wx.ALL, 10)
        szPanel.AddStretchSpacer(1)

        szPanelAll.Add(szPanel, 1, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(szPanelAll)
        self.panel.Layout()
        szPanel.Fit(self.panel)

        szAll.Add(self.panel, 1, wx.EXPAND | wx.ALL, 0)

        btnsizer = wx.StdDialogButtonSizer()

        self.btnOK = wx.Button(self, wx.ID_OK)
        self.btnOK.SetDefault()
        btnsizer.AddButton(self.btnOK)
        btnsizer.Realize()

        szAll.Add(btnsizer, 0, wx.ALIGN_RIGHT | wx.BOTTOM, 5)

        self.SetSizer(szAll)
        self.Layout()
        szAll.Fit(self)
        self.Centre()
