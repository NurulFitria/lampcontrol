import wx
import re
import sys
import string
from wx.lib.pubsub import Publisher
from util._validasi import ValidasiInput
import wx.lib.masked as masked
from util import dbutil

class Jadwal(wx.Dialog):
	def __init__(self, parent, frame_id):
		wx.Dialog.__init__(self, parent, frame_id, "Jadwal (Schedule)", size=(500,500))
		self.db = dbutil.MySQL('localhost', 'root', 'k4g4t4u', 'lampu')
		panel = wx.Panel(self)
		
		self.list_ctrlone = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.list_ctrlone.InsertColumn(0, "No", width=30)
		self.list_ctrlone.InsertColumn(1, "Id Jadwal", width=100)
		self.list_ctrlone.InsertColumn(2, "Hari", width=100)
		self.list_ctrlone.InsertColumn(3, "Mulai", width=100)
		self.list_ctrlone.InsertColumn(4, "Selesai", width=100)
		self.list_ctrlone.Show(True)
		self.isilistctrl()
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._is_selected, self.list_ctrlone)
		hari = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu']
		
		self.frmLbl = wx.StaticText(panel, -1, "Jadwal (Schedule)")
		self.frmLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
		
		self.lbIdJadwal= wx.StaticText(panel, -1, "Id_Jadwal ")
		self.inIdJadwal = wx.TextCtrl(panel, -1, size=(90, 25),validator = ValidasiInput("angka_saja"))
		self.lbNmJadwal = wx.StaticText(panel, -1, "Hari ")
		self.inNmJadwal = wx.ComboBox(panel, -1, "", size=(150, 25),choices=hari, style=wx.CB_READONLY)
		
		self.lbMulai = wx.StaticText(panel, -1, "Mulai ")
		self.spin1 = wx.SpinButton( panel, -1)
		self.inMulai = masked.TimeCtrl(panel, -1, name="24 hour control", fmt24hr=True,	spinButton = self.spin1)
		
		self.lbSelesai = wx.StaticText(panel, -1, "Selesai ")
		self.spin2 = wx.SpinButton(panel, -1)
		self.inSelesai = masked.TimeCtrl(panel, -1, name="24 hour control", fmt24hr=True,spinButton = self.spin2)
		
		self.inIdJadwal.SetInsertionPoint(0)
		self.AutoIncrementIdJadwal()
		#---button
		self.BtnSave = wx.Button(panel, -1, "Simpan")        
		self.Bind(wx.EVT_BUTTON, self.save, self.BtnSave)
		self.BtnClear = wx.Button(panel, -1, "Bersih")        
		self.Bind(wx.EVT_BUTTON, self.clear, self.BtnClear)
		
		#mengumpulkan semua textctrl
		self._all_textCtrl = [self.inIdJadwal, self.inNmJadwal, self.inMulai, self.inSelesai]
		
		self.MainLayer = wx.BoxSizer(wx.VERTICAL)
		self.entrySizer = wx.BoxSizer(wx.VERTICAL)
		self.stextSz = wx.FlexGridSizer(cols = 2, hgap = 5, vgap = 5)
		self.stextSz.AddGrowableCol(1)
		self.btnSizer= wx.BoxSizer(wx.HORIZONTAL)
		self.mulai= wx.BoxSizer(wx.HORIZONTAL)
		self.selesai= wx.BoxSizer(wx.HORIZONTAL)
		
		self.MainLayer.Fit(self)
		self.MainLayer.SetSizeHints(self)
		panel.SetSizer(self.MainLayer)
		
		self.aturSizer(panel)
			

	def aturSizer(self, panel):
		self.MainLayer.Add(self.frmLbl, 0, wx.ALL, 5)
		self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
		self.stextSz.Add(self.lbIdJadwal, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.stextSz.Add(self.inIdJadwal, 0)
		self.stextSz.Add(self.lbNmJadwal, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.stextSz.Add(self.inNmJadwal, 0)
		self.stextSz.Add(self.lbMulai, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.mulai.Add(self.inMulai, 0)
		self.mulai.Add(self.spin1, 0)
		self.stextSz.Add(self.mulai)
		self.stextSz.Add(self.lbSelesai, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.selesai.Add(self.inSelesai, 0)
		self.selesai.Add(self.spin2, 0)
		self.stextSz.Add(self.selesai)
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
		hasil = self.db.fetch_all("Select id_jadwal,hari,mulai,selesai FROM jadwal order by id_jadwal asc")
		str_hasil = str(hasil)
		kosong = '()'
		for enum, isi in enumerate(hasil):
			enum += 1
			prim = self.list_ctrlone.InsertStringItem(sys.maxint, str(enum))
			self.list_ctrlone.SetStringItem(prim, 1, str(isi[0]))
			self.list_ctrlone.SetStringItem(prim, 2, str(isi[1]))
			self.list_ctrlone.SetStringItem(prim, 3, str(isi[2]))
			self.list_ctrlone.SetStringItem(prim, 4, str(isi[3]))

	def AutoIncrementIdJadwal(self):
		hasil = self.db.fetch_one("Select max(id_jadwal) from jadwal")
		if hasil[0] == None :
			self.inIdJadwal.SetValue('001')
		else :
			a = int(hasil[0])
			a = a+1
			if a >=10 and a<=99:
				self.inIdJadwal.SetValue('0'+str(a))
			elif a<10 :
				self.inIdJadwal.SetValue('00'+str(a))
			else:
				self.inIdJadwal.SetValue(str(a))
		self.inIdJadwal.Enable(False)
			
				
				
			
	def _is_selected(self, event):
		id_jadwal = self.list_ctrlone.GetItem(event.GetIndex(), 1).GetText()
		data = self.db.fetch_one("SELECT * FROM jadwal WHERE id_jadwal='%s'" % id_jadwal)
		a = [str(x) for x in data]
		for x in a:
			self.inIdJadwal.SetValue(a[0])
			self.inNmJadwal.SetValue(a[1])
			self.inMulai.SetValue(a[2])
			self.inSelesai.SetValue(a[3])
			
		self.inIdJadwal.Enable(False)

	def save(self, event):
		IdJadwal = self.inIdJadwal.GetValue()
		Hari = self.inNmJadwal.GetValue()
		Mulai = self.inMulai.GetValue()
		Selesai = self.inSelesai.GetValue()
		nilaiEntry = [IdJadwal,Hari,Mulai,Selesai]
		val = Validasi(nilaiEntry)
		if val.FormKosong() == 1:
			pass
		else :
			tanya = wx.MessageDialog(None, "Yakin akan menyimpan?", "Konfirmasi", wx.YES_NO|wx.ICON_QUESTION)
			retCode = tanya.ShowModal()
			if (retCode == wx.ID_YES):
				idjadwal = self.db.fetch_field("SELECT id_jadwal From jadwal")
				if (nilaiEntry[0]) in idjadwal:
						alert = wx.MessageDialog(None,"ID Jadwal sudah digunakan, apakah akan diubah?","Peringatan",wx.YES_NO|wx.ICON_QUESTION)
						ret = alert.ShowModal()
						if (ret == wx.ID_YES):
							waktu = Validasi(nilaiEntry)
							if waktu.CekWaktu() == 1:
								pass
							else:
								if waktu.cekstatus() == 1:
									pass
								else:
									sql=("UPDATE jadwal SET hari='%s',mulai='%s',selesai='%s' WHERE id_jadwal='%s'") % (nilaiEntry[1],nilaiEntry[2],nilaiEntry[3],nilaiEntry[0])
									self.db.update_db(sql)
									wx.MessageDialog(self, 'Berhasil diubah', 'Informasi',wx.ICON_INFORMATION).ShowModal()
									self.clear(None)
									self.isilistctrl()
						else:
							pass
						alert.Destroy()
				else:
					waktu = Validasi(nilaiEntry)
					if waktu.CekWaktu() == 1:
						pass
					else:
						self.db.commit_db("INSERT INTO jadwal VALUES ('%s', '%s', '%s', '%s')" % \
								(nilaiEntry[0], nilaiEntry[1], nilaiEntry[2], nilaiEntry[3]))
						wx.MessageDialog(self, 'Berhasil disimpan', 'Informasi',
								wx.ICON_INFORMATION).ShowModal()
						self.clear(None)
						self.isilistctrl()
			else:
				pass
			tanya.Destroy()
				
	def clear(self, event):
		self.inIdJadwal.Clear()
		self.inNmJadwal.SetValue("")
		self.inMulai.SetValue('00:00:00')
		self.inSelesai.SetValue('00:00:00')
		self.AutoIncrementIdJadwal()
		
class Validasi():
	def __init__(self, nilaiEntry):
		self.IdJadwal = nilaiEntry[0]
		self.Hari = nilaiEntry[1]
		self.inMulai = nilaiEntry[2]
		self.inSelesai = nilaiEntry[3]
		self.db = dbutil.MySQL('localhost', 'root', 'k4g4t4u', 'lampu')
		
	def FormKosong(self):
		if ((not self.IdJadwal)|(not self.Hari) |(not self.inMulai) | (not self.inSelesai)):
			alert = wx.MessageDialog(None, "Form belum lengkap", "Error", wx.ID_OK)
			alert.ShowModal()
			alert.Destroy()
			return 1
		else:
			return 0
		
	def CekWaktu(self):
		if self.inMulai >= self.inSelesai:
			alert = wx.MessageDialog(None,"Waktu mulai harus lebih kecil dari waktu selesai","Error",wx.ID_OK)
			alert.ShowModal()
			alert.Destroy()
			return 1
		else:
			return 0

	def cekstatus(self):
		status = []
		data = self.db.fetch_all("SELECT status_jadwal from penjadwalan where id_jadwal='%s'" % (self.IdJadwal))
		for x in data:
			status.append(x[0])
		
		if 'Running' in status:
			alert = wx.MessageDialog(None,"Jadwal sedang berjalan","Error",wx.ID_OK)
			alert.ShowModal()
			alert.Destroy()
			return 1
		else:
			return 0
