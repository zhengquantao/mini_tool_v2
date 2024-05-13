import wx


class ImageViewer(wx.Frame):
    def __init__(self, parent, title):
        super(ImageViewer, self).__init__(parent, title=title, size=(600, 450))
        self.InitUI()
        self.Show()

    def InitUI(self):
        panel = wx.Panel(self)
        self.image = wx.Image(r'C:\Users\EDY\Desktop\30057\wind_speed_tsr_19#.png', wx.BITMAP_TYPE_ANY)
        self.bitmap = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(self.image))

        # 放大按钮
        self.button_zoom_in = wx.Button(panel, label='Zoom In')
        self.button_zoom_in.Bind(wx.EVT_BUTTON, self.OnZoomIn)

        # 缩小按钮
        self.button_zoom_out = wx.Button(panel, label='Zoom Out')
        self.button_zoom_out.Bind(wx.EVT_BUTTON, self.OnZoomOut)

        # 布局
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bitmap, 1, wx.EXPAND)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.button_zoom_in)
        button_sizer.Add(self.button_zoom_out)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        panel.SetSizer(sizer)

    def OnZoomIn(self, event):
        self.image.Rescale(int(self.image.GetWidth() * 0.2) + self.image.GetWidth(), int(self.image.GetWidth() * 0.2) + self.image.GetHeight())
        self.Refresh()

    def OnZoomOut(self, event):
        self.image.Rescale(self.image.GetWidth() * 0.8, self.image.GetHeight() * 0.8)
        self.Refresh()


if __name__ == '__main__':
    app = wx.App(False)
    frame = ImageViewer(None, 'Image Viewer')
    app.MainLoop()