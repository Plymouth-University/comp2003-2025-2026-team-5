#imports
import socket
import time
import random
import sys

#connection variables
HOST = "127.0.0.1"
PORT = 50000

'''
nmea_sentences = [
    
    b'$GNGGA,,,,,,0,00,25.5,,,,,,*64\r\n$GNGLL,,,,,,V,N*7A\r\n$GNGSA,A,1,,,,,,,,,,,,,25.5,25.5,25.5,1*01\r\n$GNGSA,A,1,,,,,,,,,,,,,25.5,25.5,25.5,4*04\r\n$GPGSV,1,1,00,0*65\r\n$BDGSV,1,1,00,0*74\r\n$GNRMC,,V,,,,,,,,,,N,V*37\r\n$GNVTG,,,,,,,,,N*2E\r\n$GNZDA,,,,,,*56\r\n$GPTXT,01,01,01,ANTENNA OK*35\r\n$GNGGA,,,,,,0,00,25.5,,,,,,*64\r\n$GNGLL,,,,,,V,N*7A\r\n$GNGSA,A,1,,,,,,,,,,,,,25.5,25.5,25.5,1*01\r\n$GNGSA,A,1,,,,,,,,,,,,,25.5,25.5,25.5,4*04\r\n$GPGSV,1,1,00,0*65\r\n$BDGSV,1,1,00,0*74\r\n$GNRMC,,V,,,,,,,,,,N,V*37\r\n$GNVTG,,,,,,,,,N*2E\r\n$GNZDA,,',
    b'$GPTXT,01,01,01,ANTENNA OK*35\r\n$GNGGA,,,,,,0,00,25.5,,,,,,*64\r\n$GNGLL,,,,,,V,N*7A\r\n$GNGSA,A,1,,,,,,,,,,,,,25.5,25.5,25.5,1*01\r\n$GNGSA,A,1,,,,,,,,,,,,,25.5,25.5,25.5,4*04\r\n$GPGSV,1,1,00,0*65\r\n$BDGSV,1,1,00,0*74\r\n$GNRMC,,V,,,,,,,,,,N,V*37\r\n$GNVTG,,,,,,,,,N*2E\r\n$GNZDA,,,,,,*56\r\n$GPTXT,01,01,01,ANTENNA OK*35\r\n',
    b'$GNGGA,,,,,,0,00,25.5,,,,,,*64\r\n$GNGLL,,,,,,V,N*7A\r\n$GNGSA,A,1,,,,,,,,,,,,,25.5,25.5,25.5,1*01\r\n$GNGSA,A,1,,,,,,,,,,,,,25.5,25.5,25.5,4*04\r\n$GPGSV,1,1,00,0*65\r\n$BDGSV,1,1,00,0*74\r\n$GNRMC,,V,,,,,,,,,,N,V*37\r\n$GNVTG,,,,,,,,,N*2E\r\n$GNZDA,,,,,,*56\r\n$GPTXT,01,01,01,ANTENNA OK*35\r\n'
    
]
'''

#creates socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    '''
    #original code which sent NMEA sentences, will be reused after testing
    
    for sentence in nmea_sentences:
        s.sendall((sentence + "\r\n").encode())
        time.sleep(1)
    '''

    #data transmission loop control variable
    #sendData = True

    #keeps sending data until interrupted manually from command line
    #while sendData == True:

    #sys.argv[1] defines number of times to send data, useful for testing and removes need for manual interruption
    for i in range(int(sys.argv[1])):

        #generates a random number
        sentence = random.randint(100,200)

        #converts integer to string for formatting
        sentence = str(sentence)

        #sends data with formmatting
        s.sendall((sentence + "\r\n").encode())

        #waits for specified amount of time
        time.sleep(float(sys.argv[2]))

        #resets sentence variable to make sure number is different each time
        sentence = ''
