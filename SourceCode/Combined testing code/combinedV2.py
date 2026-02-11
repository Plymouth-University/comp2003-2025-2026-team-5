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
def initialiseGSM(gsm):
    
    #only true if each step completes successfully
    success = False
    
    #bool variables for each stage
    ati = False
    cops = False
    creg = False
    
    #keeps retrying
    while success == False:
        
        #check if all stages completed successfully
        if ati == True and cops == True and creg == True:
            
            success = True
        
        if success == False:
            
            #sometimes the module takes a while to boot so make multiple attempts
            for attempt in range(5):
                
                if ati == False:
                
                    print("Attempt ", attempt, " ATI")
                    
                    gsm.write(b'ATI\r\n')
                    
                    #avoid overloading the module and pico memory
                    time.sleep(1)
                    
                    #response
                    if gsm.any:
                        
                        ATIraw = gsm.readline()
                        ATIdata = ATIraw.decode('utf-8','ignore')
                        ATIdata = ATIdata.strip()
                        
                        #success
                        if "OK" in ATIdata:
                            
                            print("GSM module alive")
                            ati = True
                        
                        #failure
                        else:
                            
                            time.sleep(1)
                    
                    #no data
                    else:
                        
                        #retry in 1 second
                        time.sleep(1)
            
            #after attempts check ATI status
            if ati == False:
                
                raise HardwareError("GSM unit not responding")
            
            #network scan to avoid wasting time trying to register if no operators are found
            for attempt in range(5):
                
                if cops == False:
                    
                    print("Attempt", attempt, "COPS")
                    
                    gsm.write(b'AT+COPS\r\n')
                    
                    #takes a while
                    time.sleep(20)
                    
                    if gsm.any:
                        
                        #retrieve cops status
                        COPSraw = gsm.readline()
                        COPSdata = COPSraw.decode('utf-8','ignore')
                        COPSdata = COPSdata.strip()
                        
                        #success
                        if "OK" in COPSdata:
                            
                            print("Network scan complete")
                            cops = True
                        
                        #failure
                        else:
                            
                            time.sleep(1)
                    
                    #no data
                    else:
                        
                        time.sleep(5)
            
            if cops == False:
                
                raise HardwareError("Network scan failed")
            
            #multiple creg attempts            
            for attempt in range(5):
                
                if creg == False:
                    
                    print("Attempt", attempt, "CREG")
                    
                    gsm.write(b'AT+CREG\r\n')
                    
                    time.sleep(15)
                    
                    if gsm.any:
                        
                        CREGraw = gsm.readline()
                        CREGdata = CREGraw.decode('utf-8','ignore')
                        CREGdata = CREGdata.strip()
                    
                    #0,1 = connected to home network
                    #0,5 = roaming
                    #check registration status
                    if "0,1", "0,5" in CREGdata:
                        
                        print("GSM module registered")
                        creg = True
                    
                    #failure
                    else:
                        
                        time.sleep(1)
                
                #no data
                else:
                    
                    time.sleep(1)
            
            #failed
            if creg == False:
                
                raise HardwareError("GSM module not registered")
        
        if success == True:
            
            return True

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