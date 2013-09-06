import wx
import re
import sys
import string
import time
import threading
from wx.lib.pubsub import Publisher
import wx.lib.masked as masked
from util import dbutil

class Monitoring(wx.Frame):
	def __init__(self, parent, frame_id):
		wx.Frame.__init__(self, parent, frame_id, "Monitoring", size=(600,400))
		self.db=dbutil.MySQL("localhost","root","k4g4t4u","lampu")
		panel = wx.Panel(self)
		
		self.list_ctrlone = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.list_ctrlone.InsertColumn(0, "No", width=30)
		self.list_ctrlone.InsertColumn(1, "Id_Lampu", width=90)
		self.list_ctrlone.InsertColumn(2, "Hari", width=100)
		self.list_ctrlone.InsertColumn(3, "Mulai", width=100)
		self.list_ctrlone.InsertColumn(4, "Selesai", width=100)
		self.list_ctrlone.InsertColumn(5, "Status Penjadwalan", width=150)
		self.list_ctrlone.Show(True)
		self.isilistctrl()
		
		self.BtnRefresh = wx.Button(panel, -1, "Refresh")		
		self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.BtnRefresh)
		
		self.frmLbl = wx.StaticText(panel, -1, "Monitoring")
		self.frmLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.lbltime = wx.StaticText(panel, -1, "00:00:00")
		self.lbltime.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
		
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.update, self.timer)
		self.timer.Start(1000)
		
		self.MainLayer = wx.BoxSizer(wx.VERTICAL)
		self.btnSizer= wx.BoxSizer(wx.HORIZONTAL)
		

		self.MainLayer.Fit(self)
		self.MainLayer.SetSizeHints(self)
		panel.SetSizer(self.MainLayer)
		
		self.aturSizer(panel)
		

	def aturSizer(self, panel):
		self.MainLayer.Add(self.frmLbl, 0, wx.ALL, 5)
		self.MainLayer.Add(self.lbltime, 0, wx.ALIGN_RIGHT, 5)
		self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
		#Agar ketika di tekan TAB kursor berpindah secara berurutan
		self.listSz = wx.BoxSizer(wx.VERTICAL)
		
		self.listSz.Add(self.list_ctrlone, 1, wx.EXPAND|wx.ALL, 20)
		self.btnSizer.Add(self.BtnRefresh)
		#------------------------------------------------------------------------
		self.MainLayer.Add(self.listSz,1, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
		self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)
		self.MainLayer.Add(self.btnSizer, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
		self.MainLayer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM,5)

	def update(self, event):
		now = time.strftime("%H:%M:%S")
		self.lbltime.SetLabel(now)

	def OnRefresh(self,event):
		self.isilistctrl()

	def make_thread(self):
		r = threading.Thread(target=self.update_list)
		r.start()

	def update_list(self):
		self.isilistctrl()
		time.sleep(5)
		wx.CallAfter(self.make_thread)			
		
	def isilistctrl(self):
		self.list_ctrlone.DeleteAllItems()
		hasil = self.db.fetch_all("Select distinct penjadwalan.id_lampu,jadwal.hari,jadwal.mulai,jadwal.selesai,penjadwalan.status_jadwal FROM penjadwalan,jadwal WHERE penjadwalan.id_jadwal=jadwal.id_jadwal order by penjadwalan.id_lampu")
		str_hasil = str(hasil)
		kosong = '()'
		for enum, isi in enumerate(hasil):
			enum += 1
			prim = self.list_ctrlone.InsertStringItem(sys.maxint, str(enum))
			self.list_ctrlone.SetStringItem(prim, 1, str(isi[0]))
			self.list_ctrlone.SetStringItem(prim, 2, str(isi[1]))
			self.list_ctrlone.SetStringItem(prim, 3, str(isi[2]))
			self.list_ctrlone.SetStringItem(prim, 4, str(isi[3]))
			self.list_ctrlone.SetStringItem(prim, 5, str(isi[4]))
