import wx
from wx.lib.agw import aui
from cefpython3 import cefpython as cef

class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent=parent, title="CEFPython wxPython AuiManager Demo",
                          size=(800, 600))

        self._init_aui_manager()
        self._init_cef()

    def _init_aui_manager(self):
        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        # Create a panel for the browser
        self.browser_panel = wx.Panel(self, size=(500, 400))

        # Add the browser panel to the AuiManager
        self._mgr.AddPane(self.browser_panel, aui.AuiPaneInfo().Name("browser_content").
                          CenterPane().Hide().CaptionVisible(False))

        # Add a toolbar
        toolbar = aui.AuiToolBar(self, -1, )
        toolbar.SetToolBitmapSize(wx.Size(16, 16))

        # Add some tools to the toolbar
        id_back = wx.NewIdRef()
        toolbar.AddSimpleTool(id_back, "Back", wx.ArtProvider.GetBitmap(wx.ART_GO_BACK))
        self.Bind(wx.EVT_TOOL, self.on_back, id=id_back)

        id_forward = wx.NewIdRef()
        toolbar.AddSimpleTool(id_forward, "Forward", wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD))
        self.Bind(wx.EVT_TOOL, self.on_forward, id=id_forward)

        id_reload = wx.NewIdRef()
        toolbar.AddSimpleTool(id_reload, "Reload", wx.ArtProvider.GetBitmap(wx.ART_REDO))
        self.Bind(wx.EVT_TOOL, self.on_reload, id=id_reload)

        # Add a text control for the URL
        self.url_ctrl = wx.TextCtrl(toolbar, -1, "https://www.baidu.com",
                                   style=wx.TE_PROCESS_ENTER)
        toolbar.AddControl(self.url_ctrl, "")
        self.Bind(wx.EVT_TEXT_ENTER, self.on_navigate, self.url_ctrl)

        toolbar.Realize()
        self._mgr.AddPane(toolbar, aui.AuiPaneInfo().Name("toolbar").ToolbarPane().
                          Top().Row(1).Position(0))

        # Update the AuiManager
        self._mgr.Update()

    def _init_cef(self):
        # Initialize CEF
        cef.Initialize()

        # Create a browser window
        window_info = cef.WindowInfo()
        window_info.SetAsChild(self.browser_panel.GetHandle(),
                               [0, 0, 400,
                                300])
        self.browser = cef.CreateBrowserSync(window_info, url="https://www.baidu.com")

        # Bind the browser to the panel
        self.browser.SetClientHandler(ClientHandler(self))

        # Show the browser panel
        self._mgr.GetPane("browser_content").Show()


        # Load the initial URL
        self.browser.LoadUrl("https://www.baidu.com")
        self._mgr.Update()

    def on_back(self, event):
        if self.browser.CanGoBack():
            self.browser.GoBack()

    def on_forward(self, event):
        if self.browser.CanGoForward():
            self.browser.GoForward()

    def on_reload(self, event):
        self.browser.Reload()

    def on_navigate(self, event):
        url = self.url_ctrl.GetValue()
        self.browser.LoadUrl(url)
        # self._mgr.Update()

    def OnClose(self, event):
        # Close the browser
        self.browser.CloseBrowser(True)

        # Clean up CEF
        cef.Shutdown()

        # Destroy the frame
        self.Destroy()

class ClientHandler(object):
    def __init__(self, main_frame):
        self.main_frame = main_frame

    def OnLoadEnd(self, browser, frame, httpStatusCode):
        # Update the URL text control
        self.main_frame.url_ctrl.SetValue(browser.GetUrl())

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()