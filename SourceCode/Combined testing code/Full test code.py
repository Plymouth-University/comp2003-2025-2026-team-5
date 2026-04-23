#=========IMPORTS=========#
from machine import UART, Pin, SPI, PWM
import framebuf
import time
import utime #figure out a way to write this out later
import json
from cryptography import gen_ecdh, encrypt_message, curve
from utinyec.ec import Point

time.sleep(5)

#=========CONSTANTS=========#

#UART connection to board
gsm = machine.UART(0, 115200) 

#PWRKEY (used for turning the board on and off)
pwr_en = 14

led = Pin(25, Pin.OUT)

buttonA = Pin(15, Pin.IN, Pin.PULL_UP)

serverIP = "86.8.24.189"
serverPort = 5000
DeviceID = "patient-1"

#=========VARIABLES=========#

#loop control variable
run = True

#module status control variable
power = False

#tcp connnection control variable
connected = False

#toggle variable for SOS button
emergency = False

device_priv = None
device_pub = None
server_pub = None


#=========CLASSES=========#

#taken from official waveshare code, will be changed later

#color is BGR
RED = 0x00F8
GREEN = 0xE007
BLUE = 0x1F00
WHITE = 0xFFFF
BLACK = 0x0000

class LCD_0inch96(framebuf.FrameBuffer):
    def __init__(self):
    
        self.width = 160
        self.height = 80
        
        self.cs = Pin(9,Pin.OUT)
        self.rst = Pin(12,Pin.OUT)
#        self.bl = Pin(13,Pin.OUT)
        self.cs(1)
        # pwm = PWM(Pin(13))#BL
        # pwm.freq(1000)        
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(10),mosi=Pin(11),miso=None)
        self.dc = Pin(8,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.Init()
        self.SetWindows(0, 0, self.width-1, self.height-1)
        
    def reset(self):
        self.rst(1)
        time.sleep(0.2) 
        self.rst(0)
        time.sleep(0.2)         
        self.rst(1)
        time.sleep(0.2) 
        
    def write_cmd(self, cmd):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))

    def write_data(self, buf):
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def backlight(self,value):#value:  min:0  max:1000
        pwm = PWM(Pin(13))#BL
        pwm.freq(1000)
        if value>=1000:
            value=1000
        data=int (value*65536/1000)       
        pwm.duty_u16(data)  
        
    def Init(self):
        self.reset() 
        self.backlight(10000)  
        
        self.write_cmd(0x11)
        time.sleep(0.12)
        self.write_cmd(0x21) 
        self.write_cmd(0x21) 

        self.write_cmd(0xB1) 
        self.write_data(0x05)
        self.write_data(0x3A)
        self.write_data(0x3A)

        self.write_cmd(0xB2)
        self.write_data(0x05)
        self.write_data(0x3A)
        self.write_data(0x3A)

        self.write_cmd(0xB3) 
        self.write_data(0x05)  
        self.write_data(0x3A)
        self.write_data(0x3A)
        self.write_data(0x05)
        self.write_data(0x3A)
        self.write_data(0x3A)

        self.write_cmd(0xB4)
        self.write_data(0x03)

        self.write_cmd(0xC0)
        self.write_data(0x62)
        self.write_data(0x02)
        self.write_data(0x04)

        self.write_cmd(0xC1)
        self.write_data(0xC0)

        self.write_cmd(0xC2)
        self.write_data(0x0D)
        self.write_data(0x00)

        self.write_cmd(0xC3)
        self.write_data(0x8D)
        self.write_data(0x6A)   

        self.write_cmd(0xC4)
        self.write_data(0x8D) 
        self.write_data(0xEE) 

        self.write_cmd(0xC5)
        self.write_data(0x0E)    

        self.write_cmd(0xE0)
        self.write_data(0x10)
        self.write_data(0x0E)
        self.write_data(0x02)
        self.write_data(0x03)
        self.write_data(0x0E)
        self.write_data(0x07)
        self.write_data(0x02)
        self.write_data(0x07)
        self.write_data(0x0A)
        self.write_data(0x12)
        self.write_data(0x27)
        self.write_data(0x37)
        self.write_data(0x00)
        self.write_data(0x0D)
        self.write_data(0x0E)
        self.write_data(0x10)

        self.write_cmd(0xE1)
        self.write_data(0x10)
        self.write_data(0x0E)
        self.write_data(0x03)
        self.write_data(0x03)
        self.write_data(0x0F)
        self.write_data(0x06)
        self.write_data(0x02)
        self.write_data(0x08)
        self.write_data(0x0A)
        self.write_data(0x13)
        self.write_data(0x26)
        self.write_data(0x36)
        self.write_data(0x00)
        self.write_data(0x0D)
        self.write_data(0x0E)
        self.write_data(0x10)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0x36)
        self.write_data(0xA8)

        self.write_cmd(0x29) 
        
    def SetWindows(self, Xstart, Ystart, Xend, Yend):#example max:0,0,159,79
        Xstart=Xstart+1
        Xend=Xend+1
        Ystart=Ystart+26
        Yend=Yend+26
        self.write_cmd(0x2A)
        self.write_data(0x00)              
        self.write_data(Xstart)      
        self.write_data(0x00)              
        self.write_data(Xend) 

        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(Ystart)
        self.write_data(0x00)
        self.write_data(Yend)

        self.write_cmd(0x2C) 
        
    def display(self):
    
        self.SetWindows(0,0,self.width-1,self.height-1)       
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

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
    cmd = 'AT+CIPSTART="TCP","' + SERVER_IP + '","' + str(SERVER_PORT) + '"'
    print("Sending:", cmd)
    response = sendcmd(cmd, 6)
    
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
        
        #send device ID as well
        text = text + '\r\n +DEVICEID: ' + DeviceID
        
        if emergency == True:
            
            text = text + '\r\n +EMERGENCY'
        
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

if __name__=='__main__':

    lcd = LCD_0inch96()   
    lcd.fill(BLACK)   
    lcd.text("Emergency button -->",35,15,GREEN)
    lcd.text("",50,35,GREEN)    
    lcd.text("Unused button -->",30,55,GREEN)
    lcd.display()
    
    lcd.hline(10,10,140,BLUE)
    lcd.hline(10,70,140,BLUE)
    lcd.vline(10,10,60,BLUE)
    lcd.vline(150,10,60,BLUE)
    
    lcd.hline(0,0,160,BLUE)
    lcd.hline(0,79,160,BLUE)
    lcd.vline(0,0,80,BLUE)
    lcd.vline(159,0,80,BLUE) 
    
    lcd.display()
    time.sleep(3) 




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
                
                time.sleep(2)
        
        #loop to send coordinates to the server
        while connected == True:
            
            #for loop replaces time.sleep(10) in order to make button responsive outside of send cycles
            for i in range(100):
            
                if buttonA.value() == 0 and emergency == False:
                
                    emergency = True
                    
                    while buttonA.value() == 0:
                        
                        pass
                    
                    time.sleep(0.3)
                
                elif buttonA.value() == 0 and emergency == True:
                    
                    emergency = False
                    
                    while buttonA.value() == 0:
                        
                        pass
                    
                    time.sleep(0.3)
                
                time.sleep(0.1)
            
            #TODO: add encryption
            
            #retrieve and transmit coordinates
            send_coordinates()
        
                
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
    
    
    
    


