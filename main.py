import wx
import time
import os
import sys
import tweepy
import wx.lib.dialogs
import MySQLdb
import serial
import threading
import logging
from wx.lib.pubsub import Publisher
import wx.lib.agw.ribbon as RB
from datetime import datetime,timedelta
from util import settings as st,dbutil,ser
from master import lamp, jadwal, penjadwalan, monitoring,saklar,log,control


logging.basicConfig()
CK = 'GJOnLjmLfAGrg5qgO7Cqg'
CS = "3gNrz7B4pxQjSIbY81xUC61O9biIhYx15XJwzDpHbw"
AT = "719356627-TLd9WqTD0SmGhkgRg9NSXt79oGnj7zSXgLcXS3Fk"
ATS = "2LyqArOBeVpVYKHjjNtEhWYxBOwJwj77VENaR8N7Ls0"
quit = False

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
		bmp = wx.Bitmap("gambar/image10.png")
		dc.DrawBitmap(bmp, 0, 0)

class RibbonFrame(wx.Frame):	
	def __init__(self):
		wx.Frame.__init__(self, None, -1, 'Sistem Penjadwalan dan Kendali lampu via Twitter', size=(1042,700))
		self._ribbon = RB.RibbonBar(self, wx.ID_ANY)
		self.db = dbutil.MySQL('localhost', 'root', 'k4g4t4u', 'lampu')					
		self.ser = None
		ser = None
		self.api = None
		friends = []
		
		home = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Master")
		lamp_panel =  RB.RibbonPanel(home, wx.ID_ANY, "Lamp", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
		schedule_panel = RB.RibbonPanel(home, wx.ID_ANY, "Schedule", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
		scheduler_panel = RB.RibbonPanel(home, wx.ID_ANY, "Scheduling", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)
		monitoring_panel = RB.RibbonPanel(home, wx.ID_ANY, "Monitoring", wx.NullBitmap, wx.DefaultPosition, agwStyle=RB.RIBBON_PANEL_NO_AUTO_MINIMISE)


		tool_tab = RB.RibbonPage(self._ribbon, wx.ID_ANY, "Tool")#isi gambar
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
		#self.play_bar = RB.RibbonButtonBar(play_panel)
		self.stop_bar = RB.RibbonButtonBar(stop_panel)

		help_bar = RB.RibbonButtonBar(help_panel)
		about_bar = RB.RibbonButtonBar(about_panel)

		lamp_bar.AddSimpleButton(ID_LAMP, "Lamp (Lampu)", wx.Bitmap(st._lamp), help_string="Lampu (Lamp)")
		schedule_bar.AddSimpleButton(ID_SCHEDULE, "Schedule (Jadwal)", wx.Bitmap(st._schedule), help_string="Jadwal (Schedule)")
		scheduler_bar.AddSimpleButton(ID_SCHEDULER, "Scheduling (Penjadwalan)", wx.Bitmap(st._scheduler), help_string="Penjadwalan (Scheduler)")
		monitoring_bar.AddSimpleButton(ID_MONITORING, "Monitoring", wx.Bitmap(st._monitoring), help_string="Monitoring")

		account_bar.AddSimpleButton(ID_ACCOUNT, "Switch (Saklar)", wx.Bitmap(st._account), help_string="Switch (Saklar)")
		log_bar.AddSimpleButton(ID_LOG, "Log (log)", wx.Bitmap(st._log), help_string="Log (Log)")
		#self.play_bar.AddSimpleButton(ID_PLAY, "Start (Mulai)", wx.Bitmap(st._play), help_string="Play")
		self.stop_bar.AddSimpleButton(ID_STOP, "Control (Kontrol Penjadwalan)", wx.Bitmap(st._stop), help_string="Control (Kontrol Penjadwalan)")

		help_bar.AddSimpleButton(ID_HELP, "Help (Bantuan)", wx.Bitmap(st._help), help_string="Help")
		about_bar.AddSimpleButton(ID_ABOUT, "About (Tentang)", wx.Bitmap(st._about), help_string="About")

		lamp_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnLamp, id=ID_LAMP)
		schedule_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnSchedule, id=ID_SCHEDULE)
		scheduler_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnScheduler, id=ID_SCHEDULER)
		monitoring_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnMonitoring, id=ID_MONITORING)

		account_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnAccount, id=ID_ACCOUNT)
		log_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnLog, id=ID_LOG)
		#self.play_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnPlay, id=ID_PLAY)
		self.stop_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnStop, id=ID_STOP)

		help_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnHelp, id=ID_HELP)
		about_bar.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.OnAbout, id=ID_ABOUT)
		
		#close event
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

		self._ribbon.Realize()
		panel = PanelUtama(self)
		s = wx.BoxSizer(wx.VERTICAL)
		s.Add(self._ribbon, 1, wx.EXPAND| wx.GROW)
		s.Add(panel, 3, wx.EXPAND| wx.GROW)
		self.SetSizer(s)
		#self.koneksi()
		if self.koneksi() == False:
			exit()
		else:
			ser = self.sambung()
			self.thread = threading.Thread(target= self.stream)
			self.thread.start()
			self.api.update_status('[%s] Start Listening' % (time.strftime("%Y-%m-%d  %H:%M:%S")))
			saklar.ser = self.ser
			control.ser = self.ser
			Publisher.sendMessage(ser, 'SERIAL')

	def sambung(self):		
		locations=['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3','/dev/ttyACM4', '/dev/ttyACM5','/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3', '/dev/ttyUSB4', '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7', '/dev/ttyUSB8', '/dev/ttyUSB9', '/dev/ttyUSB10','/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9', 'com10', 'com11', 'com12', 'com13', 'com14', 'com15', 'com16', 'com17', 'com18', 'com19', 'com20', 'com21', 'com1', 'end']
		for device in locations:
			try:
				print device
				self.ser = serial.Serial(device, 9600)
				return self.ser
				break
			except:
				if device == 'end':
					wx.MessageDialog(self, 'arduino tidak terpasang ', 'Informasi', wx.ICON_INFORMATION).ShowModal()
					exit()
					
	def koneksi(self):
		try:
			auth = tweepy.OAuthHandler(CK, CS)
			auth.set_access_token(AT, ATS)
			self.api = tweepy.API(auth)
			#print self.api.me().name
			return True
		except tweepy.error.TweepError:
			wx.MessageDialog(self, 'Tidak ada sambungan internet ', 'Informasi', wx.ICON_INFORMATION).ShowModal()
			return False		

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
		
	def OnStop(self, event):
		win = control.Control(self, -1)
		win.Show()
		win.Center()
		
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

	def OnCloseWindow(self, event):
		tanya = wx.MessageDialog(None, "Penjadwalan dan kontrol lampu akan diputuskan, Yakin akan keluar?", "Konfirmasi", wx.YES_NO|wx.ICON_QUESTION)
		retCode = tanya.ShowModal()
		if (retCode == wx.ID_YES):
			quit = True
			data = self.db.fetch_all("SELECT pin,status from lampu")
			for x in data:
				if x[1] == 'on':
					try:
						self.ser.write(str(x[0]))
						self._update_lampu(x[0])
					except:
						print 'failed'
				else:
					pass
			jobs = self.db.fetch_field("SELECT status_jadwal from penjadwalan")
			if 'Running' in jobs:
				self.db.update_db("UPDATE penjadwalan set status_jadwal='Off'")
				self.api.update_status('[%s] System terminated' % (time.strftime("%Y-%m-%d  %H:%M:%S")))
				self.Destroy()
				
			else:
				self.api.update_status('[%s] System terminated' % (time.strftime("%Y-%m-%d  %H:%M:%S")))
				self.Destroy()
			self.ser = None
			ser = None
									
		else:
			pass

	def _update_lampu(self,pin):
		self.db.update_db("UPDATE lampu set status='off' WHERE pin='%s'" % (pin))

	def update_status(self,idlampu,status):
		self.db.update_db("UPDATE lampu set status='%s' WHERE id_lampu='%s'" % (status,idlampu))

	def isi_log(self,idlampu,switch):
		asal = 'Twitter'
		tanggal = datetime.now().strftime('%Y-%m-%d')
		waktu = time.strftime('%H:%M:%S')
		self.db.commit_db("INSERT INTO log VALUES('%s','%s','%s','%s','%s')" % (tanggal,waktu,idlampu,switch,asal))

