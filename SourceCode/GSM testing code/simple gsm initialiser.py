import machine

#UART allows communication between Pico and modules
from machine import UART
import time

#connect to GSM module
gsm = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1)) 


#request SIM status
gsm.write(b'AT+CPIN?\n')
    
time.sleep(5)
    
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
print("\n" , data)
print("-----------------------------")
    
#leaves a gap between data 
time.sleep(1.0)

#switch to full functionality mode
gsm.write(b'AT+CFUN=1\n')
    
time.sleep(5)
    
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
print("\n" , data)
print("-----------------------------")
    
#leaves a gap between data 
time.sleep(1.0)

#check registration status
gsm.write(b'AT+CREG=1\n')
    
time.sleep(5)
    
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
print("\n" , data)
print("-----------------------------")
    
#leaves a gap between data 
time.sleep(1.0)

#automatic operator selection
gsm.write(b'AT+COPS=0\n')
    
time.sleep(5)
    
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
print("\n" , data)
print("-----------------------------")
    
#leaves a gap between data 
time.sleep(1.0)

#signal strength
gsm.write(b'AT+CSQ\n')
    
time.sleep(5)
    
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
print("\n" , data)
print("-----------------------------")
    
#leaves a gap between data 
time.sleep(1.0)

#check registration status
gsm.write(b'AT+CREG?\n')
    
time.sleep(5)
    
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
print("\n" , data)
print("-----------------------------")
    
#leaves a gap between data 
time.sleep(1.0)



