#===========================================================Main.py================================================
import wx
import time
import os
import sys
import wx.lib.agw.ribbon as RB
import wx.lib.dialogs
import threading
import MySQLdb
from wx.lib.pubsub import Publisher
from datetime import datetime,timedelta
from util import settings as st,dbutil
from master import lamp, jadwal, penjadwalan, monitoring,saklar,log

e = threading.Event()
threads = []

def getSec(s):
	l = s.split(':')
	return int(l[0]) * 3600 + int(l[1]) * 60 + int(l[2])


ID_CIRCLE = wx.ID_HIGHEST + 1
ID_PLAY = ID_CIRCLE + 1
ID_STOP = ID_CIRCLE + 2
ID_HELP = ID_CIRCLE + 3
ID_ABOUT = ID_CIRCLE + 4
ID_SCHEDULE = ID_CIRCLE + 5
ID_SCHEDULER = ID_CIRCLE + 6
ID_MONITORING = ID_CIRCLE + 7
ID_ACCOUNT = ID_CIRCLE + 8
ID_LAMP = ID_CIRCLE + 9
ID_LOG = ID_CIRCLE + 10

class PanelUtama(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent=parent)
		self.frame = parent
		self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

	def OnEraseBackground(self, evt):
		dc = evt.GetDC()
		if not dc:
			dc = wx.ClientDC(self)
			rect = self.GetUpdateRegion().GetBox()
			dc.SetClippingRect(rect)
		dc.Clear()
		bmp = wx.Bitmap("gambar/bg1.png")
		dc.DrawBitmap(bmp, 0, 0)

class RibbonFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, -1, 'Lamp control system via Twitter', size=(1020,700))
		self._ribbon = RB.RibbonBar(self, wx.ID_ANY)
		self.db = dbutil.MySQL('localhost', 'root', 'root', 'lampu')
		self.thread = None
		self.putar = False
		#t = Twitter.twit()
		#t.main()


		home = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Master")
		lamp_panel =  RB.RibbonPanel(home, wx.ID_ANY, "Lamp", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
		schedule_panel = RB.RibbonPanel(home, wx.ID_ANY, "Schedule", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
		scheduler_panel = RB.RibbonPanel(home, wx.ID_ANY, "Scheduler", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
		monitoring_panel = RB.RibbonPanel(home, wx.ID_ANY, "Monitoring", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)


		tool_tab = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Tool")#isi gambar
		play_panel = RB.RibbonPanel(tool_tab, wx.ID_ANY, "Play", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
		stop_panel = RB.RibbonPanel(tool_tab, wx.ID_ANY, "Stop", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
		log_panel = RB.RibbonPanel(tool_tab, wx.ID_ANY, "Stop", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
		account_panel = RB.RibbonPanel(tool_tab, wx.ID_ANY, "Saklar", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)

		help_tab = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Help")#isi gambar
		help_panel = RB.RibbonPanel(help_tab, wx.ID_ANY, "Help", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
		about_panel = RB.RibbonPanel(help_tab, wx.ID_ANY, "About", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)

		lamp_bar = RB.RibbonButtonBar(lamp_panel)
		schedule_bar = RB.RibbonButtonBar(schedule_panel)
		scheduler_bar = RB.RibbonButtonBar(scheduler_panel)
		monitoring_bar = RB.RibbonButtonBar(monitoring_panel)

		account_bar = RB.RibbonButtonBar(account_panel)
		log_bar = RB.RibbonButtonBar(log_panel)
		self.play_bar = RB.RibbonButtonBar(play_panel)
		self.stop_bar = RB.RibbonButtonBar(stop_panel)

		help_bar = RB.RibbonButtonBar(help_panel)
		about_bar = RB.RibbonButtonBar(about_panel)

		lamp_bar.AddSimpleButton(ID_LAMP, "Lamp (Lampu)", wx.Bitmap(st._lamp), help_string="Lampu (Lamp)")
		schedule_bar.AddSimpleButton(ID_SCHEDULE, "Schedule (Jadwal)", wx.Bitmap(st._schedule), help_string="Jadwal (Schedule)")
		scheduler_bar.AddSimpleButton(ID_SCHEDULER, "Scheduler (Penjadwalan)", wx.Bitmap(st._scheduler), help_string="Penjadwalan (Scheduler)")
		monitoring_bar.AddSimpleButton(ID_MONITORING, "Monitoring", wx.Bitmap(st._monitoring), help_string="Monitoring")

		account_bar.AddSimpleButton(ID_ACCOUNT, "Switch (Saklar)", wx.Bitmap(st._account), help_string="Switch (Saklar)")
		log_bar.AddSimpleButton(ID_LOG, "Log (log)", wx.Bitmap(st._log), help_string="Log (Log)")
		self.play_bar.AddSimpleButton(ID_PLAY, "Start (Mulai)", wx.Bitmap(st._play), help_string="Play")
		self.stop_bar.AddSimpleButton(ID_STOP, "Stop (Berhenti)", wx.Bitmap(st._stop), help_string="Stop")

		help_bar.AddSimpleButton(ID_HELP, "Help (Bantuan)", wx.Bitmap(st._help), help_string="Help")
		about_bar.AddSimpleButton(ID_ABOUT, "About (Tentang)", wx.Bitmap(st._about), help_string="About")

		lamp_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnLamp, id=ID_LAMP)
		schedule_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnSchedule, id=ID_SCHEDULE)
		scheduler_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnScheduler, id=ID_SCHEDULER)
		monitoring_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnMonitoring, id=ID_MONITORING)

		account_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnAccount, id=ID_ACCOUNT)
		log_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnLog, id=ID_LOG)
		self.play_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnPlay, id=ID_PLAY)
		self.stop_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnStop, id=ID_STOP)

		help_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnHelp, id=ID_HELP)
		about_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnAbout, id=ID_ABOUT)

		self._ribbon.Realize()
		panel = PanelUtama(self)
		s = wx.BoxSizer(wx.VERTICAL)
		s.Add(self._ribbon, 1, wx.EXPAND| wx.GROW)
		s.Add(panel, 3, wx.EXPAND| wx.GROW)
		self.SetSizer(s)

	def OnLamp(self, event):
		win = lamp.Lamp(self, -1)
		win.Show()
		win.Center()

	def OnSchedule(self, event):
		win = jadwal.Jadwal(self, -1)
		win.Show()
		win.Center()

	def OnScheduler(self, event):
		win = penjadwalan.Penjadwalan(self, -1)
		win.Show()
		win.Center()

	def OnMonitoring(self, event):
		win = monitoring.Monitoring(self, -1)
		win.Show()
		win.Center()

	def OnAccount(self, event):
		win = saklar.Saklar(self, -1)
		win.Show()
		win.Center()

	def OnPlay(self, event):
		self.play_bar.Disable()
		self.stop_bar.Enable()
		self.putar = True
		Publisher().sendMessage('putar', self.putar)
		e.set()
		print e
		list_hari = {
			'Sunday': 'Minggu',
			'Monday': 'Senin',
			'Tuesday': 'Selasa',
			'Wednesday': 'Rabu',
			'Thursday': 'Kamis',
			'Friday': 'Jumat',
			'Saturday': 'Sabtu'
		}
		#waktu_sekarang = datetime.now().time()
		hari_ini = [list_hari[x] for x in list_hari if x == datetime.now().strftime("%A")][0]
		print hari_ini
		jobs = self.db.fetch_all("Select penjadwalan.id_lampu, jadwal.mulai, jadwal.selesai, penjadwalan.id_jadwal \
            		from penjadwalan,jadwal where \
			penjadwalan.id_jadwal=jadwal.id_jadwal and \
			penjadwalan.id_jadwal in (select id_jadwal from jadwal where hari='%s')" % (hari_ini))
		print jobs
		if jobs == ():
			print 'tidak ada jadwal'
			skr = time.strftime('%H:%M:%S')
			tunggu = getSec('23:59:59') - getSec(skr)
			er = threading.Thread(target=self.OnTunggu, args=(tunggu, ))
			er.setDaemon(True)
			threads.append(er)
			er.start()
		else:
			skr = time.strftime('%H:%M:%S')
			tunggu = getSec('23:59:59') - getSec(skr)
			er = threading.Thread(target=self.OnTunggu, args=(tunggu, ))
			er.setDaemon(True)
			threads.append(er)
			er.start()
			for job in jobs:
				awal = job[1]
				akhir = job[2]
				idjadwal = job[3]
				status = self.db.fetch_one("SELECT status FROM lampu WHERE id_lampu='%s' " % (job[0]))
				pin = self.db.fetch_one("SELECT pin FROM lampu WHERE id_lampu='%s' " % (job[0]))
				self.thread = threading.Thread(target=self.Nyalakan, args=(job[0],awal,akhir,status, pin,idjadwal, ))
				threads.append(self.thread)
				self.thread.setDaemon(True)
				self.thread.start()
			print threads

	def Nyalakan(self,idlampu,awal,akhir,status,pin,idjadwal):
		now = datetime.strptime(time.strftime("%H:%M:%S"),'%H:%M:%S')
		skr = time.strftime('%H:%M:%S')
		sleep1 =  getSec(str(awal)) - getSec(skr)

		if (datetime.strptime(str(awal),'%H:%M:%S').time() < now.time()) and (datetime.strptime(str(akhir),'%H:%M:%S').time() > now.time()) == True:
			if status[0] == 'Off':
				#ser.write(pin)
				print 'On',idlampu
				self._update_lampu('On',idlampu)
				self._update_penjadwalan('Running',idlampu,idjadwal)
				self._isi_log('On',idlampu)

				interval = (datetime.strptime(str(akhir), '%H:%M:%S'))-(datetime.strptime(str(now.time()), '%H:%M:%S'))
				interval = interval.seconds
				time.sleep(interval-5)
				if self._cek_status(idlampu) == 1:
					time.sleep(5)
					self._update_penjadwalan('Finish',idlampu,idjadwal)
					self._isi_log('Off',idlampu)
				else:
					time.sleep(5)
					print 'Done',idlampu
					#ser.write(pin)
					self._update_lampu('Off',idlampu)
					self._update_penjadwalan('Finish',idlampu,idjadwal)
					self._isi_log('Off',idlampu)
			else:
				print 'Sudah nyala',idlampu
				self._update_penjadwalan('Running',idlampu,idjadwal)
				interval = (datetime.strptime(str(akhir), '%H:%M:%S'))-(datetime.strptime(str(now.time()), '%H:%M:%S'))
				interval = interval.seconds
				time.sleep(interval-5)
				if self._cek_status(idlampu) == 1:
					time.sleep(5)
					self._update_penjadwalan('Finish',idlampu,idjadwal)
					self._isi_log('Off',idlampu)
				else:
					time.sleep(5)
					print 'Done',idlampu
					#ser.write(pin)
					self._update_lampu('Off',idlampu)
					self._update_penjadwalan('Finish',idlampu,idjadwal)
					self._isi_log('Off',idlampu)
		elif (datetime.strptime(str(awal),'%H:%M:%S').time() > now.time()) and (datetime.strptime(str(akhir),'%H:%M:%S').time() > now.time()) == True:
			#if status[0] == 'Off':
			self._update_penjadwalan('Waiting',idlampu,idjadwal)
			print 'tunggu'
			interval1 = (datetime.strptime(str(awal), '%H:%M:%S'))-(datetime.strptime(str(now.time()), '%H:%M:%S'))
			interval1 = interval1.seconds
			time.sleep(interval1-5)
			if self._cek_status(idlampu) == 0:
				time.sleep(5)
				self._update_penjadwalan('Running',idlampu,idjadwal)
				interval3 = (datetime.strptime(str(akhir), '%H:%M:%S'))-(datetime.strptime(str(now.time()), '%H:%M:%S'))
				interval3 = interval3.seconds
				time.sleep(interval3-5)

				if self._cek_status(idlampu) == 1:
					time.sleep(5)
					self._update_penjadwalan('Finish',idlampu,idjadwal)
					self._isi_log('Off',idlampu)
				else:
					time.sleep(5)
					#ser.write(pin)
					print 'Done',idlampu
					self._update_lampu('Off',idlampu)
					self._update_penjadwalan('Finish',idlampu,idjadwal)
					self._isi_log('Off',idlampu)
			else:
				time.sleep(5)
				#ser.write(pin)
				print 'On',idlampu
				self._update_lampu('On',idlampu)
				self._update_penjadwalan('Running',idlampu,idjadwal)
				self._isi_log('On',idlampu)
				interval2 = (datetime.strptime(str(akhir), '%H:%M:%S'))-(datetime.strptime(str(awal), '%H:%M:%S'))
				interval2 = interval2.seconds
				time.sleep(interval2-5)
				if self._cek_status(idlampu) == 1:
					time.sleep(5)
					self._update_penjadwalan('Finish',idlampu,idjadwal)
					self._isi_log('Off',idlampu)
				else:
					time.sleep(5)
					#ser.write(pin)
					print 'Done',idlampu
					self._update_lampu('Off',idlampu)
					self._update_penjadwalan('Finish',idlampu,idjadwal)
					self._isi_log('Off',idlampu)
        #else:
            #print 'sudah lewat',idlampu
            #self._update_penjadwalan('Finish',idlampu,idjadwal)

	def OnTunggu(self, s):
		print 'thread hari ini'
		time.sleep(s+2)
		print 'thread hari berikutnya'
		self.OnPlay(None)

	def _update_lampu(self, switch,idlampu):
		sql = ("UPDATE lampu SET status='%s' WHERE id_lampu='%s'" % (switch,idlampu))
		self.db.update_db(sql)

	def _isi_log(self, switch,idlampu):
		asal = 'penjadwalan'
		tanggal = datetime.now().strftime('%Y-%m-%d')
		waktu = time.strftime('%H:%M:%S')
		self.db.commit_db("INSERT INTO log VALUES('%s','%s','%s','%s','%s')" % (tanggal,waktu,idlampu,switch,asal))


	def _update_penjadwalan(self, status,idlampu,idjadwal):
		sql = ("UPDATE penjadwalan SET status='%s' WHERE id_lampu='%s' and id_jadwal='%s' " % (status,idlampu,idjadwal))
		self.db.update_db(sql)

	def _cek_status(self,idlampu):
		status = self.db.fetch_one("SELECT status FROM lampu WHERE id_lampu='%s'" % (idlampu))
		if status[0] == 'Off':
			return 1
		else:
			return 0
		
	def OnStop(self, event):
		self.play_bar.Enable()
		self.stop_bar.Disable()
		self.putar = False
		print self.putar
		Publisher().sendMessage('putar',self.putar)
		e.clear()
		print e
		for t in threads:
			#t.join(timeout=1)
			print t
            		t.exit()
		print 'All Done'

	def OnLog(self,event):
		win = log.Log(self, -1)
		win.Show()
		win.Center()

	def OnHelp(self, event):
		f = open("manual.txt", "r")
		msg = f.read()
		f.close()

		dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg, "Bantuan Penggunaan")
		dlg.ShowModal()

		dlg.Destroy()

	def OnAbout(self, event):
		tentang = """Program ini dibuat untuk mempermudah pengaturan aktivitas lampu sesuai dengan jadwal yang ada dan dapat dikendalikan secara jarak jauh melalui Twitter"""
		lisensi = """Program ini adalah free software, anda bisa merubahnya dan atau hasil perubahannya itu disebarluaskan \n dibawah ketentuan GNU General Public License yang dikeluarkan oleh Free Software Foundation;"""

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

if __name__ == '__main__':
	app = wx.PySimpleApp()
	parent = RibbonFrame()
	parent.Show(True)
	parent.Center()
	app.MainLoop()
