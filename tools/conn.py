import serial
import time
class conn:
    def __init__(self):
        locations=['/dev/ttyS0','/dev/ttyACM0','/dev/ttyS1','/dev/ttyS2','/dev/ttyS3']
        
        for device in locations:
            try:
                #print "Trying ...",device
                arduino = serial.Serial(device,9600)
                self.value = device
                
                break
            except:
                #print "failed to connect on",device
                None
    
    def get_device(self):
        return self.value
    
device = conn()
arduino = conn.get_device()
'''
            try:
                arduino.write('Y')
                time.sleep(1)
                print arduino.readline()
            except:
                print "failed to send"
        
c=conn()
print c.value
'''
    
