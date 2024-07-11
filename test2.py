
import wx
from aui2 import svg_to_bitmap
from pyecharts.commons.utils import JsCode


class MyPanel(wx.Panel):
    line_svg = """<svg t="1715419373073" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="17728" width="48" height="48"><path d="M888 792H200V168c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v688c0 4.4 3.6 8 8 8h752c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8z" p-id="17729"></path><path d="M305.8 637.7c3.1 3.1 8.1 3.1 11.3 0l138.3-137.6L583 628.5c3.1 3.1 8.2 3.1 11.3 0l275.4-275.3c3.1-3.1 3.1-8.2 0-11.3l-39.6-39.6c-3.1-3.1-8.2-3.1-11.3 0l-230 229.9L461.4 404c-3.1-3.1-8.2-3.1-11.3 0L266.3 586.7c-3.1 3.1-3.1 8.2 0 11.3l39.5 39.7z" p-id="17730"></path></svg>"""
    bar_svg = """<svg t="1715419423730" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="18824" width="48" height="48"><path d="M888 792H200V168c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v688c0 4.4 3.6 8 8 8h752c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8z" p-id="18825"></path><path d="M288 712h56c4.4 0 8-3.6 8-8V560c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v144c0 4.4 3.6 8 8 8zM440 712h56c4.4 0 8-3.6 8-8V384c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v320c0 4.4 3.6 8 8 8zM592 712h56c4.4 0 8-3.6 8-8V462c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v242c0 4.4 3.6 8 8 8zM744 712h56c4.4 0 8-3.6 8-8V304c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v400c0 4.4 3.6 8 8 8z" p-id="18826"></path></svg>"""
    scatter_svg = """<svg t="1715419775288" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="23239" width="8" height="8"><path d="M631.467 652.8c0 81.067 68.266 149.333 149.333 149.333S930.133 733.867 930.133 652.8 861.867 503.467 780.8 503.467 631.467 571.733 631.467 652.8z" fill="#1890FF" p-id="23240"></path><path d="M196.267 413.867c0 38.4 34.133 72.533 72.533 72.533s72.533-34.133 72.533-72.533-34.133-72.534-72.533-72.534-72.533 29.867-72.533 72.534z" fill="#13C2C2" p-id="23241"></path><path d="M405.333 256c0 21.333 17.067 38.4 38.4 38.4s38.4-17.067 38.4-38.4-17.066-38.4-38.4-38.4-38.4 17.067-38.4 38.4zM332.8 614.4c0 21.333 17.067 38.4 38.4 38.4s38.4-17.067 38.4-38.4-17.067-38.4-38.4-38.4c-25.6 4.267-38.4 21.333-38.4 38.4z" fill="#FACC14" p-id="23242"></path><path d="M622.933 337.067c0 29.866 25.6 51.2 51.2 51.2 29.867 0 51.2-25.6 51.2-51.2s-25.6-51.2-51.2-51.2c-29.866-4.267-51.2 21.333-51.2 51.2z" fill="#13C2C2" p-id="23243"></path><path d="M529.067 512c0 29.867 25.6 55.467 55.466 55.467C614.4 567.467 640 541.867 640 512s-25.6-55.467-55.467-55.467c-29.866 0-55.466 25.6-55.466 55.467z" fill="#FACC14" p-id="23244"></path><path d="M145.067 891.733c0 4.267 0 4.267-4.267 8.534 0 4.266-4.267 4.266-8.533 4.266H98.133c-4.266 0-4.266 0-8.533-4.266s-4.267-8.534-4.267-8.534v-793.6c0-4.266 0-4.266 4.267-8.533 0-4.267 4.267-4.267 8.533-4.267h34.134c4.266 0 4.266 0 8.533 4.267s4.267 8.533 4.267 8.533v793.6z" fill="#546E7A" p-id="23245"></path><path d="M98.133 925.867c-4.266 0-4.266 0-8.533-4.267s-4.267-4.267-4.267-8.533v-38.4c0-4.267 0-4.267 4.267-8.534 4.267 0 4.267-4.266 8.533-4.266h827.734c4.266 0 4.266 0 8.533 4.266 4.267 0 4.267 4.267 4.267 8.534V908.8c0 4.267 0 4.267-4.267 8.533s-8.533 4.267-8.533 4.267H98.133z" fill="#546E7A" p-id="23246"></path></svg>"""

    def __init__(self, parent, data=None):
        wx.Panel.__init__(self, parent, -1)

        self.tmp_chart = None

        fgs = wx.FlexGridSizer(1, 2, 0, 1)
        panel1 = wx.Panel(self, size=(0, wx.EXPAND), style=wx.BORDER)
        wx.StaticText(panel1, pos=(5, 0), label='数据')
        self.listbox = wx.ListBox(panel1, -1, pos=(0, 20), size=(110, wx.EXPAND), choices=["1", "2", "3", "4", "5"],
                                  style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.SUNKEN_BORDER)
        # self.listbox.SetBackgroundColour("#eeeeee")
        # panel1.SetBackgroundColour("yellow")

        panel2 = wx.Panel(self, size=(0, wx.EXPAND), style=wx.BORDER)
        wx.StaticText(panel2, pos=(5, 0), label='图表')
        panel3 = wx.Panel(panel2, pos=(0, 20), size=(wx.EXPAND, 149), style=wx.CURSOR_NO_ENTRY)
        # wx.BitmapButton(panel3, wx.NewIdRef(), svg_to_bitmap(self.line_svg), pos=(0, 0),  size=(50, 50))
        # wx.BitmapButton(panel3, wx.NewIdRef(), svg_to_bitmap(self.bar_svg), pos=(0, 51), size=(50, 50))
        # wx.BitmapButton(panel3, wx.NewIdRef(), svg_to_bitmap(self.scatter_svg), pos=(51, 0), size=(50, 50))
        # wx.BitmapButton(panel3, wx.NewIdRef(), svg_to_bitmap(self.line_svg), pos=(51, 51), size=(50, 50))
        # wx.BitmapButton(panel3, wx.NewIdRef(), svg_to_bitmap(self.bar_svg), pos=(102, 0), size=(50, 50))
        # self.bbtn = wx.BitmapButton(panel3, wx.NewIdRef(), svg_to_bitmap(self.scatter_svg), pos=(102, 51), size=(50, 50))
        # self.bbtn.SetBackgroundColour("#B3E5FC")
        # self.bbtn.Disable()
        # self.bbtn.SetOwnBackgroundColour("")
        # self.bbtn.Enable()
        # panel3.SetBackgroundColour("white")
        self.build_bitmap_button(panel3)

        panel4 = wx.Panel(panel2, pos=(0, 150), size=(wx.EXPAND, wx.EXPAND), style=wx.BORDER)
        wx.StaticText(panel4, pos=(5, 3), label='X轴：')
        self.tc1 = wx.ComboBox(panel4, wx.ID_ANY, wx.EmptyString, pos=(5, 25), size=(150, 30),
                               choices=["1", "2", "3", "4", "5"])
        self.tc1.AutoComplete([])
        wx.StaticText(panel4, pos=(5, 55), label='Y轴：')
        self.tc2 = wx.CheckListBox(panel4, pos=(5, 75), size=(150, 145), choices=["1", "2", "3", "4", "5"],
                                   style=wx.TC_MULTILINE)
        btn = wx.Button(panel4, -1, '浏览', pos=(75, 225))
        btn.Bind(wx.EVT_BUTTON, self.on_click)
        panel4.SetBackgroundColour("white")

        fgs.Add(panel1, 0, wx.EXPAND)
        fgs.Add(panel2, 0, wx.EXPAND)
        fgs.AddGrowableCol(0, 1)
        fgs.AddGrowableCol(1, 2)
        self.SetSizer(fgs)

    def build_bitmap_button(self, panel3):
        self.bp_btn_dict = {
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(self.bar_svg), pos=(2, 2), size=(49, 49), name='Line'): "Line",
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(self.bar_svg), pos=(2, 52), size=(49, 49), name='Bar'): "Bar",
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(self.bar_svg), pos=(53, 2), size=(49, 49), name='Scatter'): "Scatter",
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(self.bar_svg), pos=(53, 52), size=(49, 49), name='BarStack'): "BarStack",
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(self.bar_svg), pos=(104, 2), size=(49, 49), name='BarReversal'): "BarReversal",
            wx.BitmapButton(panel3, wx.ID_ANY, svg_to_bitmap(self.bar_svg), pos=(104, 52), size=(49, 49), name='LineGap'): "LineGap",
        }
        for btn in self.bp_btn_dict.keys():
            panel3.Bind(wx.EVT_BUTTON, self.on_dpclick, btn)

    def on_dpclick(self, event):
        btn_obj = event.GetEventObject()

        self.tmp_chart = self.bp_btn_dict[btn_obj]
        for btn in self.bp_btn_dict.keys():
            btn.SetBackgroundColour("")

        btn_obj.SetBackgroundColour("#BBDEFB")
        return

    def on_click(self, event):
        print("-----------", self.tc1.GetValue(), self.tc2.GetValue())

        # self.tc1.SetItems(self.data_df.columns)
        # self.tc1.AutoComplete(self.data_df.columns)
        # self.tc2.SetItems(self.data_df.columns)


class MyApp(wx.App):
    def OnInit(self):

        frame = wx.Frame(None, -1, title="测试", size=(270, 800))
        MyPanel(frame)
        self.SetTopWindow(frame)
        frame.Show(True)

        return True


def main():
    app = MyApp(False)
    app.MainLoop()


if __name__ == "__main__":
    # main()
    filehistory = wx.FileHistory(1)
    config = wx.Config("能效评估助手", style=wx.CONFIG_USE_LOCAL_FILE)
    filehistory.Load(config)
    print(filehistory.GetCount())
    for i in range(1):
        filehistory.RemoveFileFromHistory(0)
    filehistory.Save(config)
    config.Flush()

