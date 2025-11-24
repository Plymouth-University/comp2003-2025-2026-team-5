import machine
from machine import UART
import time

#define GPS variable, UART pins
gps = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5)) 

run = True

#counter variable
i = 0

#loop for testing
while run == True:
    
   #increment counter variable
    i = i+1
    
    data = gps.read()
    print("-----------------------------")
    print(i+1, "\n" , data)
    print("-----------------------------")
    time.sleep(1.0)
    