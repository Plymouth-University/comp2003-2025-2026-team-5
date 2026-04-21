try:
    import uhashlib as hashlib
except:
    import hashlib

try:
    import urandom
    def randbytes(n):
        return bytes([urandom.getrandbits(8) for _ in range(n)])
except:
    import os
    def randbytes(n):
        return os.urandom(n)

from utinyec import registry

curve = registry.get_curve('secp256r1')

#Ascon

MASK64 = 0xFFFFFFFFFFFFFFFF

def rotr(x,n):
    return ((x >> n) | (x << (64-n))) & MASK64

def permutation(st, rounds):
    RC = [0xF0,0xE1,0xD2,0xC3,0xB4,0xA5,0x96,0x87,0x78,0x69,0x5A,0x4B]

    for i in range(12-rounds,12):
        st[2] ^= RC[i]

        x0,x1,x2,x3,x4 = st

        x0 ^= x4; x4 ^= x3; x2 ^= x1

        t0 = (~x0)&x1
        t1 = (~x1)&x2
        t2 = (~x2)&x3
        t3 = (~x3)&x4
        t4 = (~x4)&x0

        x0 ^= t1; x1 ^= t2
        x2 ^= t3; x3 ^= t4; x4 ^= t0

        x1 ^= x0
        x0 ^= x4; x3 ^= x2
        x2 = ~x2 & MASK64

        st[0] = x0 ^ rotr(x0,19) ^ rotr(x0,28)
        st[1] = x1 ^ rotr(x1,61) ^ rotr(x1,39)
        st[2] = x2 ^ rotr(x2,1) ^ rotr(x2,6)
        st[3] = x3 ^ rotr(x3,10) ^ rotr(x3,17)
        st[4] = x4 ^ rotr(x4,7) ^ rotr(x4,41)

    return st

def b2u(b):
    return int.from_bytes(b.ljust(8, b"\x00"), "big")
  
def pad(x):
    return x + b'\x80' + b'\x00'*(7-len(x))
  
def u2b(x):
    return x.to_bytes(8,"big")


#encryption and decryption

def ascon_encrypt(key,nonce,pt):
    k0 = b2u(key[:8]); k1 = b2u(key[8:])
    n0 = b2u(nonce[:8]); n1 = b2u(nonce[8:])

    st=[0x80400c0600000000,k0,k1,n0,n1]

    permutation(st,12)
    st[3]^=k0; st[4]^=k1
    st[4] ^= 1

    ct = b""
    i=0

    while i+8 <= len(pt):
        st[0] ^= b2u(pt[i:i+8])
        ct += u2b(st[0])
        permutation(st,6)
        i+=8

    last = pt[i:]
    st[0] ^= b2u(pad(last))
    ct += u2b(st[0])[:len(last)]

    st[1]^=k0; st[2]^=k1
    permutation(st,12)
    st[3]^=k0; st[4]^=k1

    return ct , u2b(st[3]) + u2b(st[4])

def ascon_decrypt(key,nonce,ct,tag):
    k0 = b2u(key[:8])
    k1 = b2u(key[8:])

    n0 = b2u(nonce[:8])
    n1 = b2u(nonce[8:])

    st=[0x80400c0600000000,k0,k1,n0,n1]

    permutation(st,12)
    st[3]^=k0; st[4]^=k1
    st[4]^=1

    pt=b""
    i=0

    while i+8 <= len(ct):
        c = b2u(ct[i:i+8])
        p = st[0]^c
        pt += u2b(p)

        st[0] = c
        permutation(st,6)
        i+=8

    last = ct[i:]
    sbytes = u2b(st[0])

    p_last = bytes([sbytes[j]^last[j] for j in range(len(last))])
    pt += p_last

    st[0] ^= b2u(pad(p_last))

    st[1]^=k0; st[2]^=k1
    permutation(st,12)
    st[3]^=k0; st[4]^=k1

    if tag != u2b(st[3])+u2b(st[4]):
        raise ValueError("Authentication failed")

    return pt

def derive(shared_point):
    shared_bytes = shared_point.x.to_bytes(32, "big")

    h = hashlib.sha256()
    h.update(shared_bytes)
    out = h.digest()

    return out[:16], out[16:32]

# Diffe hellmen 

def gen_ecdh():
    priv = int.from_bytes(randbytes(32), "big") % curve.field.n
    pub = priv * curve.g
    return priv, pub

def compute_shared(priv, pub):
    return priv * pub

#APi

def encrypt_message(my_priv, their_pub, msg):
    shared = compute_shared(my_priv, their_pub)

    key, _ = derive(shared)
    nonce = randbytes(16)

    ct, tag = ascon_encrypt(key, nonce, msg)

    return {
        "ciphertext": ct,
        "tag": tag,
        "nonce": nonce,
        "sender_pub": (their_pub.x, their_pub.y) 
    }

def decrypt_message(my_priv, data):
    x, y = data["sender_pub"]
    sender_pub = curve.point_class(x, y, curve)

    shared = compute_shared(my_priv, sender_pub)

    key, _ = derive(shared)

    return ascon_decrypt(
        key,
        data["nonce"],
        data["ciphertext"],
        data["tag"]
    )

