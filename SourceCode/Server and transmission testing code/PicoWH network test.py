#imports
import network
import socket
import machine
from machine import UART
import time
import ubinascii #will be usedfor encryption later

#define GPS variable, UART pins
gps = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5)) 

#loop control variable
run = True


#network credentials
SSID = "TP-Link_DCA4" #obscured for GitHub upload
Password = "11276630"

Server_IP = "86.8.24.189" 
Server_PORT = 5000

#connects to provided wifi network
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, Password)

print(">> Attempting wifi connection")

#repeats connection attempt
while not wifi.isconnected():
    time.sleep(0.5)
print(">> Connected:", wifi.ifconfig())

#opens socket
s = socket.socket()
print(">> Attempting server connection")
s.connect((Server_IP, Server_PORT))
print(">> Connected:", Server_IP, Server_PORT)

#loop for sending data
while run == True:
        
    #checks for gps data
    line = gps.readline()
    
    if line:
        
        try:
            
            text = line.decode('ascii').strip()
            print("GPS:", text)
            
            try:
                #send raw GPS output and a newline
                s.send((text + "\n").encode('ascii'))
            
            except Exception as e:
                
                print("Error Sending GPS data:", e)
            
            
        except Exception as e:
            
            print("Error Decoding GPS data:", e)
        
    time.sleep(0.1)





#----------Code dump----------#

'''
#index variable for testing
i = 0

def encrypt_data(data):
    
    try:
        
        dataArray = []
        
        hex_data = ubinascii.hexlify(data)
        
        key = 1765568736
        
        for i in range(len(hex_data)):
            
            dataArray[i] = hex_data[i]*key
            
        return dataArray
    
    except Exception as e:
        
        print("Encryption failed")
        return None
'''  
