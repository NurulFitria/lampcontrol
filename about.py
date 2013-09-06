import wx
from util import settings as st

class About(wx.Frame):
    def __init__(self, parent, frame_id):
        wx.Frame.__init__(self,  parent, frame_id, "About Program", size=(400,200))
        tentang = """Program ini dibuat untuk mempermudah pengaturan aktivitas lampu sesuai dengan jadwal yang ada \n dan dapat dikendalikan secara jarak jauh melalui Twitter"""
        lisensi = """Program ini adalah free software, anda bisa merubahnya dan atau hasil perubahannya itu disebarluaskan \ndibawah ketentuan GNU General Public License yang dikeluarkan oleh Free Software Foundation;"""    

        dialoginfo = wx.AboutDialogInfo()
        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon(st._tentang, wx.BITMAP_TYPE_PNG))
        info.SetName('Sistem Penjadwalan dan Kendali Lampu Jarak Jauh ')
        info.SetVersion('0.1-Beta')
        info.SetDescription(tentang)
        info.SetCopyright('(Copy Left) 2012')
        info.SetWebSite('http://penguintengil.web.id')
        info.SetLicence(lisensi)
        info.AddDeveloper('Developer : Nurul Fitria')
        
        wx.AboutBox(info)

