#imports
import socket
import sys

#connection variables

#allows easy connections via public ip
HOST = "0.0.0.0"
PORT = 5000

#listener loop control variable
listen = True

#useful for testing
loopIndex = 0

#creates socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
    s.bind((HOST, PORT))

    #keeps the listener open
    while listen == True:

        s.listen(1)
        
        print("Waiting for connection...")
        
        conn, addr = s.accept()
        
        with conn:
            
            print("Connected:", addr)

            while True:

                loopIndex = loopIndex+1
            
                try:

                    data = conn.recv(1024)

                    #client disconnected
                    if not data:

                        print("Client Disconnected")

                        loopIndex = 0
                        
                        break

                    #prints received data
                    print(loopIndex, "Received:", data.decode(errors="ignore").strip())

                    
                #connection interrupted
                except ConnectionResetError:

                    print("Client disconnected unexpectedly")

                    loopIndex = 0
                    
                
                
                
