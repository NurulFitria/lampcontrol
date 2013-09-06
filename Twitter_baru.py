import tweepy
import time
import serial

CK = 'GJOnLjmLfAGrg5qgO7Cqg'
CS = "3gNrz7B4pxQjSIbY81xUC61O9biIhYx15XJwzDpHbw"
AT = "719356627-TLd9WqTD0SmGhkgRg9NSXt79oGnj7zSXgLcXS3Fk"
ATS = "2LyqArOBeVpVYKHjjNtEhWYxBOwJwj77VENaR8N7Ls0"
status = ["Off", "Off", "Off","Off"]
pins = ["1","2","3","4"]


auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, ATS)
api = tweepy.API(auth)
quit = False
lastStatusProcessed = None

class twit(object):
	def __init__(self):
		auth = tweepy.OAuthHandler(CK, CS)
		auth.set_access_token(AT, ATS)
		api = tweepy.API(auth)
	
	def set_exec(self, api, author, command):
		command = command.split(" ")
		if command[0] == "lamp":
			if command[1] not in pins or command[1] != 'all':
				api.update_status('@'+author+'[%s] error command ' % (time.strftime("%Y-%m-%d  %H:%M:%S")))
			elif command[1] == 'all':
				self.set_all(api, author, command[2])
			else:
				lamp_num = command[1]
				switch = command[2]
				index = int(lamp_num)
				if switch == 'on':
					if status[index-1] == 'On':
						api.update_status('@'+author+'[%s] Lamp [%s] still on' % (time.strftime('%Y-%m-%d %H-%M-%S'), lamp_num))
					else:
						msg = 'Success Turning %s lamp %s' % (time.strftime("%Y-%m-%d %H:%M:%S"), switch, lamp_num)
						print msg
						api.send_direct_message(screen_name=author, text=msg)
				elif switch == 'off':
					if status[index-1] == 'Off':
						api.update_status('@'+author+'[%s] Lamp [%s] still on' % (time.strftime('%Y-%m-%d %H-%M-%S'), lamp_num))
					else:
						msg = 'Success Turning %s lamp %s' % (time.strftime("%Y-%m-%d %H:%M:%S"),switch,lamp_num)
						print msg
						api.send_direct_message(screen_name=author, text=msg)
				else:
					api.update_status('@'+author+'[%s] Command error ' % (time.strftime('%Y-%m-%d %H-%M-%S')))
		else:
			api.update_status('@'+author+'[%s] Command error ' % (time.strftime('%Y-%m-%d %H-%M-%S')))
		
	def set_all(self, api, author, switch):
		for x in status:
			if x == switch:
				api.update_status('@'+author+'[%s] Lamp still [%s]'  % (time.strftime('%Y-%m-%d %H-%M-%S'), switch))
			else:
				#ser.write()
				print ' Lamp %s %s ' % (x, switch)
	
	def status_exec(self, api, author, command):
		command = command.split(" ")
		if ommand[0] == 'lamp':
			if command[1] == 'all':
				msg = '[%s] Status Lamp 1'% (time.strftime("%Y-%m-%d %H:%M:%S"))+' '+status[0]+' '+'Lamp 2'+' '+status[1]+' '+'Lamp 3'+' '+status[2]+' '+'Lamp 4'+' '+status[3]
				api.send_direct_message(screen_name=author, text=msg)
				print msg
			elif command[1] in pins:
				for x in command:
					lamp_num = command[1]
					index = int(lamp_num)
				msg = '[%s] Status Lamp %s' % (time.strftime("%Y-%m-%d %H:%M:%S"),lamp_num)+' ' + status[index-1]
				print msg
				api.send_direct_message(screen_name=author, text=msg)
			else:
				api.update_status('@'+author + ' %s error command, after command lamp '
							'must digit ' % (time.strftime("%Y-%m-%d %H:%M:%S")))
		else:
			api.update_status('@'+author + ' %s error command, after command lamp '
						'must digit ' % (time.strftime("%Y-%m-%d %H:%M:%S")))

	def process_text(self, api, author, text):
		command = text.split(" ")
		if command[0] == 'set':
			command = self.reformat(text, 'set ')
			command = command.split('& ')
			for x in command:
				self.set_exec(api, author, x)
		elif command[0] == 'status':
			command = self.reformat(text, 'status ')
			command = command.split('& ')
			for x in command:
				self.status_exec(api, author, x)
		else:
			api.update_status('@'+author + ' [%s] error command ' % (time.strftime("%Y-%m-%d %H:%M:%S")))
	
	def reformat(self, command, string):
		if command.starswith(string):
			command = command[len(string):]
			return command
		else:
			pass

	def main(self):
		auth = tweepy.OAuthHandler(CK, CS)
		auth.set_access_token(AT, ATS)
		api = tweepy.API(auth)
		quit = False
		lastStatusProcessed = None
		while True:
			for mention in tweepy.Cursor(api.mentions, since_id=lastStatusProcessed).items(20):
				if lastStatusProcessed is None:
					lastStatusProcessed = mention.id
				break
				if mention.id > lastStatusProcessed:
					msg = msg.lower()
					msg = self.reformat(mention.text, '@tweetduno ')
					msg = msg.replace('&amp;', '&')
					print msg
					print mention.author
					self.process_text(api, mention.author.screen_name, msg)
			time.sleep(30)

