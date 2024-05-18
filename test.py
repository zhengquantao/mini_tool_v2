import wx
import wx.aui
import wx.lib.agw.aui as aui

class MyFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
        super(MyFrame, self).__init__(parent, id, title, pos, size, style)

        # 创建 AuiManager
        self._aui_manager = aui.AuiManager(self)

        # 创建 AuiToolBar
        toolbar = aui.AuiToolBar(self, style=aui.AUI_TB_OVERFLOW | aui.AUI_TB_VERT_TEXT | aui.AUI_TB_PLAIN_BACKGROUND & ~aui.AUI_TB_GRIPPER,
                                 )
        toolbar.AddSimpleTool(wx.ID_ANY, "Tool 1", wx.ArtProvider.GetBitmap(wx.ART_INFORMATION))
        toolbar.Realize()

        # 将工具栏添加到 AuiManager
        self._aui_manager.AddPane(toolbar, aui.AuiPaneInfo().Top().CloseButton(False))

        # 显示工具栏
        self._aui_manager.Update()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, title="AuiToolBar Example")
    frame.Show()
    app.MainLoop()