############################################## Twitter ############################################################
	def stream(self):
		lastStatusProcessed = None
		friends = self.api.friends_ids()
		print friends
		while quit == False:
			for mention in tweepy.Cursor(self.api.mentions, since_id=lastStatusProcessed).items(20):
				if lastStatusProcessed is None:
					print 'mention id :', mention.id
					print 'author :' , mention.author.screen_name
					lastStatusProcessed = mention.id
				#break
				if mention.id > lastStatusProcessed:
					lastStatusProcessed = mention.id
					print mention.author.id
					if mention.author.id not in friends:
						self.api.update_status('@'+mention.author.screen_name + ' [%s] you are not allowed to access ' % (time.strftime("%Y-%m-%d %H:%M:%S")))
					else:
						if mention.text == '':
							self.api.update_status('@'+mention.author.screen_name + ' [%s] error command ' % (time.strftime("%Y-%m-%d %H:%M:%S")))
						else:
							msg = mention.text.lower()
							msg = msg.replace('@tweetduno ','')
							msg = msg.replace('&amp;', '&')
							self.process_text(self.api, mention.author.screen_name, msg)
			time.sleep(30)

############## proses text
	def process_text(self, api, author, text):
		command = text.split(" ")
		if command[0] == 'set':
			msg = text.replace('set ','')
			#print 'hilang kan set',msg
			commands = msg.split('& ')
			#print commands
			for x in commands:
				#print x
				self.set_exec(api, author, x)
		elif command[0] == 'status':
			msg = text.replace('status ','')
			#print 'hilang kan status',msg
			commands = msg.split('& ')
			#print commands
			for x in commands:
				#print x
				self.status_exec(api, author, x)
		else:
			#print 'bukan set atau status'
			api.update_status('@'+author + ' [%s] error command ' % (time.strftime("%Y-%m-%d %H:%M:%S")))

