import wx
import re
import sys
import string
from wx.lib.pubsub import Publisher
from util import dbutil
import MySQLdb
import settings as st
import tweepy
CK = "GJOnLjmLfAGrg5qgO7Cqg"
CS = "3gNrz7B4pxQjSIbY81xUC61O9biIhYx15XJwzDpHbw"
AT = "719356627-TLd9WqTD0SmGhkgRg9NSXt79oGnj7zSXgLcXS3Fk"
ATS = "2LyqArOBeVpVYKHjjNtEhWYxBOwJwj77VENaR8N7Ls0"
 
# Initialize the tweepy API
auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, ATS)
api = tweepy.API(auth)

class Twitter(wx.Frame):
   
    def __init__(self, parent, frame_id):
        wx.Frame.__init__(self, parent, frame_id, "Twitter", size=(550,500))
        self.db = dbutil.MySQL("localhost","root","k4g4t4u","lampu")
        panel = wx.Panel(self)
        #insert pengguna
        self._getFriends()      
        
        self.list_ctrlone = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.list_ctrlone.InsertColumn(0, "No", width=30)
        self.list_ctrlone.InsertColumn(1, "Pengguna", width=200)
        self.list_ctrlone.Show(True)
        self.isilistctrl()
        
        
        self.list_ctrltwo = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.list_ctrltwo.InsertColumn(0, "No", width=30)
        self.list_ctrltwo.InsertColumn(1, "Pengguna", width=200)
        self.list_ctrltwo.InsertColumn(2, "Control Lampu", width=250)
        self.list_ctrltwo.Show(True)
        self.isilistHak_akses()
                
        #-------isi combo id jadwal from database
        data = self.db.fetch_field("SELECT id_lampu FROM lampu ")
        #-------create event for item list
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._is_selected, self.list_ctrlone)
                
        self.lbHak= wx.StaticText(panel, -1, " Hak Akses")
        self.lbHak.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.lbID= wx.StaticText(panel, -1, "ID ")
        self.inID = wx.TextCtrl(panel, -1, size=(120, 30))
        self.lbUser = wx.StaticText(panel, -1, "User ")
        self.inUser = wx.TextCtrl(panel, -1, size=(120, 30))
        self.lbLampu = wx.StaticText(panel, -1, "Lampu ")
        self.inLampu = wx.ComboBox(panel, -1, "", size=(150, 30),choices=data, style=wx.CB_READONLY)  
        
        
        self.BtnSave = wx.Button(panel, -1, "Save")        
        self.Bind(wx.EVT_BUTTON, self.Save, self.BtnSave)
        self.BtnClear = wx.Button(panel, -1, "Clear")        
        self.Bind(wx.EVT_BUTTON, self.clear, self.BtnClear)
        
        #mengumpulkan semua textctrl
        self._all_textCtrl = [self.inID, self.inUser, self.inLampu]
        
        self.MainLayer = wx.BoxSizer(wx.VERTICAL)
        self.MainLayer.Fit(self)
        self.MainLayer.SetSizeHints(self)
        panel.SetSizer(self.MainLayer)
    
        self.aturSizer(panel)

    def aturSizer(self, panel):
        self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        #Agar ketika di tekan TAB kursor berpindah secara berurutan
        self.listSz = wx.BoxSizer(wx.HORIZONTAL)
        self.frmTwt = wx.FlexGridSizer(cols = 2, hgap = 5, vgap = 5)
        self.frmTwt.Add(self.lbID, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.frmTwt.Add(self.inID, 0)
        self.frmTwt.Add(self.lbUser, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.frmTwt.Add(self.inUser, 0)
        self.frmTwt.Add(self.lbLampu, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.frmTwt.Add(self.inLampu, 0)
        self.frmTwt.Add(self.BtnSave, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.frmTwt.Add(self.BtnClear, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.listSz.Add(self.list_ctrlone, 1, wx.EXPAND|wx.ALL, 20)
        self.listSz.Add(self.frmTwt, 1, wx.EXPAND|wx.ALL, 20)
        #------------------------------------------
        self.listtwo = wx.BoxSizer(wx.HORIZONTAL)
        self.listtwo.Add(self.list_ctrltwo, 1, wx.EXPAND|wx.ALL, 20)
        #------------------------------------------------------------------------
        self.MainLayer.Add(self.lbHak, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        self.MainLayer.Add(self.listSz,1,  wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        self.MainLayer.Add(self.listtwo,1,  wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
                
    def _getFriends(self):
        for friend in tweepy.Cursor(api.friends).items(100):
            user = friend.screen_name
            id = friend.id
            nilaiEntry = [user,id]
            user = self.db.fetch_field("SELECT username From pengguna")
            if nilaiEntry[0] in user:
                pass
            else:
                self.db.commit_db("INSERT INTO pengguna VALUES ('%s', '%s')" % (id,user))
            
    def isilistctrl(self):
      self.list_ctrlone.DeleteAllItems()        
      hasil = self.db.fetch_all("Select username FROM pengguna")
      str_hasil = str(hasil)
      kosong = '()'
      for enum, isi in enumerate(hasil):
            enum += 1
            prim = self.list_ctrlone.InsertStringItem(sys.maxint, str(enum))
            self.list_ctrlone.SetStringItem(prim, 1, str(isi[0]))
            
    def isilistHak_akses(self):
      self.list_ctrltwo.DeleteAllItems()        
      hasil = self.db.fetch_all("Select ket,id_lampu FROM hak_akses order by ket asc")
      str_hasil = str(hasil)
      kosong = '()'
      for enum, isi in enumerate(hasil):
            enum += 1
            prim = self.list_ctrltwo.InsertStringItem(sys.maxint, str(enum))
            self.list_ctrltwo.SetStringItem(prim, 1, str(isi[0]))
            self.list_ctrltwo.SetStringItem(prim, 2, str(isi[1]))
            
    def _is_selected(self, event):
        user = self.list_ctrlone.GetItem(event.GetIndex(), 1).GetText()
        data = self.db.fetch_one("SELECT * FROM pengguna WHERE username='%s'" % user)
        a = [str(x) for x in data]
        for x in a:
            self.inID.SetValue(a[0])
            self.inUser.SetValue(a[1])
        
        self.inID.Enable(False)
        self.inUser.Enable(False)
        self.inLampu.SetFocus()
         
    def Save(self, event):
        id = self.inID.GetValue()
        user = self.inUser.GetValue()
        lampu = self.inLampu.GetValue()
        try:
            self.db.commit_db("INSERT INTO hak_akses VALUES ('%s', '%s', '%s')" % \
                        (id,lampu,user))
            wx.MessageDialog(self, 'Berhasil disimpan!', 'Berhasil',
                    wx.ICON_INFORMATION).ShowModal()
            
        except MySQL.OperationalError:
            wx.MessageDialog(self, 'Gagal disimpan!', 'Error', 
                    wx.ICON_ERROR).ShowModal()
        self.clear(None)
        self.isilistHak_akses()
                    
    def clear(self, event):
       self.inID.Clear()
       self.inUser.Clear()
       self.inLampu.SetValue("")
       self.inID.Enable(True)
       self.inUser.Enable(True)
       self.inID.SetFocus()

        
       
