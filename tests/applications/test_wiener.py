import random

from tourbus.applications.wiener import (
    RSAKey,
    egcd,
    gen_prime,
    is_probable_prime,
    make_safe_key,
    make_vulnerable_key,
    modinv,
    wiener_attack,
)


def test_wiener_recovers_small_private_exponent():
    key = make_vulnerable_key(256, rng=random.Random(7))
    assert wiener_attack(key.e, key.n) == key.d


def test_recovered_key_actually_works():
    key = make_vulnerable_key(256, rng=random.Random(7))
    d = wiener_attack(key.e, key.n)
    # A recovered d must invert e modulo phi, i.e. decrypt.
    phi = (key.p - 1) * (key.q - 1)
    assert (key.e * d) % phi == 1
    message = 42
    cipher = pow(message, key.e, key.n)
    assert pow(cipher, d, key.n) == message


def test_safe_key_resists_the_attack():
    key = make_safe_key(256, rng=random.Random(11))
    assert key.e == 65537
    assert wiener_attack(key.e, key.n) is None


def test_textbook_example():
    # n = 379 * 239 = 90581, phi = 89964, d = 5, e = 17993.
    assert wiener_attack(17993, 90581) == 5


def test_vulnerable_key_is_a_valid_keypair():
    key = make_vulnerable_key(256, rng=random.Random(3))
    assert isinstance(key, RSAKey)
    assert key.p * key.q == key.n
    assert is_probable_prime(key.p) and is_probable_prime(key.q)
    phi = (key.p - 1) * (key.q - 1)
    assert (key.e * key.d) % phi == 1


def test_vulnerable_d_is_below_wiener_bound():
    key = make_vulnerable_key(256, rng=random.Random(5))
    from math import isqrt

    assert key.d < isqrt(isqrt(key.n)) // 3


def test_egcd_and_modinv():
    g, x, y = egcd(240, 46)
    assert g == 2 and 240 * x + 46 * y == 2
    assert modinv(17993, 89964) == 5
    assert (7 * modinv(7, 1000)) % 1000 == 1


def test_is_probable_prime_basics():
    assert is_probable_prime(2) and is_probable_prime(97)
    assert not is_probable_prime(1)
    assert not is_probable_prime(561)      # a Carmichael number, still composite
    small = [n for n in range(2, 30) if is_probable_prime(n)]
    assert small == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


def test_gen_prime_is_prime_and_sized():
    p = gen_prime(24, random.Random(0))
    assert is_probable_prime(p)
    assert p.bit_length() == 24
