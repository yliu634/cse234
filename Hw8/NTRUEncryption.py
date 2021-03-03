import numpy as np
import polynomial
import random

def generator(N, d1 = 5, d2 = None):
    if(d2 == None):
        d1, d2 = d1 + 1, d1;
    assert(d1 + d2 <= N);
    f = np.zeros(N);
    for i in range(d1 + d2):
        while 1:
            tmp = random.randint(0, N-1)
            if (f[tmp] == 0 and i < d1):
                f[tmp] = 1;
                break;
            elif (f[tmp] == 0 and i >= d1):
                f[tmp] = -1;
                break;
            else:
                continue;
    return f

def main():
    N, p, q, d = 251, 3, 257, 5;
    f = np.zeros(252)
    g = np.zeros(230)
    m = np.zeros(6)

    r = np.ones(4)
    polyr = polynomial.Polynomial(r)

    ring = np.zeros(252)
    ring[251] = 1
    ring[0] = -1
    polyring = polynomial.Polynomial(ring)

    for i in [251, 249, 211, 188, 107, 57]:
        f[i] = 1
    for i in [2, 8, 44, 46, 134]:
        f[i] = -1
    polyf = polynomial.Polynomial(f);

    for i in [192, 128, 92, 74, 29]:
        g[i] = -1
    for i in [229, 181, 103, 88, 33]:
        g[i] = 1

    polyg = polynomial.Polynomial(g)

    for i in [0, 2, 3]:
        m[i] = 1
    for i in [1, 5]:
        m[i] = -1
    polym = polynomial.Polynomial(m)

    fp = polyf.inverse(polyring, p)
    fq = polyf.inverse(polyring, q)

    print();
    print("6. fp_inverse's degree is {} and coefficient is {}".format(fp.degree(), fp.coefficients[fp.degree()]))
    print("7. fq_inverse's degree is {} and coefficient is {}".format(fq.degree(), fq.coefficients[fq.degree()]))
    hx = fq._polynomial_mul(polyg, q)
    print("8. hx's degree is {} and coefficient is {}".format(hx.degree(), hx.coefficients[hx.degree()]))
    e = polynomial.Polynomial(p) * hx * polyr
    e = polym._polynomial_add(e, q)

    print("9. The largest 4 terms are ", e)


if (__name__ == "__main__"):
    main()