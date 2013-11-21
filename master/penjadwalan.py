import wx
import re
import sys
import string
from datetime import datetime, timedelta
import time
import threading
from wx.lib.pubsub import Publisher
import wx.lib.masked as masked
from util import dbutil
import MySQLdb

class Penjadwalan(wx.Frame):
	def __init__(self, parent, frame_id):
		wx.Frame.__init__(self, parent, frame_id, "Penjadwalan (Scheduling)", size=(500,600))
		self.db = dbutil.MySQL("localhost","root","k4g4t4u","lampu")
		panel = wx.Panel(self)	

		self.list_ctrlone = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.list_ctrlone.InsertColumn(0, "No", width=30)
		self.list_ctrlone.InsertColumn(1, "Id Jadwal", width=150)
		self.list_ctrlone.InsertColumn(2, "Id lampu", width=100)
		self.list_ctrlone.InsertColumn(3, "Hari", width=100)
		self.list_ctrlone.InsertColumn(4, "Status Jadwal", width=100)
		self.list_ctrlone.Show(True)
		self.isilistctrl()
		
#========================isi combo id jadwal from database
		data1 = self.db.fetch_field("SELECT id_jadwal FROM jadwal ")
		data2 = self.db.fetch_field("SELECT id_lampu FROM lampu ")
		
		