############# set exec
	def set_exec(self, api, author, command):
		command = command.split(" ")
		n = len(command)
		#print 'isi command',n
		if n < 3 or n > 3 == True:
			#print 'kurang dari 3 atau lebih'
			api.update_status('@'+author+'[%s] error command ' % (time.strftime("%Y-%m-%d  %H:%M:%S")))
		else:		
			if command[0] == "lamp":
				lampu = self.db.fetch_field("SELECT id_lampu from lampu")
				print lampu
				if command[1] in lampu:
					idlampu = command[1]
					switch = command[2]
					pin = self.db.fetch_one("SELECT pin from lampu WHERE id_lampu='%s'" %(idlampu))
					status = self.db.fetch_one("SELECT status from lampu WHERE id_lampu='%s'"%(idlampu))
					#print status
					if switch == 'on':
						if status[0] == switch:
							api.update_status('@'+author+'[%s] Lamp [%s] still on' % (time.strftime('%Y-%m-%d %H-%M-%S'), idlampu))
						else:
							self.ser.write(str(pin[0]))
							self.isi_log(idlampu,switch)
							self.update_status(idlampu,switch)
							msg = '[%s] Success Turning %s lamp %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), switch, idlampu)
							#print msg
							api.send_direct_message(screen_name=author, text=msg)

					elif switch == 'off':
						if status[0] == switch:
							api.update_status('@'+author+'[%s] Lamp [%s] still off' % (time.strftime('%Y-%m-%d %H-%M-%S'), idlampu))
						else:
							self.ser.write(str(pin[0]))
							self.isi_log(idlampu,switch)
							self.update_status(idlampu,switch)
							msg = '[%s] Success Turning %s lamp %s' % (time.strftime("%Y-%m-%d %H:%M:%S"),switch,idlampu)
							#print msg
							api.send_direct_message(screen_name=author, text=msg)
					else:
						#print 'bukan on atau off'
						api.update_status('@'+author+'[%s] Command error ' % (time.strftime('%Y-%m-%d %H-%M-%S')))

				elif command[1] == 'all':
					self.set_all(api, author, command[2])
				else:
					#print 'bukan idlamp dan bukan all'
					api.update_status('@'+author+'[%s] Command error ' % (time.strftime('%Y-%m-%d %H-%M-%S')))
			else:
				#print 'bukan lamp'
				api.update_status('@'+author+'[%s] Command error ' % (time.strftime('%Y-%m-%d %H-%M-%S')))

########## status exec
	def status_exec(self, api, author, command):
		idlampu = self.db.fetch_field("SELECT id_lampu from lampu")
		data = self.db.fetch_all("SELECT id_lampu,status from lampu")
		command = command.split(" ")
		n = len(command)
		#print 'n =',n
		if n < 2 or n > 2 == True:
			#print 'kurang dari 2 atau lebih dari 2'
			api.update_status('@'+author + '[%s] error command' % (time.strftime("%Y-%m-%d %H:%M:%S")))
		else:
			if command[0] == 'lamp':
				if command[1] == 'all':
					for x in data:
						lampu = x[0]
						status = x[1]
						msg = '[%s] Status Lamp %s ' % (time.strftime("%Y-%m-%d %H:%M:%S"),lampu)+' '+status
						#print msg
						api.send_direct_message(screen_name=author, text=msg)
					
				elif command[1] in idlampu:
					lamp_num = command[1]
					status = self.db.fetch_one("SELECT status from lampu WHERE id_lampu='%s'" % (lamp_num))
					msg = '[%s] Status Lamp %s' % (time.strftime("%Y-%m-%d %H:%M:%S"),lamp_num)+' ' + status[0]
					#print msg
					api.send_direct_message(screen_name=author, text=msg)

				else:
					api.update_status('@'+author + ' %s error command' % (time.strftime("%Y-%m-%d %H:%M:%S")))
			else:
				api.update_status('@'+author + ' %s error command' % (time.strftime("%Y-%m-%d %H:%M:%S")))
		
	def set_all(self, api, author, switch):
		data = self.db.fetch_all("SELECT id_lampu,pin,status from lampu")
		for x in data:
			#print 'lampu yang ke ',x[0]
			if x[2] == switch:
				api.update_status('@'+author+'[%s] Lamp %s still %s'  % (time.strftime('%Y-%m-%d %H-%M-%S'), x[0], switch))
			else:
				self.ser.write(str(x[1]))
				self.isi_log(x[1],switch)
				msg = '[%s] Success Turning %s lamp %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), switch, x[0])
				#print msg
				self.update_status(x[0],switch)
				api.send_direct_message(screen_name=author, text=msg)


if __name__ == '__main__':
	app = wx.PySimpleApp()
	parent = RibbonFrame()
	parent.Show(True)
	parent.Center()
	app.MainLoop()
