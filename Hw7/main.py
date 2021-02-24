import numpy as np
import math
import binascii
import sympy
import random
import time

import simon
import ECDSA
import sha3

a = -3
b = 0x051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00
# modulus
p = 6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028291115057151
# order
q = 6864797660130609714981900799081393217269435300143305409394463459185543183397655394245057746333217197532963996371363321113864768612440380340372808892707005449
# Generator
x = 0xc6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66
y = 0x11839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650
P = np.array([x, y])
# ephemeral
ekey_n = 758771


def message_signing(msg, a_private):
    # hash using SHA3-512
    msg_hash = sha3.SHA3_512(msg)
    msg_hash = binascii.hexlify(msg_hash)
    msg_hash = int(msg_hash, 16)

    # sign with ECDSA
    R = ECDSA.nP(a, b, p, ekey_n, P)
    xr = pow(a_private * R[0], 1, q)
    n_inverse = pow(ekey_n, -1, q)
    s = ((msg_hash + xr) * n_inverse) % q
    r = R[0]
    # print("The signature (s, r): ")
    # signature = np.array([s,r])
    # print(signature)

    # 521 bit number padded into 66 bytes
    r = (hex(r)[2:]).rjust(132, '0')
    s = (hex(s)[2:]).rjust(132, '0')
    print("Padded Signature:")
    print('r = ', r)
    print('s = ', s)

    # print("Message in hex: {}".format(msg.hex()))
    msg_assembled = r + s + msg.hex()
    print("Assembled signature and message:")
    print(msg_assembled)
    return msg_assembled


def gen_keys():
    seed = int(time.time())
    random.seed(seed)
    private_key = random.getrandbits(256)
    public_key = ECDSA.nP(a, b, p, private_key, P)
    return private_key, public_key


def Encryption(k, msg_assembled):
    # Padding with 0 to fit in the block size
    if len(msg_assembled) % 32 != 0:
        plaintext = msg_assembled.rjust(32 - (len(msg_assembled) % 32) + len(msg_assembled), '0')
    # print("After padding:")
    # print(plaintext)

    ciphertext = ''
    for count in range(0, (len(plaintext) // 32)):
        simon = en_simon.encryption(count + 1)
        m = plaintext[(count * 32):(count * 32) + 32]
        m = int(m, 16)
        cipher = m ^ simon
        ciphertext += hex(cipher)[2:].rjust(32, '0')

        # print(hex(simon)[2:])
        # print(hex(m)[2:])

    return ciphertext


def Decryption(simon_dekey, m_cipher):
    # print(len(m_cipher))

    plaintext = ''
    for count in range(0, (len(m_cipher) // 32)):
        simon = de_simon.encryption(count + 1)
        m = m_cipher[(count * 32):(count * 32) + 32]
        m = int(m, 16)
        plain = m ^ simon
        plaintext += hex(plain)[2:].rjust(32, '0')

    return plaintext


def Bob_de(plaintext_sig, A_public):
    r = int(plaintext_sig[0:132], 16)
    s = int(plaintext_sig[132:132 * 2], 16)
    msg = plaintext_sig[132 * 2:]
    print("After decryption:")
    print(msg)
    print("Extracted signature:")
    print('r = ', hex(r)[2:])
    print('s = ', hex(s)[2:])

    bytes_object = bytes.fromhex(msg)
    output_msg = bytes_object.decode("ASCII")
    print("\nDecrypted original message:")
    print(output_msg)
    output_msg.encode('UTF-8')

    # signature
    h_msg = sha3.SHA3_512(output_msg.encode('UTF-8'))
    h_msg = binascii.hexlify(h_msg)
    h_msg = int(h_msg, 16)
    # print(h_msg)

    # validation:
    sign_check = ECDSA_validation(s, r, p, q, P, A_public, h_msg)
    print("\nPass the valiadation: ")
    print(sign_check)


def ECDSA_validation(s, r, p, q, P, A_public, h_msg):
    w = pow(s, -1, q)
    u_1 = pow(w * h_msg, 1, q)
    u_2 = pow(w * r, 1, q)
    u_1P = ECDSA.nP(a, b, p, u_1, P)
    u2_X = ECDSA.nP(a, b, p, u_2, A_public)
    V = ECDSA.ECCAdd(a, b, p, u_1P, u2_X)

    sign_check = (V[0] == (r % q))
    return sign_check


if __name__ == "__main__":
    msg = b'yliu634'
    print("The original message we want to send:")
    print(msg)

    # 1.2 Setup: create private and public keys
    a_private, A_public = gen_keys()
    b_private, B_public = gen_keys()

    print("The key pair of Alice:")
    print(a_private, A_public)
    print("The key pair of Bob:")
    print(b_private, B_public)

    # Alice part:
    print("\n\nAlice Part:\n")
    # 1.3 Signature
    msg_assembled = message_signing(msg, a_private)

    # 1.4 Key Creation: transient private and public key pair
    x_t_private, X_t_public = gen_keys()

    # calculate k
    xB = ECDSA.nP(a, b, p, x_t_private, B_public)
    k = xB

    # The agreed key is placed in the message as two 66 byte values:
    print("The agreed key k is:")
    print((hex(k[0])[2:]).rjust(132, '0'))
    print((hex(k[1])[2:]).rjust(132, '0'))

    # 1.5 Encryption: Simon
    # Configuration
    block_size = 128
    key_size = 256
    rounds = 72
    key_words = 4
    const_seq = [1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0,
                 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1,
                 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0,
                 1, 1, 1, 0, 1, 1, 1, 1]  # z_4

    # Simon key is bottom 64 bytes of x coordinate of k
    simon_key = hex(k[0])[-64:]
    # print(int(simon_key,16))

    en_simon = simon.Simon(block_size, key_size, rounds, key_words, const_seq, int(simon_key, 16))
    ciphertext = Encryption(k, msg_assembled)
    print("After Simon cipher:")
    print(ciphertext)

    # Padding X to the ciphertext
    X_0 = (hex(X_t_public[0])[2:]).rjust(132, '0')
    X_1 = (hex(X_t_public[1])[2:]).rjust(132, '0')
    AWS = X_0 + X_1 + ciphertext
    print("Final send message: ")
    print(X_0 + X_1 + ciphertext[-len(msg_assembled):])

    # Bob part:
    print("\n\nBob Part:\n")
    # Decryption
    # Extract X and ciphertext
    pub_X_0 = int(AWS[0:132], 16)
    pub_X_1 = int(AWS[132:132 * 2], 16)
    pub_X = np.array([pub_X_0, pub_X_1])
    # print('Extracted X public key:')
    # print(pub_X) 
    m_cipher = AWS[132 * 2:]

    bX = ECDSA.nP(a, b, p, b_private, pub_X)
    k_de = bX
    # print('Calculated agreed key:')
    # print(k_de)
    simon_dekey = hex(k_de[0])[-64:]

    de_simon = simon.Simon(block_size, key_size, rounds, key_words, const_seq, int(simon_dekey, 16))
    plaintext_sig = Decryption(simon_dekey, m_cipher)
    plaintext_sig = plaintext_sig[-len(msg_assembled):]
    print("After Simon decryption:")
    print(plaintext_sig)
    Bob_de(plaintext_sig, A_public)
