import wx
import re
import sys
import string
import serial
from datetime import datetime
import time
from wx.lib.pubsub import Publisher
from util._validasi import ValidasiInput
from util import dbutil
import MySQLdb

ser = 0

class Saklar(wx.Frame):
    def __init__(self, parent, frame_id):
        wx.Frame.__init__(self, parent, frame_id, "Saklar (Switch)", size=(400,450))
        self.db = dbutil.MySQL('localhost','root','k4g4t4u','lampu')
        panel = wx.Panel(self)
       
        self.list_ctrlone = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.list_ctrlone.InsertColumn(0, "No", width=30)
        self.list_ctrlone.InsertColumn(1, "Id lampu", width=100)
        self.list_ctrlone.InsertColumn(2, "Status lampu", width=100)
        self.list_ctrlone.Show(True)
        self.isilistctrl()

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._is_selected, self.list_ctrlone)
      
        data = self.db.fetch_field("SELECT id_lampu FROM lampu ")


        self.frmLbl = wx.StaticText(panel, -1, "Saklar (Switch)")
        self.frmLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.lbIdLamp= wx.StaticText(panel, -1, "Id Lampu ")
        self.inIdLamp = wx.ComboBox(panel, -1, "", size=(150, 25),choices=data, style=wx.CB_READONLY)
        Radio = ['on','off']
        self.Status = wx.RadioBox(panel, -1, "Status", wx.DefaultPosition, wx.DefaultSize, Radio, 2, wx.RA_SPECIFY_COLS)
        self.inIdLamp.SetInsertionPoint(0)

        self.BtnSimpan = wx.Button(panel, -1, "Simpan")
        self.Bind(wx.EVT_BUTTON, self.save, self.BtnSimpan)
        self.BtnBersih = wx.Button(panel, -1, "Bersih")
        self.Bind(wx.EVT_BUTTON, self.clear, self.BtnBersih)

        self.MainLayer = wx.BoxSizer(wx.VERTICAL)
        self.entrySizer = wx.BoxSizer(wx.VERTICAL)
        self.stextSz = wx.FlexGridSizer(cols = 2, hgap = 5, vgap = 5)
        self.stextSz.AddGrowableCol(1)
        self.btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.radioSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.MainLayer.Fit(self)
        self.MainLayer.SetSizeHints(self)
        panel.SetSizer(self.MainLayer)
        self.aturSizer(panel)



    def aturSizer(self, panel):
        self.MainLayer.Add(self.frmLbl, 0, wx.ALL, 5)
        self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        self.stextSz.Add(self.lbIdLamp, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.stextSz.Add(self.inIdLamp, 0)
        self.radioSizer.Add(self.Status, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
        self.stextSz.Add(self.radioSizer, 0)
        self.entrySizer.Add(self.stextSz, 0, wx.EXPAND|wx.ALL, 10)

        self.btnSizer.Add(self.BtnSimpan,0,wx.ALIGN_CENTER|wx.ALL, 10)
        self.btnSizer.Add(self.BtnBersih,0,wx.ALIGN_CENTER|wx.ALL, 10)

        #Agar ketika di tekan TAB kursor berpindah secara berurutan
        self.listSz = wx.BoxSizer(wx.VERTICAL)

        self.listSz.Add(self.list_ctrlone, 1, wx.EXPAND|wx.ALL, 20)
        #------------------------------------------------------------------------
        self.MainLayer.Add(self.entrySizer)
        self.MainLayer.Add(self.btnSizer)
        self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        self.MainLayer.Add(self.listSz,1, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
        self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)


    def isilistctrl(self):
        self.list_ctrlone.DeleteAllItems()
        hasil = self.db.fetch_all("Select id_lampu,status FROM lampu")
        for enum, isi in enumerate(hasil):
            enum += 1
            prim = self.list_ctrlone.InsertStringItem(sys.maxint, str(enum))
            self.list_ctrlone.SetStringItem(prim, 1, str(isi[0]))
            self.list_ctrlone.SetStringItem(prim, 2, str(isi[1]))

    def save(self, event):
		idlampu = self.inIdLamp.GetValue()
		status = self.Status.GetStringSelection()
		nilaiEntry = [idlampu, status]
		val = Validasi(nilaiEntry)
		if val.FormKosong() == 1:
			pass
		else :
			tanya = wx.MessageDialog(None, "Yakin akan menyimpan?", "Konfirmasi", wx.YES_NO|wx.ICON_QUESTION)
			retCode = tanya.ShowModal()
			if (retCode == wx.ID_YES):
				if status == self._cek_status(idlampu):
					wx.MessageDialog(self, 'Lampu dalam keadaan sama','Informasi',wx.ICON_INFORMATION).ShowModal()
					self.clear(None)
				else:
					pin = self.db.fetch_one("SELECT pin from lampu WHERE id_lampu='%s'" % (idlampu))
					try:
						ser.write(str(pin[0]))
						sql = ("UPDATE lampu SET status='%s' WHERE id_lampu='%s'") % (status,idlampu)
						self.db.update_db(sql)
						self._isi_log(status,idlampu)
						wx.MessageDialog(self, 'Berhasil diubah','Informasi',wx.ICON_INFORMATION).ShowModal()
						self.clear(None)
						self.isilistctrl()
					except:
						wx.MessageDialog(self, 'Gagal mengubah status ', 'Informasi', wx.ICON_INFORMATION).ShowModal()
			else:
				pass
			tanya.Destroy()
        
    def _cek_status(self,idlampu):
        status = self.db.fetch_one("SELECT status From lampu WHERE id_lampu='%s'" %(idlampu))
        return status[0]
    
    def _isi_log(self,switch,idlampu):
        asal = 'saklar'
        tanggal = datetime.now().strftime('%Y-%m-%d')
        waktu = time.strftime('%H:%M:%S')
        self.db.commit_db("INSERT INTO log VALUES('%s','%s','%s','%s','%s')" % (tanggal,waktu,idlampu,switch,asal))

    def _is_selected(self, event):
        idlampu = self.list_ctrlone.GetItem(event.GetIndex(), 1).GetText()
        data = self.db.fetch_one("Select id_lampu,status From lampu WHERE id_lampu='%s'" % idlampu)
        a = [str (x) for x in data]
        for x in a:
            self.inIdLamp.SetValue(a[0])
            self.Status.SetStringSelection(a[1])
        self.inIdLamp.Enable(False)

    def clear(self, event):
        self.inIdLamp.SetValue("")
        self.inIdLamp.Clear
        self.Status.SetStringSelection("on")
        self.inIdLamp.Enable(True)


class Validasi():
	def __init__(self, nilaiEntry):
		self.idlampu = nilaiEntry[0]
		self.status = nilaiEntry[1]
		
	def FormKosong(self):
		if ((not self.idlampu)|(not self.status)):
			alert = wx.MessageDialog(None, "Form belum lengkap", "Error", wx.ID_OK)
			alert.ShowModal()
			alert.Destroy()
			return 1
		else:
			return 0


