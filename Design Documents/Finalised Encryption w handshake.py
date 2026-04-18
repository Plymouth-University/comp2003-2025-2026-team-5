import os

# Ascon (unchanged since last alteration)
MASK64 = 0xFFFFFFFFFFFFFFFF

def rotr(x,n):
    return ((x >> n) | (x << (64-n))) & MASK64


def permutation(st, rounds):

    RC = [0xF0,0xE1,0xD2,0xC3,0xB4,0xA5,0x96,0x87,0x78,0x69,0x5A,0x4B]

    for i in range(12-rounds,12):

        st[2] ^= RC[i]

        # Sbox
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

        # Linear diffusion
        st[0] = x0 ^ rotr(x0,19) ^ rotr(x0,28)
        st[1] = x1 ^ rotr(x1,61) ^ rotr(x1,39)
        st[2] = x2 ^ rotr(x2,1) ^ rotr(x2,6)
        st[3] = x3 ^ rotr(x3,10) ^ rotr(x3,17)
        st[4] = x4 ^ rotr(x4,7) ^ rotr(x4,41)

    return st


def b2u(b):
    return int.from_bytes(b.ljust(8, b"\x00"), "big")
    
def u2b(x):
    return x.to_bytes(8,"big")

def pad(x):
    return x + b'\x80' + b'\x00'*(7-len(x))


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


# Diffie-Hellman, ECDSA and Handshake
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization


def derive(shared):
    hk = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ascon-ecdh"
    )
    out = hk.derive(shared)
    return out[:16], out[16:]


def gen_ecdh():
    priv = ec.generate_private_key(ec.SECP256R1())
    return priv, priv.public_key()


def gen_sign():
    p = ec.generate_private_key(ec.SECP256R1())
    return p, p.public_key()


def sign_pub(priv, pub):
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    sig = priv.sign(pub_bytes, ec.ECDSA(hashes.SHA256()))
    return pub_bytes, sig


def check_sig(pub, data, sig):
    try:
        pub.verify(sig, data, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


# API

def encrypt_message(my_ecdh, my_sign, their_pub, msg):

    shared = my_ecdh.exchange(ec.ECDH(), their_pub)
    key, nonce = derive(shared)

    ct, tag = ascon_encrypt(key, nonce, msg)

    pub_bytes, sig = sign_pub(my_sign, my_ecdh.public_key())

    return {
        "ciphertext": ct,
        "tag": tag,
        "sender_pub": pub_bytes,
        "signature": sig
    }


def decrypt_message(my_ecdh, their_sign_pub, data):

    if not check_sig(their_sign_pub, data["sender_pub"], data["signature"]):
        raise ValueError("MITM detected: invalid signature")

    sender_pub = serialization.load_der_public_key(data["sender_pub"])

    shared = my_ecdh.exchange(ec.ECDH(), sender_pub)
    key, nonce = derive(shared)

    return ascon_decrypt(key, nonce, data["ciphertext"], data["tag"])


# Test

if __name__ == "__main__":

    alice_ecdh_priv, alice_ecdh_pub = gen_ecdh()
    bob_ecdh_priv, bob_ecdh_pub = gen_ecdh()

    alice_sign_priv, alice_sign_pub = gen_sign()

    message = b"Secure Location"

    print("Original message:")
    print(message)

    encrypted = encrypt_message(
        alice_ecdh_priv,
        alice_sign_priv,
        bob_ecdh_pub,
        message
    )

    print("\nEncrypted message (ciphertext):")
    print(encrypted["ciphertext"])

    print("\nAuthentication tag:")
    print(encrypted["tag"])

    decrypted = decrypt_message(
        bob_ecdh_priv,
        alice_sign_pub,
        encrypted
    )

    print("\nDecrypted message:")
    print(decrypted)

    print("\n Success:", decrypted == message)
