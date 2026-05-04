import socket
import json
import time
import sys
import os

#calls custom utinyec implementation from lib directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from utinyec import registry
from utinyec.ec import Point
from crypto_ecdh_ascon import gen_ecdh, compute_shared, derive, ascon_encrypt


SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

#fake gps coordinates generator
def generate_gps():

    base_lat = 50.3741
    base_lon = -4.1385

    return (
        base_lat + (os.urandom(1)[0] - 128) / 5000,
        base_lon + (os.urandom(1)[0] - 128) / 5000
    )

#connect to the server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))

print("connected")

#receive server private key
server_pub = None

#generate keys
device_priv, device_pub = gen_ecdh()

buffer = ""

def recv_line():
    
    global buffer
    
    while "\n" not in buffer:
    
        buffer += sock.recv(1024).decode("utf-8", "ignore")

    line, buffer = buffer.split("\n", 1)
    return line.strip()


#receive keys from server
line = recv_line()
server_obj = json.loads(line)

#calculate server public key
server_pub = Point(
    
    registry.get_curve("secp256r1"),
    int(server_obj["srv_pub_x"]),
    int(server_obj["srv_pub_y"])

)

print("got server pubkey")


#simulatiom
while True:

    #generate new coordinates
    lat, lon = generate_gps()

    #simulate real CGNSINF sentence
    sentence = f"+CGNSINF: 1,1,20260421120000,{lat:.6f},{lon:.6f},0.0"

    #calculate shared key
    shared = compute_shared(device_priv, server_pub)
    key, _ = derive(shared)

    #generate nonce
    nonce = os.urandom(16)

    #encrypt
    ct, tag = ascon_encrypt(key, nonce, sentence.encode())

    #generate payload
    payload = {
        "dev_pub_x": device_pub.x,
        "dev_pub_y": device_pub.y,
        "nonce": nonce.hex(),
        "ciphertext": ct.hex(),
        "tag": tag.hex()
    }

    #send
    sock.send((json.dumps(payload) + "\n").encode())

    print("sent:", sentence)

    time.sleep(3)