import machine

#UART allows communication between Pico and modules
from machine import UART
import time

gsm = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1)) 


run = True

#counter variable
i = 0


loop for testing
while run == True:
    
       #increment counter variable
    i = i+1
    
    data = gsm.read()
    
    #helps to separate data
    print("-----------------------------")
    print(i+1, "\n" , data)
    print("-----------------------------")
    
    #leaves a gap between data 
    time.sleep(1.0)



