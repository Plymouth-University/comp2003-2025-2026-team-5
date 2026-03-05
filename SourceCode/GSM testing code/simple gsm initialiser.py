#imports
from machine import UART, Pin
import time
import utime

#connect to GSM module
gsm = machine.UART(0, 115200) 

pwr_en = 14


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

