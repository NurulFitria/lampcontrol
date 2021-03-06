import wx
import re
import sys
import string
from wx.lib.pubsub import Publisher
from util._validasi import ValidasiInput
from util import dbutil
import MySQLdb

class Lamp(wx.Frame):
	def __init__(self, parent, frame_id):
		wx.Frame.__init__(self, parent, frame_id, "Lampu (Lamp)", size=(500,500))
		self.db = dbutil.MySQL('localhost', 'root', 'k4g4t4u', 'lampu')
		panel = wx.Panel(self)
		
		self.list_ctrlone = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.list_ctrlone.InsertColumn(0, "No", width=30)
		self.list_ctrlone.InsertColumn(1, "Id", width=100)
		self.list_ctrlone.InsertColumn(2, "Nama Ruangan", width=150)
		self.list_ctrlone.InsertColumn(3, "Pin", width=100)
		self.list_ctrlone.InsertColumn(4, "Status", width=100)
		self.list_ctrlone.Show(True)
		self.isilistctrl()
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._is_selected, self.list_ctrlone)
		#insert items for inPin
		data = ['1', '2', '3', '4']

		self.frmLbl = wx.StaticText(panel, -1, "Lamp (Lampu)")
		self.frmLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.lbIdLamp= wx.StaticText(panel, -1, "Id Lampu ")
		self.inIdLamp = wx.TextCtrl(panel, -1, size=(90, 25),validator = ValidasiInput("angka_saja"))
		self.lbNmLamp = wx.StaticText(panel, -1, "Nama Ruangan ")
		self.inNmLamp = wx.TextCtrl(panel, -1, size=(150, 25))
		self.lbPin = wx.StaticText(panel, -1, "Pin ")
		self.inPin = wx.ComboBox(panel, -1, "", size=(150, 25),choices=data, style=wx.CB_READONLY)
		self.inIdLamp.SetInsertionPoint(0)
		self.AutoIncrementIdLamp()

		#---button
		self.BtnSave = wx.Button(panel, -1, "Simpan")
		self.Bind(wx.EVT_BUTTON, self.save, self.BtnSave)
		self.BtnClear = wx.Button(panel, -1, "Bersih")
		self.Bind(wx.EVT_BUTTON, self.clear, self.BtnClear)
				
		self.MainLayer = wx.BoxSizer(wx.VERTICAL)
		self.entrySizer = wx.BoxSizer(wx.VERTICAL)
		self.stextSz = wx.FlexGridSizer(cols = 2, hgap = 5, vgap = 5)
		self.stextSz.AddGrowableCol(1)
		self.btnSizer= wx.BoxSizer(wx.HORIZONTAL)
		self.radioSizer= wx.BoxSizer(wx.HORIZONTAL)
		
		self.MainLayer.Fit(self)
		self.MainLayer.SetSizeHints(self)
		panel.SetSizer(self.MainLayer)
		
		self.aturSizer(panel)

	def aturSizer(self, panel):
		self.MainLayer.Add(self.frmLbl, 0, wx.ALL, 5)
		self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
		self.stextSz.Add(self.lbIdLamp, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.stextSz.Add(self.inIdLamp, 0)
		self.stextSz.Add(self.lbNmLamp, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.stextSz.Add(self.inNmLamp, 0)
		self.stextSz.Add(self.lbPin, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.stextSz.Add(self.inPin, 0)
		self.entrySizer.Add(self.stextSz, 0, wx.EXPAND|wx.ALL, 10)
		
		self.btnSizer.Add(self.BtnSave,0,wx.ALIGN_CENTER|wx.ALL, 10)
		self.btnSizer.Add(self.BtnClear,0,wx.ALIGN_CENTER|wx.ALL, 10)
		
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
		hasil = self.db.fetch_all("Select * FROM lampu order by id_lampu asc")
		str_hasil = str(hasil)
		kosong = '()'
		for enum, isi in enumerate(hasil):
			enum += 1
			prim = self.list_ctrlone.InsertStringItem(sys.maxint, str(enum))
			self.list_ctrlone.SetStringItem(prim, 1, str(isi[0]))
			self.list_ctrlone.SetStringItem(prim, 2, str(isi[1]))
			self.list_ctrlone.SetStringItem(prim, 3, str(isi[2]))
			self.list_ctrlone.SetStringItem(prim, 4, str(isi[3]))

	def AutoIncrementIdLamp(self):
		hasil = self.db.fetch_one("Select max(id_lampu) from lampu")
		if hasil[0] == None :
			self.inIdLamp.SetValue('1')
			self.inIdLamp.Enable(False)
		else :
			b = int(hasil[0]) + 1
			self.inIdLamp.SetValue(str(b))
			self.inIdLamp.Enable(False)

	def save(self, event):
		idlampu = self.inIdLamp.GetValue()
		nmlampu = self.inNmLamp.GetValue()
		pin = self.inPin.GetValue()
		status = 'off'
		nilaiEntry = [idlampu, nmlampu, pin, status]
		val = Validasi(nilaiEntry)
		if val.FormKosong() == 1:
			pass
		else :
			tanya = wx.MessageDialog(None, "Yakin akan menyimpan?", "Konfirmasi",
				 wx.YES_NO|wx.ICON_QUESTION)
			retCode = tanya.ShowModal()
			if (retCode == wx.ID_YES):
				lamps = self.db.fetch_field("SELECT id_lampu From lampu")
				if (nilaiEntry[0]) in lamps:
					alert = wx.MessageDialog(None,"ID Lampu sudah digunakan, apakah akan diubah?","Peringatan",wx.YES_NO|wx.ICON_QUESTION)
					ret = alert.ShowModal()
					if (ret == wx.ID_YES):
						sql=("UPDATE lampu SET nama_lampu='%s',pin='%s' WHERE id_lampu='%s'") % (nmlampu,pin,idlampu)
						self.db.update_db(sql)
						wx.MessageDialog(self, 'Berhasil diubah', 'Informasi', wx.ICON_INFORMATION).ShowModal()
						self.clear(None)
						self.isilistctrl()
					else:
						pass
						alert.Destroy()						
				else:
					if self.CekPin() == 1:
						pass
					else:
						self.db.commit_db("INSERT INTO lampu VALUES ('%s', '%s', '%s','%s')" % \
							(idlampu, nmlampu, int(pin),status))
						wx.MessageDialog(self, 'Berhasil disimpan!', 'Informasi',
							wx.ICON_INFORMATION).ShowModal()
						self.clear(None)
						self.isilistctrl()
							
			else:
				pass
			tanya.Destroy()
		
	def _is_selected(self, event):
		id_lampu = self.list_ctrlone.GetItem(event.GetIndex(), 1).GetText()
		data = self.db.fetch_one("SELECT * FROM lampu WHERE id_lampu='%s'" % id_lampu)
	
		a = [str(x) for x in data]
		
		for x in a:
			self.inIdLamp.SetValue(a[0])
			self.inNmLamp.SetValue(a[1])
			self.inPin.SetValue(a[2])
			
		self.inIdLamp.Enable(False)
		self.inPin.Enable(False)
		
		
	def CekPin(self):
		idlampu = self.inIdLamp.GetValue()
		nmlampu = self.inNmLamp.GetValue()
		pin = self.inPin.GetValue()
		nilaiEntry = [idlampu,nmlampu,pin]
		pins = self.db.fetch_field("SELECT pin FROM lampu")
		if int(nilaiEntry[2]) in pins:
			alert = wx.MessageDialog(None, "Pin sudah digunakan", "Error", wx.ID_OK)
			alert.ShowModal()
			alert.Destroy()
			return 1
		else:
			return 0
							
	def clear(self, event):
		self.inIdLamp.Clear()
		self.inNmLamp.Clear()
		self.inPin.SetValue("")
		self.inIdLamp.Enable(True)
		self.inPin.Enable(True)
        	self.inIdLamp.Enable(True)
		self.AutoIncrementIdLamp()

class Validasi():
	def __init__(self, nilaiEntry):
		self.idlampu = nilaiEntry[0]
		self.nmlampu = nilaiEntry[1]
		self.pin = nilaiEntry[2]
		
	def FormKosong(self):
		if ((not self.idlampu)|(not self.nmlampu) |(not self.pin)):
			alert = wx.MessageDialog(None, "Form belum lengkap", "Error", wx.ID_OK)
			alert.ShowModal()
			alert.Destroy()
			return 1
		else:
			return 0
	
