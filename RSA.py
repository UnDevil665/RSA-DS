from hashlib import md5
from random import getrandbits, randint

def rmspp(number, attempts=28):
    """
    rmspp(n, attempts=28) -> True if n appears to be primary, else False
    rmspp: Rabin-Miller Strong Pseudoprime Test
    http://mathworld.wolfram.com/Rabin-MillerStrongPseudoprimeTest.html
    """
    if number < 2:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False
    # Given an odd integer n, let n = 2**r*s+1, with s odd...
    s = number - 1
    r = 0
    while s % 2 == 0:
        r += 1
        s //= 2
    while attempts:
        # ... choose a random integer a with 1 ≤ a ≤ n-1
        a = randint(1, number - 1)
        # Unless a**s % n ≠ 1 ...
        if mod_exp(a, s, number) != 1:
            # ... and a**((2**j)*s) % n ≠ -1 for some 0 ≤ j ≤ r-1
            for j in range(0, r):
                if mod_exp(a, (2 ** j) * s, number) == number - 1:
                    break
            else:
                return False
        attempts -= 1
        continue
    # A prime will pass the test for all a.
    return True


def mod_exp(base, exponent, modulus):
    """
    mod_exp(b, e, m) -> value of b**e % m
    Calculate modular exponentation using right-to-left binary method.
    http://en.wikipedia.org/wiki/Modular_exponentiation#Right-to-left_binary_method
    """
    result = 1
    while exponent > 0:
        if (exponent & 1) == 1:
            result = (result * base) % modulus
        exponent >>= 1
        base = (base * base) % modulus
    return result


def keys(bits):
    """
    keys(bits) -> (public, private)
    Generate public and private RSA keys of the given size.
    """
    # Pragma: use a fixed e, the fourth Fermat prime (0b10000000000000001)
    e = 2**16+1
    while True:
        # Generate two large prime numbers p and q, n = pq and φ = (p-1)(q-1)
        s = bits // 2
        mask = 0b11 << (s - 2) | 0b1  # two highest and the lowest bit
        while True:
            p = getrandbits(s) | mask
            # Pragma: check p % e here to guarantee that φ and e are coprimes
            if p % e != 1 and rmspp(p):
                break
        s = bits - s
        mask = 0b11 << (s - 2) | 0b1  # same as above, but maybe different s
        while True:
            q = getrandbits(s) | mask
            if q != p and q % e != 1 and rmspp(q):
                break
        n = p * q
        phi = (p - 1) * (q - 1)
        # Pragma: e is chosen already and is relative prime to φ
        # Compute d, a modular multiplicative inverse to e (i.e. e*d % φ = 1)
        d = mmi(e, phi)
        if d:  # if not, the process will repeat
            break
    return (n, e), (n, d)


def mmi(a, m):
    """
    mmi(a, m) -> x, such as ax % m = 1
    mmi is a Modular Multiplicative Inverse
    See http://en.wikipedia.org/wiki/Modular_multiplicative_inverse
    """
    gcd, x, q = egcd(a, m)
    if gcd != 1:
        # The a and m are not coprimes, so the inverse doesn't exist
        return None
    else:
        return (x + m) % m


def egcd(a, b):
    """
    egcd(a, b) -> d, x, y, such as d == gcd(a, b) == ax + by
    egcd is an Extended Greatest Common Divisor
    http://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
    """
    if b == 0:
        return a, 1, 0
    else:
        d, x, y = egcd(b, a % b)
        return d, y, x - y * (a // b)


def get_hash(string):
    hashes = md5(string.encode()).hexdigest()
    return hashes


def get_mod_exponentation(hashes, n, key):
    return hex(pow(int(hashes, 16), key, n))
