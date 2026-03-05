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


def text_mode():
    
    send("AT+CMGF=1", 2)
    
def send_message(number, message):
    
    
    send(f'AT+CMGS="{number}"', 2)
    
    gsm.write(message.encode())
    
    
    gsm.write(bytes([26]))
    
    
    #wait_resp_info(5000) 
    

