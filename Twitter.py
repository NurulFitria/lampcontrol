import tweepy
import time
import serial

CK = "GJOnLjmLfAGrg5qgO7Cqg"
CS = "3gNrz7B4pxQjSIbY81xUC61O9biIhYx15XJwzDpHbw"
AT = "719356627-TLd9WqTD0SmGhkgRg9NSXt79oGnj7zSXgLcXS3Fk"
ATS = "2LyqArOBeVpVYKHjjNtEhWYxBOwJwj77VENaR8N7Ls0"
status = ["Off", "Off", "Off","Off"]
pins = ["1","2","3","4"]
#ser = serial.Serial('/dev/ttyACM0', 9600) #connect arduino

# Initialize the tweepy API
auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, ATS)
api = tweepy.API(auth)

print "Start listening at " + time.strftime("%Y-%m-%d %H:%M:%S")
#print
class twit(object):
	def __init__(self):
		pass
	def set_exec(self, api,author,command):
		command = command.split(" ")
		if command[0] == "lamp":
			if command[1] not in pins or command[1] != 'all':
				api.update_status('@'+author + ' %s error command, after command lamp '
									'must digit ' % (time.strftime("%Y-%m-%d %H:%M:%S")))				
			elif command[1] == 'all':
                                                            switch = command[2]
                			 if switch == 'on':
                        			for x in status:
                           				 if x == 'On'
                                				api.update_status('@'+author + ' [%s] Lamp [%s] still on' % (time.strftime("%Y-%m%d %H:%M:%S"),lamp_num))
                           				 else:
                                				msg = '[%s] Turning %s Lamp %s' % (time.strftime("%Y-%m-%d %H:%M:%S"),switch,lamp_num)
                               		                                         api.send_direct_message(screen_name=author,text=msg)
                    		elif switch == 'off':
                        			for x in status:
                           				 if x == 'Off'
                                				api.update_status('@'+author + ' [%s] Lamp [%s] still on' % (time.strftime("%Y-%m%d %H:%M:%S"),lamp_num))
                                        else:
                                			msg = '[%s] Turning %s Lamp %s' % (time.strftime("%Y-%m-%d %H:%M:%S"),switch,lamp_num)
                                            api.send_direct_message(screen_name=author,text=msg)
                    		else:
                        			api.update_status('@'+author + ' %s error command' % (time.strftime("%Y-%m-%d %H:%M:%S")))
            		elif command[1] in pins:
                    		#for x in command:
                    		lamp_num = command[1]
                    		switch = command[2]
                    		index = int(lamp_num)
                    		if switch == "on":
                        			if status[index-1] == "On":
                            				api.update_status('@'+author + ' [%s] Lamp [%s] still on' % (time.strftime("%Y-%m%d %H:%M:%S"),lamp_num))
                        			else:
                            				#ser.write(lamp_num)
                    		elif switch == "off":
                       			 if status[index-1] == "Off":
                            				api.update_status('@'+author + ' [%s] Lamp [%s] still off' % (time.strftime("%Y-%m%d %H:%M:%S"),lamp_num))
                        			else:
                            				#ser.write(lamp_num)
                    		else:
                        			api.update_status('@'+author + ' [%s] error command after code lamp, use on or '
                                            		'off to switch the lamp ' % (time.strftime("%Y-%m%d %H:%M:%S")))
                    			msg = '[%s] Turning %s Lamp %s' % (time.strftime("%Y-%m-%d %H:%M:%S"),switch,lamp_num)
                    			print msg
                    			api.send_direct_message(screen_name=author,text=msg)
			
			else:
				api.update_status('@'+author + ' [%s] error command '% (time.strftime("%Y-%m-%d %H:%M:%S")))
				#ser.write(lamp_num)
	
	def status_exec(self, api,author,command):
		command = command.split(" ")
		print command
		if command[0] == 'lamp':
			if command[1] == 'all':
				msg = '[%s] Status Lamp 1'% (time.strftime("%Y-%m-%d %H:%M:%S"))+' '+status[0]+' '+'Lamp 2'+' '+status[1]+' '+'Lamp 3'+' '+status[2]+' '+'Lamp 4'+' '+status[3]
				api.send_direct_message(screen_name=author,text=msg)
				print msg
			elif command[1] in pins:
				for x in command:
					lamp_num = command[1]
					index = int(lamp_num)
				msg = '[%s] Status Lamp %s' % (time.strftime("%Y-%m-%d %H:%M:%S"),lamp_num)+' ' + status[index-1]
				print msg
				api.send_direct_message(screen_name=author,text=msg)
			else:
				api.update_status('@'+author + ' %s error command, after command lamp '
									'must digit ' % (time.strftime("%Y-%m-%d %H:%M:%S")))
		else:
			api.update_status('@'+author + ' [%s] error command, check your format request .'
								'ex: status lamp lamp_number ' % (time.strftime("%Y-%m-%d %H:%M:%S")))
		


	def process_text(self, api, author, text):
		print '*****************************'
		command = text.split(" ")
		if command[0] == 'set':
			command = self.reformat(text,'set ')
			command = command.split('& ')
			print 'proces text:',command
			for x in command:
				self.set_exec(api,author,x)
		elif command[0] == 'status':
			command = self.reformat(text,'status ')
			command = command.split('& ')
			print 'proces text:',command
			for x in command:
				self.status_exec(api,author,x)
		else:
			api.update_status('@'+author + ' [%s] error command, using (set lamp lamp_code on/off) to switch lamp '
							'or (status lamp lamp_code) to check lamp status ' % (time.strftime("%Y-%m-%d %H:%M:%S")))

	def reformat(self,command,string):
		if command.startswith(string):
			command = command[len(string):]
			return command
		else:
			print 'Not Found'
								
	def main(self):
		quit = False
		lastStatusProcessed = None	
		while True:	
			#get mention
			for mention in tweepy.Cursor(api.mentions, since_id=lastStatusProcessed).items(20):
				if lastStatusProcessed is None:
					print 'mention id :', mention.id
					print 'author :' , mention.author.screen_name
					lastStatusProcessed = mention.id
					break
				
				if mention.id > lastStatusProcessed:
					lastStatusProcessed = mention.id
					print 'mention id :', mention.id
					msg = self.reformat(mention.text,'@TweetDuno ')
					msg = msg.lower()
					msg = msg.replace('&amp;','&')
					print 'message :', msg
					print 'author :', mention.author.screen_name
					self.process_text(api,mention.author.screen_name, msg)
					
				
			time.sleep(30) # We have a limit of calls to Twitter per hour
		api.update_status('Bye! ' + time.strftime("%Y-%m-%d %H:%M:%S"))
		print "Bye!"
