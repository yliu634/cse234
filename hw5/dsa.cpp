#import cryptocommons as commons
def modInverse(a, p) :
    if a % p == 0:
        raise ZeroDivisionError("Impossible inverse")
    return pow(a, p-2, p)

print("key generation")

base = 3
p = 1279 #prime

#p = a * q + 1
def testPrimeness(number):
	for i in range(2, number):
		if number % i == 0:
			return False
			break
	return True

for i in range(10, p):
	if (p-1) % i == 0 and testPrimeness(i):
		q = i
		break

a = int((p-1)/q)
print(p," = ",a," * ",q," + 1")

g = pow(base, a, p) 

x = 15 # private key

y = pow(g, x, p)

print("private key: ",x)
print("public key: ",y)
print("public params: p=",p,", q=",q,", g=",g,"")

#-------------------------------

print("signing")

k = 10 #random key

h = 907333948972403931478241199054473720791704089052

r = pow(g, k, p) % q
s = modInverse(k, q) * (h + x*r) % q

print("signature: (r=",r,", s=",s,")")

#-------------------------------
print("verification")

h = 123

#Bob knows public key -> y
#Also, he knows public params -> p, q, g
#Also, he knows h, (r, s) pair

w = modInverse(s, q)
u1 = h * w % q
u2 = r * w % q
v = ((pow(g, u1, p) * pow(y, u2, p)) % p) % q

print("w:", w)
print("u1:", u1)
print("u2:", u2)
print("v:", v)

if v == r:
	print("signature is valid")
else:
	print("invalid signature is detected")
