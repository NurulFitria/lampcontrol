import wx
import re
import sys
import string
import serial
import time
from datetime import datetime, timedelta
from wx.lib.pubsub import Publisher
import wx.lib.masked as masked
from apscheduler.scheduler import Scheduler
from util import dbutil
import MySQLdb

ser = 0
db = dbutil.MySQL('localhost','root','k4g4t4u','lampu')
sched = Scheduler()
sched.start()
list_hari = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']

def rename_func(nama_baru):
    def decorator(func):
        func.__name__ = nama_baru
        return func
    return decorator

def nyala(nama_baru, ser, idlampu, idjadwal, index, hour, minute, second):
    @rename_func(nama_baru)
    @sched.cron_schedule(args=[idlampu,idjadwal], day_of_week=index, hour=hour, minute=minute, second=second)
    def nyalakan(idlampu, idjadwal):
        asal = 'penjadwalan'
        tanggal = datetime.now().strftime('%Y-%m-%d')
        waktu = time.strftime('%H:%M:%S')
        status = db.fetch_one("SELECT status from lampu WHERE id_lampu='%s'" % idlampu)
        pin = db.fetch_one("SELECT pin from lampu WHERE id_lampu='%s'" % idlampu)

        if status[0] == 'off':
            try:
                ser.write(str(pin[0]))
                switch = 'on'
                db.update_db("UPDATE lampu SET status='on' WHERE id_lampu='%s'" % idlampu)
                db.commit_db("INSERT INTO log VALUES('%s','%s','%s','%s','%s')" % (tanggal, waktu, idlampu, switch, asal))
                print 'On', idlampu
            except:
                wx.MessageDialog(self, 'Gagal menyalakan lampu ', 'Informasi', wx.ICON_INFORMATION).ShowModal()
        else:
            print 'Lampu %s sudah menyala sebelumnya' % idlampu

def mati(nama_baru, ser, idlampu, idjadwal, index, hour, minute, second):
    @rename_func(nama_baru)
    @sched.cron_schedule(args=[idlampu,idjadwal], day_of_week=index, hour=hour, minute=minute, second=second)
    def matikan(idlampu, idjadwal):
        asal = 'penjadwalan'
        tanggal = datetime.now().strftime('%Y-%m-%d')
        waktu = time.strftime('%H:%M:%S')
        status = db.fetch_one("SELECT status from lampu WHERE id_lampu='%s'" %(idlampu))
        pin = db.fetch_one("SELECT pin from lampu WHERE id_lampu='%s'" %(idlampu))
        #print status[0]
        if status[0] == 'on':
            try:
                ser.write(str(pin[0]))
                switch = 'off'
                db.update_db("UPDATE lampu SET status='off' WHERE id_lampu='%s'" % (idlampu))
                db.commit_db("INSERT INTO log VALUES('%s','%s','%s','%s','%s')" %  (tanggal,waktu,idlampu,switch,asal))
                #db.update_db("UPDATE penjadwalan SET status_jadwal='Off' WHERE id_lampu='%s'and id_jadwal='%s'" %(idlampu,idjadwal))
                #print 'Off', idlampu
            except:
                wx.MessageDialog(self, 'Gagal mematikan lampu ', 'Informasi', wx.ICON_INFORMATION).ShowModal()
        else:
            print 'Lampu %s sudah mati sebelumnya' % idlampu

        sched.print_jobs()


