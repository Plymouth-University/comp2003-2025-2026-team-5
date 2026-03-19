MASK64 = 0xFFFFFFFFFFFFFFFF


def rotr(x, n):
    return ((x >> n) | (x << (64 - n))) & MASK64


def permutation(state, rounds):
    RC = [
        0xF0, 0xE1, 0xD2, 0xC3,
        0xB4, 0xA5, 0x96, 0x87,
        0x78, 0x69, 0x5A, 0x4B
    ]

    for i in range(12 - rounds, 12):
       
        state[2] ^= RC[i]

        # Sbox
        x0, x1, x2, x3, x4 = state

        x0 ^= x4
        x4 ^= x3
        x2 ^= x1

        t0 = (~x0) & x1
        t1 = (~x1) & x2
        t2 = (~x2) & x3
        t3 = (~x3) & x4
        t4 = (~x4) & x0

        x0 ^= t1
        x1 ^= t2
        x2 ^= t3
        x3 ^= t4
        x4 ^= t0

        x1 ^= x0
        x0 ^= x4
        x3 ^= x2
        x2 = ~x2 & MASK64

        #Linear diffusion
        state[0] = x0 ^ rotr(x0, 19) ^ rotr(x0, 28)
        state[1] = x1 ^ rotr(x1, 61) ^ rotr(x1, 39)
        state[2] = x2 ^ rotr(x2, 1) ^ rotr(x2, 6)
        state[3] = x3 ^ rotr(x3, 10) ^ rotr(x3, 17)
        state[4] = x4 ^ rotr(x4, 7) ^ rotr(x4, 41)

    return state


def bytes_to_u64(b):
    return int.from_bytes(b.ljust(8, b'\x00'), "big")


def u64_to_bytes(x):
    return x.to_bytes(8, "big")


def pad(block, rate=8):
    pad_len = rate - len(block)
    return block + b'\x80' + b'\x00' * (pad_len - 1)

#Decryption

def ascon_decrypt(key, nonce, ciphertext, tag, ad=b""):
    assert len(key) == 16
    assert len(nonce) == 16

    rate = 8

    k0 = bytes_to_u64(key[:8])
    k1 = bytes_to_u64(key[8:])
    n0 = bytes_to_u64(nonce[:8])
    n1 = bytes_to_u64(nonce[8:])

    IV = 0x80400c0600000000
  
    state = [IV, k0, k1, n0, n1]
    permutation(state, 12)
    state[3] ^= k0
    state[4] ^= k1

  
    if ad:
        i = 0
        while i + rate <= len(ad):
            state[0] ^= bytes_to_u64(ad[i:i+rate])
            permutation(state, 6)
            i += rate

        last = ad[i:]
        state[0] ^= bytes_to_u64(pad(last))
        permutation(state, 6)

    state[4] ^= 1

    plaintext = b""
    i = 0

    while i + rate <= len(ciphertext):
        cblock = bytes_to_u64(ciphertext[i:i+rate])
        pblock = state[0] ^ cblock
        plaintext += u64_to_bytes(pblock)
        state[0] = cblock
        permutation(state, 6)
        i += rate

    last = ciphertext[i:]
    s0_bytes = u64_to_bytes(state[0])
    p_last = bytes([s0_bytes[j] ^ last[j] for j in range(len(last))])
    plaintext += p_last

    padded = pad(p_last)
    state[0] ^= bytes_to_u64(padded)

 
    state[1] ^= k0
    state[2] ^= k1
    permutation(state, 12)
    state[3] ^= k0
    state[4] ^= k1

    calc_tag = u64_to_bytes(state[3]) + u64_to_bytes(state[4])

    if calc_tag != tag:
        raise ValueError("Authentication failed")

    return plaintext
