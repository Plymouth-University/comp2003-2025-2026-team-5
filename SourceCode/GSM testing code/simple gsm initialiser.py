#imports
from machine import UART, Pin
import time
import utime

#connect to GSM module
gsm = machine.UART(0, 115200) 

#PWRKEY
pwr_en = 14

#toggle device power
def power_on_off():
    
    pwr_key = machine.Pin(pwr_en, machine.Pin.OUT)
    pwr_key.value(1)
    utime.sleep(2)
    pwr_key.value(0)

#function to send commands to the module
def send(command, delay):
    
    text = ''
    data = b''
    
    #send commands
    gsm.write(command.encode() + b'\r\n')
        
    time.sleep(delay)
    
    #read entire buffer as data arrives
    while gsm.any():
        
        part = gsm.read()
        
        if part:
        
            data += part
        
        #pause for a moment
        time.sleep(0.01)
        
    #only runs if there is a return
    if data:
            
        #decode data and then strip headers
        data = data.decode('utf-8', 'ignore')
        text = data.strip()
        
    #helps to separate data
    print("-----------------------------")
    print("\n" , text)
    print("-----------------------------")

#sets sms text mode
def text_mode():
    
    send("AT+CMGF=1", 2)

#function for sending text messages
def send_message(number, message):
    
    #sets phone number (must use country codes e.g. +44)
    send(f'AT+CMGS="{number}"', 2)
    
    #writes the message passed to the function
    gsm.write(message.encode())
    
    #writes ctrl+z to end writing
    gsm.write(bytes([26]))
    
    #reads buffer for 5 seconds
    send("",5)

#tcp connection initialiser
def tcp_open(SERVER_IP, SERVER_PORT):
    
    #set bearer paramter on profile 1 - GPRS connection
    send('AT+SAPBR=3,1,"Contype","GPRS"', 2)
    
    #set bearer apn parameter on profile 1
    send('AT+SAPBR=3,1,"APN","mobile.o2.co.uk"', 2)
    
    #open bearer
    send("AT+SAPBR=1,1", 5)
    
    #query bearer
    send("AT+SAPBR=2,1", 2)
    
    #single connection mode (0 = single connection, 1 = multiple)
    send("AT+CIPMUX=0", 2)
    
    #start TCP connection with server ip and port
    send(f'AT+CIPSTART="TCP","{SERVER_IP}","{SERVER_PORT}"', 6)

#tcp send command
def tcp_send(message):
    
    send("AT+CIPSEND",2)
    
    time.sleep(2)
    
    gsm.write(message.encode())
    
    #writes ctrl+z to end writing
    gsm.write(bytes([26]))
    
    #reads buffer for 5 seconds
    send("",5)

#tcp connection close
def tcp_close():
    
    send("AT+CIPCLOSE", 2)
    send("AT+SAPBR=0,1", 2)

#captures coordinates and sends them to the server
#basically the same as send() due to data capture issues
#running send("AT+CGNSINF",2)
def retrieve_coordinates():
    
    text = ''
    data = b''
    
    #query GSM module for position
    gsm.write(b'AT+CGNSINF\r\n')
    
    #wait
    time.sleep(2)
    
    #read entire buffer as data arrives
    while gsm.any():
        
        part = gsm.read()
        
        if part:
        
            data += part
        
        #pause
        time.sleep(0.01)
        
    #only runs if there is a return
    if data:
            
        #decode data and then strip headers
        text = data.decode('utf-8', 'ignore').strip()
        
    #debug
    #helps to separate data
    print("-----------------------------")
    print("\n" , text)
    print("-----------------------------")
    
    #if there is something to send
    if text:
        
        #send the retrieved data
        tcp_send(text)
    
    
    
    
    
    