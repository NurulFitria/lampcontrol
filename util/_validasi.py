import wx
import string
import wx.lib.pubsub

class ValidasiInput(wx.PyValidator):
    def __init__(self, flag):
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return ValidasiInput(self.flag)

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def OnChar(self, evt):
		key = evt.GetKeyCode()
		koma = '.'
		kombinasi_1 = string.digits + koma
		kombinasi_2 = string.letters + '-' + koma
		if key == 9 or key == 8 or key == 32 or key == wx.WXK_DELETE or key > 256 or key == 1:
			evt.Skip()
			return
			
		if self.flag == "huruf_saja" and chr(key) in kombinasi_2:
			evt.Skip()
			return
		if self.flag == "angka_saja" and chr(key) in kombinasi_1:
			evt.Skip()
			return