class Control(wx.Frame):
	def __init__(self, parent, frame_id):
		wx.Frame.__init__(self, parent, frame_id, "Kontrol Penjadwalan (Control Scheduling)", size=(500,650))
		panel = wx.Panel(self)

		self.list_ctrlone = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.list_ctrlone.InsertColumn(0, "No", width=30)
		self.list_ctrlone.InsertColumn(1, "Id Jadwal", width=100)
		self.list_ctrlone.InsertColumn(2, "Id lampu", width=100)
		self.list_ctrlone.InsertColumn(3, "Hari", width=100)
		self.list_ctrlone.InsertColumn(4, "Status Jadwal", width=150)
		self.list_ctrlone.Show(True)
		self.isilistctrl()

        # Event ketika memilih wx.ListCtrl
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._is_selected, self.list_ctrlone)

		self.frmLbl = wx.StaticText(panel, -1, "Kontrol Jadwal (Control Scheduling)")
		self.frmLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

		self.lbIdJadwal = wx.StaticText(panel, -1, "Id Jadwal ")
		self.inIdJadwal = wx.TextCtrl(panel, -1, "", size=(150, 25))
		self.lbNmJadwal = wx.StaticText(panel, -1, "Hari ")
		self.inNmJadwal = wx.TextCtrl(panel, -1, size=(150, 25))
		self.lbMulai = wx.StaticText(panel, -1, "Mulai ")
		self.inMulai = masked.TimeCtrl(panel, -1, name="24 hour control", fmt24hr=True)
		self.lbSelesai = wx.StaticText(panel, -1, "Selesai ")
		self.inSelesai = masked.TimeCtrl(panel, -1, name="24 hour control", fmt24hr=True)
		self.lbIdLampu = wx.StaticText(panel, -1, "Id Lampu ")
		self.inIdLampu = wx.TextCtrl(panel, -1, "", size=(150, 25))
		self.nonaktif()

        #---button
		self.BtnPlay = wx.Button(panel, -1, "Play")
		self.Bind(wx.EVT_BUTTON, self.play, self.BtnPlay)
		self.BtnStop = wx.Button(panel, -1, "Stop")
		self.Bind(wx.EVT_BUTTON, self.stop, self.BtnStop)
		self.BtnClear = wx.Button(panel, -1, "Bersih")
		self.Bind(wx.EVT_BUTTON, self.clear, self.BtnClear)
		self.BtnPlayAll = wx.Button(panel, -1, "Play All")
		self.Bind(wx.EVT_BUTTON, self.playall, self.BtnPlayAll)
		self.BtnStopAll = wx.Button(panel, -1, "Stop All")
		self.Bind(wx.EVT_BUTTON, self.stopall, self.BtnStopAll)
		self.inIdJadwal.SetInsertionPoint(0)

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
		self.MainLayer.Add(self.BtnPlayAll, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		self.MainLayer.Add(self.BtnStopAll, 0, wx.ALIGN_CENTER|wx.ALL, 5)
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
		#self.radioSizer.Add(self.Status, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
		#self.stextSz.Add(self.radioSizer, 0)
		self.entrySizer.Add(self.stextSz, 0, wx.EXPAND|wx.ALL, 10)

		self.btnSizer.Add(self.BtnPlay,0,wx.ALIGN_CENTER|wx.ALL, 10)
		self.btnSizer.Add(self.BtnStop,0,wx.ALIGN_CENTER|wx.ALL, 10)
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
		hasil = db.fetch_all("Select penjadwalan.id_jadwal,penjadwalan.id_lampu,jadwal.hari,penjadwalan.status_jadwal FROM penjadwalan,jadwal,lampu WHERE penjadwalan.id_jadwal=jadwal.id_jadwal and penjadwalan.id_lampu=lampu.id_lampu")
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
		data = db.fetch_one("SELECT penjadwalan.id_jadwal,penjadwalan.id_lampu,jadwal.hari,jadwal.mulai,jadwal.selesai,penjadwalan.status_jadwal FROM penjadwalan, jadwal WHERE penjadwalan.id_jadwal=jadwal.id_jadwal and penjadwalan.id_jadwal='%s' and penjadwalan.id_lampu='%s' " % (idjadwal, idlampu))
		a = [str(x) for x in data]
		for x in a:
			self.inIdJadwal.SetValue(a[0])
			self.inIdLampu.SetValue(a[1])
			self.inNmJadwal.SetValue(a[2])
			self.inMulai.SetValue(a[3])
			self.inSelesai.SetValue(a[4])
			status = (a[5])
			if status == 'Running':
				self.BtnPlay.Enable(False)
				self.BtnStop.Enable(True)
			else:
				self.BtnStop.Enable(False)
				self.BtnPlay.Enable(True)

			self.inIdJadwal.Enable(False)
			self.inIdLampu.Enable(False)

	def clear(self, event):
		self.bersih()

	def play(self, event):
		hari = self.inNmJadwal.GetValue()
		index = [list_hari.index(x) for x in list_hari if x == hari][0]
		idlampu = self.inIdLampu.GetValue()
		idjadwal = self.inIdJadwal.GetValue()
		awal = self.inMulai.GetValue()
		akhir = self.inSelesai.GetValue()
		pawal = awal.split(':')
		pakhir = akhir.split(':')
		h1 = pawal[0]
		m1 = pawal[1]
		s1 = pawal[2]
		h2 = pakhir[0]
		m2 = pakhir[1]
		s2 = pakhir[2]
		nama_baru = str('%s_%s' % (idlampu, idjadwal))
		nyala(nama_baru, ser, idlampu, idjadwal, index, h1, m1, s1)
		mati(nama_baru, ser, idlampu, idjadwal, index, h2, m2, s2)
		db.update_db("UPDATE penjadwalan SET status_jadwal='Running' WHERE id_lampu='%s' and id_jadwal='%s'" %(idlampu,idjadwal))
		wx.MessageDialog(self, 'Penjadwalan Dijalankan', 'Informasi',wx.ICON_INFORMATION).ShowModal()
		sched.print_jobs()
		self.bersih()
		self.nonaktif()
		self.isilistctrl()

	def playall(self, event):
		data = db.fetch_all("SELECT penjadwalan.id_jadwal,penjadwalan.id_lampu,jadwal.hari,jadwal.mulai,jadwal.selesai,penjadwalan.status_jadwal FROM penjadwalan, jadwal WHERE penjadwalan.id_jadwal=jadwal.id_jadwal AND penjadwalan.status_jadwal='Off'" )
		#print data
		if data == ():
			wx.MessageDialog(self, 'Penjadwalan sudah berjalan semua', 'Informasi',wx.ICON_INFORMATION).ShowModal()
		else:
			for x in data:
				a = [str(i) for i in x]
				idjadwal = a[0]
				idlampu = a[1]
				hari = a[2]
				mulai = a[3]
				selesai= a[4]
				#print hari
				for i in list_hari:
					if i == hari:
						d = list_hari.index(i)
						print d
					else:
						pass
				
				pawal = mulai.split(':')
				pakhir = selesai.split(':')
				h1 = pawal[0]
				m1 = pawal[1]
				s1 = pawal[2]
				h2 = pakhir[0]
				m2 = pakhir[1]
				s2 = pakhir[2]
				nama_baru = str('%s_%s' % (idlampu, idjadwal))
				nyala(nama_baru, ser, idlampu, idjadwal, d, h1, m1, s1)
				mati(nama_baru, ser, idlampu, idjadwal, d, h2, m2, s2)
			db.update_db("UPDATE penjadwalan SET status_jadwal='Running'")
		wx.MessageDialog(self, 'Semua penjadwalan dijalankan', 'Informasi',wx.ICON_INFORMATION).ShowModal()
		sched.print_jobs()
		self.isilistctrl()
		self.bersih()
		self.cek_run()

	def stop(self, event):
		idlampu = self.inIdLampu.GetValue()
		idjadwal = self.inIdJadwal.GetValue()
		nama = '%s_%s' % (idlampu, idjadwal)
		for jobs in sched.get_jobs():
			if jobs.__dict__['func'].__name__ == nama:
				sched.unschedule_job(jobs.__dict__['func'].job)

		db.update_db("UPDATE penjadwalan SET status_jadwal='Off' WHERE id_lampu='%s'and id_jadwal='%s'" %(idlampu,idjadwal))
		wx.MessageDialog(self, 'Penjadwalan Berhenti', 'Informasi',wx.ICON_INFORMATION).ShowModal()
		self.isilistctrl()
		self.bersih()
		sched.print_jobs()

	def stopall(self, event):
		data = db.fetch_all("SELECT id_lampu,id_jadwal from penjadwalan WHERE status_jadwal='Running'")
		#print data
		if data == ():
			wx.MessageDialog(self, 'Tidak ada jadwal yang sedang berjalan', 'Informasi',wx.ICON_INFORMATION).ShowModal()
		else:
			for x in data:
				nama = '%s_%s' % (x[0], x[1])
				for jobs in sched.get_jobs():
					if jobs.__dict__['func'].__name__ == nama:
						sched.unschedule_job(jobs.__dict__['func'].job)
						db.update_db("UPDATE penjadwalan SET status_jadwal='Off' WHERE id_lampu='%s' and id_jadwal='%s'"%(x[0],x[1]))
			wx.MessageDialog(self, 'Semua penjadwalan dihentikan', 'Informasi',wx.ICON_INFORMATION).ShowModal()
		sched.print_jobs()
		self.isilistctrl()
		self.bersih()
		self.cek_run()

	def cek_run(self):
		status = db.fetch_field("SELECT status_jadwal from penjadwalan")
		if 'Off' in status:
			self.BtnPlayAll.Enable(True)
			self.BtnStopAll.Enable(True)
		else:
			self.BtnStopAll.Enable(True)
			self.BtnPlayAll.Enable(False)

	def tampil(self,event):
		self.inNmJadwal.Clear()
		self.inMulai.SetValue("00:00:00")
		self.inSelesai.SetValue("00:00:00")
		id_jadwal = self.inIdJadwal.GetValue()
		if id_jadwal != '':
			data = db.fetch_one("SELECT hari,mulai,selesai From jadwal WHERE id_jadwal='%s'" % (id_jadwal))
			self.inNmJadwal.SetValue(data[0])
			self.inMulai.SetValue(str(data[1]))
			self.inSelesai.SetValue(str(data[2]))
			self.inIdLampu.SetFocus()

	def nonaktif(self):
		self.inNmJadwal.Enable(False)
		self.inMulai.Enable(False)
		self.inSelesai.Enable(False)
		self.inIdLampu.Enable(False)
		self.inIdJadwal.Enable(False)

	def bersih(self):
		self.inNmJadwal.SetValue("")
		self.inMulai.SetValue("00:00:00")
		self.inSelesai.SetValue("00:00:00")
		self.inIdLampu.SetValue("")
		self.inIdJadwal.SetValue("")
		self.BtnPlay.Enable(True)
		self.isilistctrl()
