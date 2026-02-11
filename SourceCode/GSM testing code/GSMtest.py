import machine

#UART allows communication between Pico and modules
from machine import UART
import time

#connect to GSM module
gsm = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1)) 

#loop control
run = True

#counter variable
i = 0

#loop for testing
while run == True:
    
    #increment counter variable
    i = i+1
    
    #request firmware version and device status
    gsm.write(b'AT+CCID\r\n')
    
    #store output in data variable
    data = gsm.read()
    
    #only runs if there is a return
    if data:
        
        #decode data and then strip headers
        text = data.decode('utf-8', 'ignore')
        data = text.strip()
    
    #for testing
    #helps to separate data
    print("-----------------------------")
    print(i+1, "\n" , data)
    print("-----------------------------")
    
    #leaves a gap between data 
    time.sleep(1.0)



