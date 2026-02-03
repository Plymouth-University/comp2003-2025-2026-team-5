#imports
import machine
from machine import UART
import time

#module connnections
gsm = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1)) 
gps = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5)) 

#classes
class HardwareError(Exception):
    pass

#functions

#status check for GSM unit before proceeding
def initialiseGSM():
    
    try:
        
        #request firmware and status
        gsm.write(b'ATI\r\n')
        
        time.sleep(1.0)
        
        #read response
        data = gsm.read()
        
        if data:
            
            #decode data
            text = data.decode('utf-8', 'ignore')
            data = text.strip()
        
        #GSM module status ok
        if "OK" in data:
            
            #GSM initialised
            return True
        
        #GSM module not responding
        else:
            
            #raise error
            raise HardwareError("GSM unit not responding")
        
    except HardwareError as e:
        
        #output error
        print("GSM unit error: ", e)
        
        #GSM not initialised
        return False

#GPS provides no status check, only data
def getCoords():
    
    try:
        
        line = gps.readline()
        
        if line:
            
            try:
                
                text = line.decode('ascii').strip()
                print("GPS:", text)
                
                return line
                
            except Exception as e:
                
                print("Error Decoding GPS data:", e)
                
                raise HardwareError("Error decoding GPS data")
        
        if !line:
            
            raise HardwareError("GPS Unit Not Responding")
    
    except HardwareError as e:
        
        print("GPS unit error: ", e)
    


#main loop