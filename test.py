import wx

class MyDialog(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.flag_timer_run = False

        # Event handler for timer event
        def onTimer(event):
            if not self.flag_timer_run:
                # Perform actions here only once
                print("Timer event triggered!")

                # Stop the timer
                self.timer.Stop()

                self.flag_timer_run = True

        # Create the timer
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.timer.Bind(wx.EVT_TIMER, onTimer)

    def startTimer(self):
        if not self.flag_timer_run:
            self.timer.Start(1000)  # Start timer with 1 second interval

# Create the dialog
app = wx.App()
dialog = MyDialog(None)
dialog.ShowModal()
app.MainLoop()