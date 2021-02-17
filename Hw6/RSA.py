import numpy as np
import math
import binascii
import sympy


# RSA Encryption
def RSA_en():
    n = 900348238029332668175881559281442423068410198618801978249457479037932527260331
    e = pow(2,16) +1
    msg = 39611541800605679895240898832274013906789

    ciphertext  = pow(msg,e,n)

def RSA_de():
    p = 929960838713976909720407931803976852619
    q = 808840137850295240473898249118645909517
    e = pow(2,16) +1
    n = p * q

    phi = (p-1) * (q-1)
    de_msg = 159734044950403172452950888182831615189169981060911046776030041921878667289492
    d = pow(e,-1,phi)
    plaintext = pow(de_msg,d,n)
    plaintext_hex = hex(plaintext)[2:]
    if len(plaintext_hex)%2==1:
        plaintext_hex =  '0' + plaintext_hex
    bytes_object = bytes.fromhex(plaintext_hex)
    ascii_string = bytes_object.decode("ASCII")

def RSA_sig():
    n =  675165783015058999747250696593100898855524580839851357422716901254932757710763
    e = pow(2,16) +1

    sig_msg = 284741839593698522184778360417494843180877037145726733862568997913589354461044

    msg = pow(sig_msg,e,n)
    msg_hex = hex(msg)[2:]
    if len(msg_hex)%2==1:
        msg_hex =  '0' + msg_hex
    bytes_object = bytes.fromhex(msg_hex)
    ascii_string = bytes_object.decode("ASCII")



if __name__ == "__main__":

    RSA_en()

    RSA_de()

    RSA_sig()

    # Mersenne Primes
    print(sympy.isprime(pow(2,521) -1))