#=================================event ketika memilih listctrl
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._is_selected, self.list_ctrlone)
		
		self.frmLbl = wx.StaticText(panel, -1, "Penjadwalan (Scheduling)")
		self.frmLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.lbIdJadwal = wx.StaticText(panel, -1, "Id Jadwal ")
		self.inIdJadwal = wx.ComboBox(panel, -1, "", size=(150, 25),choices=data1, style=wx.CB_READONLY)
		self.Bind(wx.EVT_COMBOBOX, self.tampil, self.inIdJadwal)
		self.lbNmJadwal = wx.StaticText(panel, -1, "Hari ")
		self.inNmJadwal = wx.TextCtrl(panel, -1, size=(150, 25))
		self.lbMulai = wx.StaticText(panel, -1, "Mulai ")
		self.inMulai = masked.TimeCtrl(panel, -1, name="24 hour control", fmt24hr=True)
		self.lbSelesai = wx.StaticText(panel, -1, "Selesai ")
		self.inSelesai = masked.TimeCtrl(panel, -1, name="24 hour control", fmt24hr=True)
		self.lbIdLampu = wx.StaticText(panel, -1, "Id Lampu ")
		self.inIdLampu = wx.ComboBox(panel, -1, "", size=(150, 25),choices=data2, style=wx.CB_READONLY)
		
		#---button
		self.BtnSave = wx.Button(panel, -1, "Save")
		self.Bind(wx.EVT_BUTTON, self.save, self.BtnSave)
		self.BtnDelete = wx.Button(panel, -1, "Delete")
		self.Bind(wx.EVT_BUTTON, self.delete, self.BtnDelete)
		self.BtnClear = wx.Button(panel, -1, "Clear")
		self.Bind(wx.EVT_BUTTON, self.clear, self.BtnClear)
		
		self.inIdJadwal.SetInsertionPoint(0)		
		self.nonaktif()
		
		#adding sizer
		self.MainLayer = wx.BoxSizer(wx.VERTICAL)
		self.entrySizer = wx.BoxSizer(wx.VERTICAL)
		self.stextSz = wx.FlexGridSizer(cols = 2, hgap = 5, vgap = 5)
		self.stextSz.AddGrowableCol(1)
		self.btnSizer= wx.BoxSizer(wx.HORIZONTAL)
		

		self.MainLayer.Fit(self)
		self.MainLayer.SetSizeHints(self)
		panel.SetSizer(self.MainLayer)
		self.aturSizer(panel)

	def aturSizer(self, panel):
		self.MainLayer.Add(self.frmLbl, 0, wx.ALL, 5)
		self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
		#---entry sizer
		self.stextSz.Add(self.lbIdJadwal, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.stextSz.Add(self.inIdJadwal, 0)
		self.stextSz.Add(self.lbNmJadwal, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.stextSz.Add(self.inNmJadwal, 0)
		self.stextSz.Add(self.lbMulai, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.stextSz.Add(self.inMulai, 0)
		self.stextSz.Add(self.lbSelesai, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.stextSz.Add(self.inSelesai, 0)
		self.stextSz.Add(self.lbIdLampu, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
		self.stextSz.Add(self.inIdLampu, 0)

		self.entrySizer.Add(self.stextSz, 0, wx.EXPAND|wx.ALL, 10)
		
		self.btnSizer.Add(self.BtnSave,0,wx.ALIGN_CENTER|wx.ALL, 10)
		self.btnSizer.Add(self.BtnDelete,0,wx.ALIGN_CENTER|wx.ALL, 10)
		self.btnSizer.Add(self.BtnClear,0,wx.ALIGN_CENTER|wx.ALL, 10)
		self.BtnDelete.Enable(False)
		
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
		hasil = self.db.fetch_all("Select penjadwalan.id_jadwal,penjadwalan.id_lampu,jadwal.hari,penjadwalan.status_jadwal \
		    FROM penjadwalan,jadwal,lampu \
			 WHERE penjadwalan.id_jadwal=jadwal.id_jadwal and penjadwalan.id_lampu=lampu.id_lampu")
		
		str_hasil = str(hasil)
		kosong = '()'
		for enum, isi in enumerate(hasil):
			enum += 1
			prim = self.list_ctrlone.InsertStringItem(sys.maxint, str(enum))
			self.list_ctrlone.SetStringItem(prim, 1, str(isi[0]))
			self.list_ctrlone.SetStringItem(prim, 2, str(isi[1]))
			self.list_ctrlone.SetStringItem(prim, 3, str(isi[2]))
			self.list_ctrlone.SetStringItem(prim, 4, str(isi[3]))
		
		
	def _is_selected(self, event):
		idjadwal = self.list_ctrlone.GetItem(event.GetIndex(), 1).GetText()
		idlampu = self.list_ctrlone.GetItem(event.GetIndex(), 2).GetText()
		data = self.db.fetch_one("Select penjadwalan.id_jadwal,penjadwalan.id_lampu,jadwal.hari,jadwal.mulai,jadwal.selesai \
		       FROM penjadwalan,jadwal WHERE penjadwalan.id_jadwal=jadwal.id_jadwal and penjadwalan.id_jadwal='%s' \
		       and penjadwalan.id_lampu='%s' " % (idjadwal,idlampu))
		a = [str(x) for x in data]
		
		for x in a:
			self.inIdJadwal.SetValue(a[0])
			self.inIdLampu.SetValue(a[1])
			self.inNmJadwal.SetValue(a[2])
			self.inMulai.SetValue(a[3])
			self.inSelesai.SetValue(a[4])
			
		self.inIdJadwal.Enable(False)
		self.inIdLampu.Enable(False)
		self.BtnSave.Enable(False)
		self.BtnDelete.Enable(True)

	def save(self, event):
		idlampu = self.inIdLampu.GetValue()
		idjadwal = self.inIdJadwal.GetValue()
		hari = self.inNmJadwal.GetValue()
		mulai = datetime.strptime(self.inMulai.GetValue(),'%H:%M:%S')
		selesai = datetime.strptime(self.inSelesai.GetValue(),'%H:%M:%S')
		x = [idlampu,idjadwal]
		status = "Off"
		tanya = wx.MessageDialog(None, "Yakin akan menyimpan?", "Konfirmasi", wx.YES_NO|wx.ICON_QUESTION)
		retCode = tanya.ShowModal()
		if (retCode == wx.ID_YES):
			hasil = self.db.fetch_one("Select id_lampu,id_jadwal From penjadwalan \
			        WHERE id_lampu='%s' and id_jadwal='%s'" % (idlampu,idjadwal))
			if (idlampu,idjadwal) == hasil:
				wx.MessageDialog(self, 'Id Jadwal dan Id lampu sudah digunakan', 'Error',wx.ICON_INFORMATION).ShowModal()
			else:
				idlampu1 = self.db.fetch_one("Select id_lampu From penjadwalan where id_lampu=%s" % (idlampu))
				hari1 = self.db.fetch_one("Select jadwal.hari From jadwal,penjadwalan \
				        WHERE jadwal.id_jadwal=penjadwalan.id_jadwal and penjadwalan.id_lampu='%s'" % (idlampu))
				
				if idlampu1 == None:
					self.db.commit_db("INSERT INTO penjadwalan VALUES ('%s', '%s','%s')" % (x[0], x[1],status))
					wx.MessageDialog(self, 'Berhasil disimpan!', 'Berhasil',
						wx.ICON_INFORMATION).ShowModal()
				else:
					if (idlampu == idlampu1[0]) and (hari == hari1[0]) == True:
						jml_jadwal = self.db.fetch_one("Select COUNT(jadwal.id_jadwal) from jadwal,penjadwalan \
						             WHERE penjadwalan.id_jadwal=jadwal.id_jadwal and penjadwalan.id_lampu='%s' \
						             and jadwal.hari='%s' " %(idlampu,hari))
						
						if jml_jadwal[0] >= 2 :
							wx.MessageDialog(self, 'Lampu sudah punya 2 penjadwalan', 'Error',wx.ICON_INFORMATION).ShowModal()
						else:
							cek = self.db.fetch_one("Select jadwal.mulai, jadwal.selesai From penjadwalan,jadwal \
								where penjadwalan.id_jadwal=jadwal.id_jadwal and penjadwalan.id_lampu=%s " % (idlampu1))
						
							mulai_awal = datetime.strptime(str(cek[0]),'%H:%M:%S')
							selesai_awal = datetime.strptime(str(cek[1]),'%H:%M:%S')
							

							if (selesai >= mulai_awal and selesai <= selesai_awal) or (mulai <= selesai_awal and mulai >= mulai_awal) or (mulai <= mulai_awal and selesai >= selesai_awal):
								wx.MessageDialog(self, 'Jadwal ini sudah ada di range jadwal sebelumnya', 'Error',
									wx.ICON_INFORMATION).ShowModal()
							else:
								
								self.db.commit_db("INSERT INTO penjadwalan VALUES ('%s', '%s','%s')" % (x[0], x[1],status))
								wx.MessageDialog(self, 'Berhasil disimpan!', 'Berhasil',
								wx.ICON_INFORMATION).ShowModal()
					else:
						
						self.db.commit_db("INSERT INTO penjadwalan VALUES ('%s', '%s','%s')" % (x[0], x[1],status))
						wx.MessageDialog(self, 'Berhasil disimpan!', 'Berhasil',
							wx.ICON_INFORMATION).ShowModal()
		else:
			pass
			tanya.Destroy()		
					

		self.clear(None)
		self.BtnDelete.Enable(True)
		self.isilistctrl()
		
	def delete(self, event):
		idlampu = self.inIdLampu.GetValue()
		idjadwal = self.inIdJadwal.GetValue()
		status = self.db.fetch_one("SELECT status_jadwal from penjadwalan where id_jadwal='%s' and id_lampu='%s'" % (idjadwal,idlampu))
		if status[0] != 'Running':
			sql = ("DELETE FROM penjadwalan where id_jadwal='%s' and id_lampu='%s'" % (idjadwal,idlampu))
			self.db.delete_db(sql)
			wx.MessageDialog(self, 'Berhasil dihapus!', 'Berhasil', wx.ICON_INFORMATION).ShowModal()
		else:
			wx.MessageDialog(self, 'Tidak bisa dihapus, penjadwalan sedang berjalan', 'Informasi', wx.ICON_INFORMATION).ShowModal()
		self.clear(None)
		self.isilistctrl()
		
	def tampil(self,event):
		self.inNmJadwal.Clear()
		self.inMulai.SetValue("00:00:00")
		self.inSelesai.SetValue("00:00:00")
		id_jadwal = self.inIdJadwal.GetValue()
		if id_jadwal != '':
			data = self.db.fetch_one("SELECT hari,mulai,selesai From jadwal WHERE id_jadwal='%s'" % (id_jadwal))
			self.inNmJadwal.SetValue(data[0])
			self.inMulai.SetValue(str(data[1]))
			self.inSelesai.SetValue(str(data[2]))
			self.inIdLampu.SetFocus()
		
	def clear(self, event):
		self.inIdJadwal.SetValue("")
		self.inIdLampu.SetValue("")
		self.inIdLampu.Enable(True)
		self.inIdJadwal.Enable(True)
		self.inNmJadwal.SetValue("")
		self.inMulai.SetValue("00:00:00")
		self.inSelesai.SetValue("00:00:00")
		self.BtnSave.Enable(True)
		self.inIdJadwal.SetFocus()
		
	def nonaktif(self):
		self.inNmJadwal.Enable(False)
		self.inMulai.Enable(False)
		self.inSelesai.Enable(False)
		
	def aktif(self):
		self.inNmJadwal.Enable(True)
		self.inMulai.Enable(True)
		self.inSelesai.Enable(True)
