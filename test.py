
import wx
import wx.lib.agw.aui as aui
# 定义数据模型
class MyModel:
    def __init__(self):
        self.count = 0
    def increase_count(self):
        self.count += 1
# 定义视图
class MyView(wx.Frame):
    def __init__(self, parent=None, title="My View", pos=wx.DefaultPosition, size=wx.DefaultSize):
        super().__init__(parent, title=title, pos=pos, size=size)
        self.model = MyModel()
        self.create_button()
        self.create_notebook()
    def create_button(self):
        self.toolbar = self.CreateToolBar()
        # self.toolbar.AddTool(wx.ID_ANY, 'Click me', "")
        self.toolbar.Realize()

    def create_notebook(self):
        self.notebook = aui.AuiNotebook(self, -1, agwStyle=aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_CLOSE_ON_ALL_TABS)
        self.notebook.AddPage(wx.Panel(self.notebook), "Page A")
        self.notebook.AddPage(wx.Panel(self.notebook), "Page B")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(sizer)
    def get_count(self):
        return self.model.count
# 定义控制器
class MyController:
    def __init__(self, view):
        self.view = view
        self.view.Bind(wx.EVT_TOOL, self.on_tool_click)
    def on_tool_click(self, event):
        self.view.model.increase_count()
        count = self.view.get_count()
        wx.MessageBox(f'Button clicked {count} times', 'Info', wx.OK | wx.ICON_INFORMATION)
if __name__ == "__main__":
    app = wx.App()
    view = MyView(title="My App", size=(500, 500))
    controller = MyController(view)
    view.Show()
    app.MainLoop()