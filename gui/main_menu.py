"""Builds menubar.

This class relies on the order-preserving behavior of the stock Python
dictionary for both top-level menu labels and menu items.
"""
import datetime

import wx
import wx.lib.agw.aui as aui
from aui2 import svg_to_bitmap

from gui.convert_panel import ScadaPanel, PowerTheoreticalPanel
from gui.main_menu_res import main_menu_items
from settings.settings import main_title, __version__, icon_svg, delete_svg, contact_svg, web_svg


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
        self.build()
        frame.SetMenuBar(self.menubar)

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
        self.items["Tools"].Append(id_covert_data, "Convert SCADA")
        self.frame.Bind(wx.EVT_MENU, self.on_convert_scada, id=id_covert_data)
        self.items["Tools"].Append(id_covert_power, "Convert POWER")
        self.frame.Bind(wx.EVT_MENU, self.on_convert_power, id=id_covert_power)

        self.items["Help"].Append(wx.ID_HELP)
        self.frame.Bind(wx.EVT_MENU, self.on_help, id=wx.ID_HELP)
        contact_menu = self.items["Help"].Append(wx.ID_HELP_CONTEXT, "Contact Us")
        contact_menu.SetBitmap(svg_to_bitmap(contact_svg, size=(15, 15)))
        self.frame.Bind(wx.EVT_MENU, self.on_contact, id=wx.ID_HELP_CONTEXT)
        self.items["Help"].Append(wx.ID_ABOUT)
        self.frame.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        web_menu = self.items["Help"].Append(wx.ID_HELP_CONTENTS, "WebSite")
        web_menu.SetBitmap(svg_to_bitmap(web_svg, size=(15, 15)))
        self.frame.Bind(wx.EVT_MENU, self.on_web_home, id=wx.ID_HELP_CONTENTS)

    def on_about(self, _event: wx.CommandEvent) -> None:
        # msg = "wx.aui Demo\nAn advanced library for wxWidgets"
        # dlg = wx.MessageDialog(self.frame, msg, "About wx.aui Demo", wx.OK | wx.ICON_INFORMATION)
        # dlg.ShowModal()
        # dlg.Destroy()

        """show about dialog"""
        dlg = AboutDialog(self.frame)
        dlg.ShowModal()
        dlg.Destroy()

    def on_help(self, _event: wx.CommandEvent) -> None:
        msg = "Energy efficiency assistant \nAn advanced scientific analysis  tool for operations personnel"
        dlg = wx.MessageDialog(self.frame, msg, "Help You", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def on_contact(self, _event: wx.CommandEvent):
        msg = "Website: https://www.quant-cloud.cn \nPhone :110 3423 3242\n Email: 123234224324@qq.com \n Address: 中国广东省深圳市南山区前海街道50034号4楼"
        dlg = wx.MessageDialog(self.frame, msg, "Contact Us", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def on_web_home(self, _event: wx.CommandEvent):
        """go to web homepage"""
        wx.BeginBusyCursor()
        import webbrowser
        webbrowser.open("https://www.quant-cloud.cn/home.html")
        wx.EndBusyCursor()

    def on_convert_scada(self, _event: wx.CommandEvent):
        ScadaPanel(self.frame)

    def on_convert_power(self, _event: wx.CommandEvent):
        PowerTheoreticalPanel(self.frame)


class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self,
                           parent,
                           title=f"About {main_title}",
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
        MAX_SIZE = 300
        caption = f'{main_title} {__version__}'
        self.stCaption = wx.StaticText(self.panel, wx.ID_ANY, caption)
        self.stCaption.SetMaxSize((MAX_SIZE, -1))
        self.stCaption.Wrap(MAX_SIZE)
        self.stCaption.SetFont(wx.Font(pointSize=16, family=wx.FONTFAMILY_DEFAULT,
                                       style=wx.FONTSTYLE_NORMAL,
                                       weight=wx.FONTWEIGHT_NORMAL,
                                       underline=False))

        szPanel.Add(self.stCaption, 0, wx.ALL | wx.EXPAND, 5)

        strCopyright = f'(c) 2018-{datetime.datetime.now().year} Shenzhen LiangYun.\n All rights reserved.'
        self.stCopyright = wx.StaticText(self.panel, wx.ID_ANY, strCopyright)
        self.stCopyright.SetMaxSize((MAX_SIZE, -1))
        self.stCopyright.Wrap(MAX_SIZE)
        self.stCopyright.SetFont(wx.Font(pointSize=10, family=wx.FONTFAMILY_DEFAULT,
                                         style=wx.FONTSTYLE_NORMAL,
                                         weight=wx.FONTWEIGHT_NORMAL,
                                         underline=False))
        szPanel.Add(self.stCopyright, 0, wx.ALL | wx.EXPAND, 5)

        build = wx.GetOsDescription() + '; wxWidgets ' + wx.version()
        self.stBuild = wx.StaticText(self.panel, wx.ID_ANY, build)
        self.stBuild.SetMaxSize((MAX_SIZE, -1))
        self.stBuild.Wrap(MAX_SIZE)
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
