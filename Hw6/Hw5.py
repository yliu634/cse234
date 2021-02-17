import numpy as np
import math

def modInverse(a, m) :
    m0 = m
    y = 0
    x = 1
    if (m == 1) :
        return 0
    while (a > 1) :
        # q is quotient
        q = a // m
        t = m

        # m is remainder now, process
        # same as Euclid's algo
        m = a % m
        a = t
        t = y
        # Update x and y
        y = x - q * y
        x = t

    # Make x positive
    if (x < 0) :
        x = x + m0

    return x
    
def ECCAdd(a,b,p,P1,P2):
    P3 = np.zeros_like(P1)
    if np.sum(np.abs(P1-P2)) == 0:
        s = (3*P1[0]**2 + a) * modInverse(a = 2*P1[1], n = p) % p
    else:
        s = (P2[1]-P1[1]) * modInverse(a = P2[0]-P1[0], n = p) % p
    P3[0] = (s**2 - P1[0] - P2[0]) % p
    P3[1] = (s*(P1[0] - P3[0]) - P1[1]) % p
    return P3

def EEA(a,b,arr): 
    if b == 0:
        arr[0] = 1
        arr[1] = 0
        return a
    g = EEA(b, a % b, arr)
    t = arr[0]
    arr[0] = arr[1]
    arr[1] = t - a // b * arr[1]
    return g

def modInverse(a,n):
    if a == 0: 
        print('Neutral element obtained.')
        exit()
    arr = [0,1]
    gcd = EEA(a,n,arr)
    if gcd == 1:
        return (arr[0] % n + n) % n
    else:
        raise('gcd(a,b) not equals to 1')

    

if __name__ == "__main__":
    a = 654624412321892857559038596828572669649402987879847772735693306089759
    b = 563386056159714380473737077729260896240517015706612537779563193095411
    p = 1579602854473772853128287506817718026426265023617379175335587248616431
    x = 953216670857201615849458843136747040308850692140282160349854110301248
    y = 187696769665068572312633292858802066603155820538026405642457554453538
    n = 230768357842901099381188113760304602568543491144769691849643435691536

    T = np.array([x,y])
    P = np.array([x,y])

    bin_n = bin(n)[2:]
    for i in range(len(bin_n)-2,-1,-1):
        T = ECCAdd(a,b,p,T,T)
        if bin_n[len(bin_n) - i - 1] == '1':
            T = ECCAdd(a,b,p,T,P)
    print(T)
