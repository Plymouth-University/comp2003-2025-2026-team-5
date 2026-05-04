from machine import UART, Pin, SPI, PWM
import framebuf
import time
import utime
import json
import sys
import ubinascii
import gc

from crypto_ecdh_ascon import Session, gen_ecdh, compute_shared, derive, ascon_encrypt, curve
from utinyec.ec import Point

time.sleep(5)

#this file is a mess and does not work as intended AT ALL

#=========CONSTANTS=========#

gsm = UART(0, 115200)

pwr_en = 14
led = Pin(25, Pin.OUT)
buttonA = Pin(15, Pin.IN, Pin.PULL_UP)

serverIP = ""
serverPort = 5000

#=========VARIABLES=========#

run = True
power = False
connected = False
emergency = False

device_priv = None
device_pub = None
server_pub = None
session = None



#=========COLOURS=========#
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
        self.cs(1)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(10),mosi=Pin(11),miso=None)
        self.dc = Pin(8,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.Init()
        self.SetWindows(0, 0, self.width-1, self.height-1)

    def reset(self):
        
        self.rst(1); time.sleep(0.2)
        self.rst(0); time.sleep(0.2)
        self.rst(1); time.sleep(0.2)

    def write_cmd(self, cmd):
        
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def backlight(self,value):
        
        pwm = PWM(Pin(13))
        pwm.freq(1000)
        if value>=1000:
            value=1000
        data=int (value*65536/1000)
        pwm.duty_u16(data)

    def Init(self):
        
        self.reset()
        self.backlight(1000)

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
        for v in [0x10,0x0E,0x02,0x03,0x0E,0x07,0x02,0x07,0x0A,0x12,0x27,0x37,0x00,0x0D,0x0E,0x10]:
            self.write_data(v)

        self.write_cmd(0xE1)
        for v in [0x10,0x0E,0x03,0x03,0x0F,0x06,0x02,0x08,0x0A,0x13,0x26,0x36,0x00,0x0D,0x0E,0x10]:
            self.write_data(v)

        self.write_cmd(0x3A)
        self.write_data(0x05)

        self.write_cmd(0x36)
        self.write_data(0xA8)

        self.write_cmd(0x29)

    def SetWindows(self, Xstart, Ystart, Xend, Yend):
        
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

def power_on_off():
    
    pwr_key = Pin(pwr_en, Pin.OUT)
    pwr_key.value(1)
    utime.sleep(2)
    pwr_key.value(0)

def clear_buffer():
    
    deadline = time.time() + 2
    
    while time.time() < deadline:
        
        if gsm.any():
            
            gsm.read()
        
        time.sleep(0.01)

def sendcmd(command, delay):
    text = ''
    data = b''
    
    #make sure commands are only sent if they are provided
    if command:
        
        gsm.write(command.encode() + b'\r\n')
        
    time.sleep(delay)

    while gsm.any():
        part = gsm.read()
        if part:
            data += part
        time.sleep(0.01)

    if data:
        data = data.decode('utf-8', 'ignore')
        text = data.strip()

    print("-----------------------------")
    print("\n", text)
    print("-----------------------------")

    return text

def tcp_open(SERVER_IP, SERVER_PORT):
    
    sendcmd('AT+SAPBR=3,1,"Contype","GPRS"', 2)
    sendcmd('AT+SAPBR=3,1,"APN","mobile.o2.co.uk"', 2)
    sendcmd("AT+SAPBR=1,1", 5)
    sendcmd("AT+SAPBR=2,1", 2)
    sendcmd("AT+CIPMUX=0", 2)

    cmd = 'AT+CIPSTART="TCP","' + SERVER_IP + '","' + str(SERVER_PORT) + '"'
    print("Sending:", cmd)
    
    
    response = sendcmd(cmd, 6)
    #return response

    #gsm.write(cmd.encode() + b'\r\n')
    #time.sleep(2)
    
    #raw = b""
    #while gsm.any():
        #raw += gsm.read()
        #time.sleep(0.01)
    
    #return raw.decode('utf-8', 'ignore').strip()
    
    return response
    
def tcp_send(message):
    #msg_bytes = message.encode()
    #length = len(msg_bytes)
    
    
    #clear_buffer()
    #log("tcp_send: writing cipsend, length = " + str(length))
    #response = sendcmd("AT+CIPSEND", 2)
    #log("tcp_send: CIPSEND response: " + str(response))
    
    #if ">" not in response:
     #   log("tcp_send: no prompt, aborting")
      #  return
    
    #log("tcp_send: writing data")
    #gsm.write(msg_bytes)
    #log("msg written, sending ctrl-z")
    #gsm.write(bytes([26]))
    #log("tcp_send: waiting for response")
    #response2 = sendcmd("", 5)
    #log("tcp_send: modem response: " + str(response2))
    #time.sleep(1)
    
    msg_bytes = message.encode()
    
    clear_buffer()
    
    log("message encoded")
    
    log("entering CIPSEND...")
    gsm.write(("AT+CIPSEND=%d\r\n" % len(msg_bytes)).encode())
    
    buf = b""
    start = time.time()
    while time.time() - start < 5:
        
        if gsm.any():
            
            buf += gsm.read()
            
            if b'>' in buf:
                
                break
            
    log("done" + buf.decode('utf-8', 'ignore'))
    
    if b'>' not in buf:
        log("no > received, aborting")
        return
    
    
    
    log("writing message")
    
    gsm.write(msg_bytes)
    
    gsm.write(bytes([26]))
    
    log("done")
    
    response = b""
    
    start = time.time()
    while time.time() - start < 5:
        
        if gsm.any():
            
            response += gsm.read()
            
    log("send response: " + response.decode('utf-8', 'ignore'))
    
    
    
    
    
    
    
    
  
    
    
    
    
def tcp_close():
    sendcmd("AT+CIPCLOSE", 2)
    sendcmd("AT+SAPBR=0,1", 2)

#required to retrieve server public key
def tcp_readline(timeout=10):
    
    start = time.time()
    buf = b""
    
    while time.time() - start < timeout:
        
        if gsm.any():
            
            chunk = gsm.read()  #read all
            
            if chunk:
                
                buf += chunk
                decoded = buf.decode('utf-8', 'ignore')
                #look for a complete JSON object
                start_i = decoded.find('{')
                end_i = decoded.find('}')
                
                if start_i != -1 and end_i != -1:
                    
                    return decoded[start_i:end_i+1].strip()
        
        time.sleep(0.05)
    return ""

#logging function for debugging purposes, writes events to a txt file
def log(msg):
    
    try:
        
        with open("debug_log.txt", "a") as f:
            
            f.write(str(time.time()) + " | " + str(msg) + "\n")
            
    except:
                
        pass


def send_coordinates():
    
    
    
    try:
        
        #garbage collector clears memory
        gc.collect()
        
        log("FREE MEM: " + str(gc.mem_free()))
        
        
        log("cycle start")
        led.on()
        log("LED turned on")
        
        
        text = ''
        data = b''
        
        time.sleep(1)
        
        
        #reset modem kind of
        sendcmd("AT", 2)
        
        #request GNSS data
        log("about to write GPS cmd")
        gsm.write(b'AT+CGNSINF\r\n')
        log("Requested GPS data")
        time.sleep(2)

        timeout = 5
        start_time = time.time()
        
        
        
        #while time.time() - start_time < timeout:
         #   
          #  if gsm.any():
           #     
            #    chunk = gsm.read()
             #       
              #  if chunk:
               #         
                #    data += chunk
                #
                #else:
                
                 #   time.sleep(0.02)
        while time.time() - start_time < timeout:
            
            if gsm.any():
                
                part = gsm.read()
                
                if part:
                    
                    data += part
                    
                    if b"OK" in data and b"+CGNSINF" in data:
                        
                        break
                    
                    
            time.sleep(0.01)
        
        log("finished reading data")
        
        #while gsm.any() and (time.time() - start_time < timeout):
         #   part = gsm.read(1)
          #  if part:
           #     data += part
            #time.sleep(0.01)

        if data:
            decoded = data.decode('utf-8', 'ignore')
            log("Decoded text:" + decoded)

            #pick only the +CGNSINF line
            for line in decoded.splitlines():
                
                if line.startswith("+CGNSINF:"):
                    
                    text = line.strip()
                    
                    break
           
            else:
                text = ""  #nothing usable

            if emergency and text:
                
                text = text + '\r\n+EMERGENCY'

        print("-----------------------------")
        print("\n", text)
        print("-----------------------------")
        
        
        #clear_buffer()

        #use session keys
        if text and session is not None:
            
            log("Encrypting")
            
            ct, tag, nonce = session.encrypt(text.encode())
            
            log("successfully encrypted")
            
            payload = json.dumps({
                "dev_pub_x": device_pub.x,
                "dev_pub_y": device_pub.y,
                "nonce": ubinascii.hexlify(nonce).decode(),
                "ciphertext": ubinascii.hexlify(ct).decode(),
                "tag": ubinascii.hexlify(tag).decode()
            })
            
            log("json dumps done")
            log("payload legnth: " + str(len(payload)))
            
            log("Payload created")
            
            print("SENDING ENCRYPTED PAYLOAD:", payload)
            
            #status = sendcmd("AT+CIPSTATUS", 2)
            #log("status before send: " + status)
            
            tcp_send(payload + "\n")
            
            log("send attempted")
            gc.collect()
            clear_buffer()
            
            log("Payload send")
            
        led.off()
        
        log("Cycle end")
        
        time.sleep(1)
    
    except Exception as e:
    
        log("ERROR: " + repr(e))
    
    
        

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

    

    while run:

        while power == False:
            power_on_off()
            tcp_close()
            response = sendcmd("AT",2)

            if "OK" in response:
                power = True
                
                gsm.write(bytes([26]))  
                time.sleep(1)
                clear_buffer()
    
                
                
                sendcmd("AT+CGNSPWR=1", 1)
            else:
                power_on_off()
                tcp_close()

        while connected == False:
            tcpCheck = tcp_open(serverIP, serverPort)

            if ("CONNECT" in tcpCheck and "OK" in tcpCheck) or "ALREADY" in tcpCheck:
                connected = True

                #fresh device keypair per connection
                device_priv, device_pub = gen_ecdh()
                server_pub = None
                
                #time.sleep(1)        
                #clear_buffer() 
                
                start_i = tcpCheck.find('{')
                end_i = tcpCheck.find('}')
                
                if start_i != -1 and end_i != -1:
                    
                    try:
                        
                        obj = json.loads(tcpCheck[start_i:end_i+1])
                        server_pub = Point(curve, int(obj["srv_pub_x"]), int(obj["srv_pub_y"]))
                        
                    except:
                        
                        pass
                
                #wait for server public key to arrive
                if server_pub is None:
                    
                    for _ in range(5):
                        
                        line = tcp_readline(15)
                        log("tcp_readline got:" + str(line))
                        
                        if not line:
                            
                            continue
                        
                        try:
                            
                            obj = json.loads(line)
                            server_pub = Point(curve, int(obj["srv_pub_x"]), int(obj["srv_pub_y"]))
                            print("Got server pubkey")
                            break
                        
                        except:
                            
                            print("Skipping non-JSON from server:", line)

                if server_pub is None:
                    
                    print("Failed to get server pubkey, reconnecting")
                    connected = False
                    tcp_close()
                    
                    continue
                
                #session key storage
                session = Session(device_priv, server_pub)

            else:
                
                tcp_open(serverIP, serverPort)
                time.sleep(2)

        while connected == True:
            
            #poll button A
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

            #send
            send_coordinates()

