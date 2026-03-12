#=========IMPORTS=========#
import machine
from machine import UART, Pin
import time
import utime #figure out a way to write this out later

time.sleep(5)

#=========CONSTANTS=========#

#UART connection to board
gsm = machine.UART(0, 115200) 

#PWRKEY (used for turning the board on and off)
pwr_en = 14

led = Pin(25, Pin.OUT)

serverIP = "" #obscured for githu upload
serverPort = 5000

#=========VARIABLES=========#

#loop control variable
run = True

#module status control variable
power = False

#tcp connnection control variable
connected = False

#=========CLASSES=========#

#add error handling classes here later

#=========FUNCTIONS=========#

#toggle device power
def power_on_off():
    
    pwr_key = machine.Pin(pwr_en, machine.Pin.OUT)
    pwr_key.value(1)
    utime.sleep(2)
    pwr_key.value(0)

def clear_buffer():
    while gsm.any():
        gsm.read()

#function to send commands to the module
def sendcmd(command, delay):
    
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
    
    return text

#tcp connection initialiser
def tcp_open(SERVER_IP, SERVER_PORT):
    
    #set bearer paramter on profile 1 - GPRS connection
    sendcmd('AT+SAPBR=3,1,"Contype","GPRS"', 2)
    
    #set bearer apn parameter on profile 1
    sendcmd('AT+SAPBR=3,1,"APN","mobile.o2.co.uk"', 2)
    
    #open bearer
    sendcmd("AT+SAPBR=1,1", 5)
    
    #query bearer
    sendcmd("AT+SAPBR=2,1", 2)
    
    #single connection mode (0 = single connection, 1 = multiple)
    sendcmd("AT+CIPMUX=0", 2)
    
    #start TCP connection with server ip and port
    response = sendcmd(f'AT+CIPSTART="TCP","{SERVER_IP}","{SERVER_PORT}"', 6)
    
    return response

#tcp send command
def tcp_send(message):
    
    sendcmd("AT+CIPSEND",2)
    
    time.sleep(2)
    
    gsm.write(message.encode())
    
    #writes ctrl+z to end writing
    gsm.write(bytes([26]))
    
    #reads buffer for 5 seconds
    sendcmd("",5)

#tcp connection close
def tcp_close():
    
    #close connection
    sendcmd("AT+CIPCLOSE", 2)
    
    #close bearer
    sendcmd("AT+SAPBR=0,1", 2)

#captures coordinates and sends them to the server
#basically the same as send() due to data capture issues
#running send("AT+CGNSINF",2)
def send_coordinates():
    
    #turn onboard LED on
    led.on()
    
    text = ''
    data = b''
    
    #discard buffer before retrieving coordinates
    clear_buffer()
    
    #query GSM module for position
    gsm.write(b'AT+CGNSINF\r\n')
    
    #wait
    time.sleep(2)
    
    timeout = 5
    
    start_time = time.time()
    
    #read entire buffer as data arrives
    while gsm.any() and (time.time() - start_time < timeout):
        
        part = gsm.read(1)
        
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
    
    clear_buffer()
    
    #if there is something to send
    if text:
        
        #send the retrieved data
        tcp_send(text)
    
    led.off()
    
#=========MAIN LOOP=========#

while run == True:

    #keeps trying to turn the module on until it gets a response
    while power == False:
        
        power_on_off()
        
        #reset any carried over connections
        tcp_close()
        
        #send status command
        response = sendcmd("AT",2)
        
        #module alive
        if "OK" in response:
            
            #don't repeat
            power = True
            
            sendcmd("AT+CGNSPWR=1", 1)
        
        #module not turned on
        elif "OK" not in response:
            
            #try turning on again then loop
            power_on_off()
            
            #reset connections
            tcp_close()
    
    #loop to reattempt connection to server over tcp
    while connected == False:
        
        #store response to tcp open function
        tcpCheck = tcp_open(serverIP, serverPort)
    
        if "CONNECT" in tcpCheck and "OK" in tcpCheck or "ALREADY" in tcpCheck:
            
            connected = True
            
        elif "CONNECT" not in tcpCheck or "OK" not in tcpCheck:
            
            tcp_open(serverIP, serverPort)
    
    #loop to send coordinates to the server
    while connected == True:
        
        #TODO: add enccyption
        
        #retrieve and transmit coordinates
        send_coordinates()
        
        #sleep for 10 seconds to avoid buffer overflow
        time.sleep(10)
                
#=========CODE DUMP=========#
        
'''
#sets sms text mode
def text_mode():
    
    send("AT+CMGF=1", 2)

#function for sending text messages
def send_message(number, message):
    
    #sets phone number (must use country codes e.g. +44)
    sendcmd(f'AT+CMGS="{number}"', 2)
    
    #writes the message passed to the function
    gsm.write(message.encode())
    
    #writes ctrl+z to end writing
    gsm.write(bytes([26]))
    
    #reads buffer for 5 seconds
    sendcmd("",5)
'''
    
    
    
    

