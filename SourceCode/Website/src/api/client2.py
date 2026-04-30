#imports
import socket
import time

#connection variables
HOST = "127.0.0.1"
PORT = 5000

DeviceID = "550e8400-e29b-41d4-a716-446655440000"

cgnsinf_sentences = [
    
    b'AT+CGNSINF\r\r\n+CGNSINF: 1,1,20260313153133.000,50.374988,-4.139735,71.736,4.13,319.5,1,,0.6,0.9,0.7,,12,17,9,,48,,\r\n\r\nOK',
    b'AT+CGNSINF\r\r\n+CGNSINF: 1,1,20260313153302.000,50.375569,-4.139002,49.870,4.54,123.6,1,,0.6,0.9,0.7,,12,18,8,,47,,\r\n\r\nOK',
    b'AT+CGNSINF\r\r\n+CGNSINF: 1,1,20260313153409.000,50.374879,-4.139046,46.775,0.00,211.9,1,,0.6,0.9,0.7,,12,18,8,,48,,\r\n\r\nOK',
    b'AT+CGNSINF\r\r\n+CGNSINF: 1,1,20260313153600.000,50.374438,-4.139098,50.758,0.00,106.1,1,,0.7,1.0,0.7,,13,15,8,,45,,\r\n\r\nOK'

]

#creates socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    time.sleep(1.0)

    for i in range(3):

        #send each sentence
        for sentence in cgnsinf_sentences:
            
            full_sentence = sentence + f"\r\n+DEVICEID:{DeviceID}".encode()
            
            #sends data
            s.sendall(full_sentence)

            #waits for specified amount of time
            time.sleep(1.0)

            #clear sentence variable
            sentence = ''


