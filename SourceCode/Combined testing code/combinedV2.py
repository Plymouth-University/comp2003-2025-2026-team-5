#==============IMPORTS==============#
import machine
from machine import UART
import time

#==============MODULE CONNECTIONS==============#
gsm = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1)) 
gps = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5))

#==============CLASSES==============#

#custom error class for hardware problems
class HardwareError(exception):
    pass

#for issues sending data
class TransmissionError(exception):
    pass

#==============VARIABLES==============#

serverIP = ''
serverPORT = ''

#==============FUNCTIONS==============#

#function to initialise the GSM module before configuring
#it for SMS and TCP/IP transmissions
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

#gps module initialisation
def initialiseGPS(gps):
    
    #avoid initialising multiple times and wasting resources
    success = False
    
    for attempt in range(5):
        
        if success == False:
            
            time.sleep(1)
            
            #response
            if gps.any():
                
                data = gps.readline()
                data = data.decode('utf-8','ignore')
                data = data.strip()
                
                #TODO: change this later
                #this is not a good check
                
                #GNGGA header present
                if "$GNGGA" in data:
                    
                    #quit out of loop
                    print("GPS module initialised")
                    success = True                    
                    return True
    
    #no response
    if success == False:
        
        raise HardwareError("GPS module not responding")
        
        return False

#function to send data
#GSM module should be pre-configured as this function will only
#be called by the functions which configure the GSM mode
def send(data, state):
    
    success = False
    
    #just in case no state is provided
    if state != True or state != False:
        
        raise TransmissionError("Must configure transmission mode before transmission can take place")
    
    
    #TCP/IP 
    if state == True:
        
        #TODO: add code for TCP/IP transmission
        
        success = True
        return True
    
    #SMS
    else if state == False:
        
        #TODO: add code for SMS transmission
        
        success = True
        return True
    
    #data cannot be sent
    if success == False:
        
        return False
    
    
#function to configure GSM module for SMS transmissions
def transmitSMS(gps, gsm):
    
    #variables to store GPS and GSM responses
    GPSdata = ''
    GSMdata = ''
    
    
    
    #check for response from GPS unit before configuring
    if gps.any():
        
        GPSdata = gps.readline()
        GPSdata = GPSdata.decode('utf-8','ignore')
        GPSdata = GPSdata.strip()
        
        send(GPSdata, False)
        

#function to configure the GSM module for TCP/IP transmissions
def transmitTCP(gps, gsm):
    
    #variables to store GPS and GSM responses
    GPSdata = ''
    GSMdata = ''
    
    #check variable, avoids multiple reconnections
    cipstart = False
    
    if cipstart == False:
        
        for attempt in range(5):
            
            #TODO: figure out a way of running env variables in micropython
            
            #starts TCP connection to defined ip using defined port
            gsm.write(b'AT+CIPSTART="TCP","{serverIP}","{serverPORT}",\r\n')
            
            #debug
            print(attempt, "initialising connection to", serverIP, serverPORT)
            
            #wait for response
            time.sleep(1.0)
            
            #read response
            response = gsm.readline()
            
            print(response)
            
            #connection initiated
            if "CONNECT" in response and "OK" in response:
                
                #prevent reconnection attempts
                cipstart = True
                
                print("Connnected to: ", serverIP, serverPORT)
                
            #sleep and then try again
            if cipstart == False:
                
                time.sleep(1.0)
                
                print("Connection attempt failed, retrying")
    
    #only check GPS if TCP/IP connection is successful
    while cipstart == True:
        
        #check for GPS response
        if gps.any():
                
            GPSdata = gps.readline()
            GPSdata = GPSdata.decode('utf-8','ignore')
            GPSdata = GPSdata.strip()
            
            #only send data containing valid positional header
            if "$GNGGA" in GPSdata:
            
                gsm.write(b'AT+CIPSEND\r\n') #open transmission
                
                time.sleep(0.1) #wait for response
                
                gsm.write(GPSdata) #write GPS data
                
                #debug
                print("Sending", GPSdata, "to", serverIP, serverPORT)
                
                gsm.write("0x1a") #end of transmission
                
                time.sleep(0.2)
                
                response = gsm.readline()
                
                if "OK" not in response:
                    
                    raise transmissionError("Server not responding")
                
        else:
            
            #wait for response from GPS module as it can take a moment
            time.sleep(0.2)
    
    #throw error if connection still not initialised
    if cipstart == False:
         
        raise TransmissionError("Could not initiate TCP connection")
    

#main loop
