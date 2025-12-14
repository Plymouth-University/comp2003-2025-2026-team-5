#imports
import network
import socket
import machine
from machine import UART
import time
import ubinascii

#define GPS variable, UART pins
gps = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5)) 

#loop control variable
run = True

#index variable for testing
i = 0

SSID = "" #obscured for GitHub upload
Password = ""

Server_IP = "" 
Server_PORT = 5000

#connects to provided wifi network
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, Password)

print(">> Attempting wifi connection")
while not wifi.isconnected():
    time.sleep(0.5)
print(">> Connected:", wifi.ifconfig())


s = socket.socket()
print(">> Attempting server connection")
s.connect((Server_IP, Server_PORT))
print(">> Connected:", Server_IP, Server_PORT)

def encrypt_data(data):
    
    try:
        
        dataArray = []
        
        hex_data = ubinascii.hexlify(data)
        
        int key = 1765568736
        
        for i in range len(hex_data):
            
            dataArray[i] = hex_data[i]*key
            
        return dataArray
    
    except Exception as e:
        
        print("Encryption failed")
        return None
    
        
    
        


#loop for sending data
while run == True:
        
        #checks for gps data
        if gps.any():
            
            #reads data and stores in data variable
            gpsData = gps.readline()
            
            if gpsData:
                
                
            
                encrypted = encrypt_data(gpsData)
                
                #decodes the data to a readable format and removes spaces at the start of lines
                #sentence = data.decode('utf - 8').strip()
                
                #sends the data
                s.send(i, encrypted)
        
        else:
            
            s.send(">>", i, "Waiting for GPS signal")
        
        time.sleep(1.0)
