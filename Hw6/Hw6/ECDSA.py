import numpy as np
import math
import sha3
import binascii
import sympy

    
def ECCAdd(a,b,p,P1,P2):
    P3 = np.zeros_like(P1)
    if np.sum(np.abs(P1-P2)) == 0:
        # s = ((3*P1[0]**2 + a)/(2*P1[1])) % p
        s = (3*P1[0]**2 + a) * sympy.mod_inverse(2*P1[1], p) % p
    else:
        # s = ((P2[1]-P1[1])/(P2[0]-P1[0])) % p
        s = (P2[1]-P1[1]) * sympy.mod_inverse(P2[0]-P1[0], p) % p
    P3[0] = (s**2 - P1[0] - P2[0]) % p
    P3[1] = (s*(P1[0] - P3[0]) - P1[1]) % p
    return P3


def nP(a,b,p,n,P):  # T = nP
    bin_n = bin(n)[2:]
    T = P.copy()
    for i in range(len(bin_n)-2,-1,-1):
        T = ECCAdd(a,b,p,T,T)
        if bin_n[len(bin_n) - i - 1] == '1':
            T = ECCAdd(a,b,p,T,P)
    return T
    

if __name__ == "__main__":
    a = -3
    b = 0x051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00
    # modulus
    p = 6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028291115057151
    # order
    q = 6864797660130609714981900799081393217269435300143305409394463459185543183397655394245057746333217197532963996371363321113864768612440380340372808892707005449 
    # Generator
    x = 0xc6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66
    y = 0x11839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650
    P = np.array([x,y])

    # private key
    pri_n = 1778570
    # public key
    pub_X = nP(a,b,p,pri_n,P)

    print("9. My public key X = ")
    print(pub_X)

    email = b'xzhan330@ucsc.edu'
    h_email = sha3.SHA3_512(email)
    h_email = binascii.hexlify(h_email)
    print("11. The SHA3-512 value = ")
    print(h_email)

    ekey_n = 758771
    R = nP(a,b,p,ekey_n,P)
    print("13. The entire point R = ")
    print(R)

    xr = pow(pri_n*R[0], 1, q)
    print("14. What is xr mod q (r is the x-axis of R): ")
    print(xr)
    n_inverse = pow(ekey_n, -1, q)
    print("15. What is n^{−1} mod q: ")
    print(n_inverse)

    # signature
    h_email  = int(h_email, 16)
    s = ((h_email + xr) * n_inverse)%q
    r = R[0]
    print("16. The signature (s, r): ")
    print(s)
    print(r)

    # Validation
    w = pow(s, -1, q)
    print("17. w = ")
    print(w)

    u_1 = pow(w*h_email, 1, q)
    u_2 = pow(w*r, 1, q)
    print("18. u_1 = ")
    print(u_1)
    print("19. u_2 = ")
    print(u_2)

    u_1P = nP(a,b,p,u_1,P)
    u2_X = nP(a,b,p,u_2,pub_X)
    V = ECCAdd(a,b,p,u_1P,u2_X)
    print("20. V = ")
    print(V)

    print("21. Is v = r ?")
    print(V[0] == (r %q))
