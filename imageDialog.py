import wx
import wx.lib.dialogs
 
########################################################################
class MyForm(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "ScrolledMessageDialog Tutorial")
        panel = wx.Panel(self, wx.ID_ANY)
        b = wx.Button(panel, label="Create and Show a ScrolledMessageDialog")
        b.Bind(wx.EVT_BUTTON, self.onButton)
 
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(b, 0, wx.ALL|wx.CENTER, 5)
        panel.SetSizer(sizer)
 
    #----------------------------------------------------------------------
    def onButton(self, event):
        """
        Based on the wxPython demo by the same name
        """
        f = open("imageDialog.py", "r")
        msg = f.read()
        f.close()
 
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg, "message test")
        dlg.ShowModal()
 
        dlg.Destroy()
 
#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()
