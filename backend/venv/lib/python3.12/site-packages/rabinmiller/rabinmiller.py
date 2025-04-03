"""
Pure-Python implementation of the
`Rabin-Miller primality test <https://en.wikipedia.org/wiki/Rabin-Miller_primality_test>`__.
"""
from __future__ import annotations
import doctest
import secrets

def rabinmiller(number: int, rounds: int = 10) -> bool:
    # pylint: disable=too-many-branches
    """
    Pure-Python implementation of the Rabin-Miller primality test.

    :param number: Nonnegative integer to be tested for primality.
    :param rounds: Number of randomly generated base values to consider when testing.

    The Miller-Rabin primality test may return a false positive with low probability,
    but never returns a false negative. A return value of ``False`` guarantees that the
    input is composite; a return value of ``True`` indicates that there is a high
    likelihood that the input is prime.

    >>> rabinmiller(2)
    True
    >>> rabinmiller(4)
    False
    >>> rabinmiller(9999777777776655544433333333222111111111)
    True
    >>> rabinmiller(9999777777776655544433333333222111111115)
    False
    >>> rabinmiller(0) or rabinmiller(1)
    False
    >>> any(rabinmiller(i * i) for i in range(2, 1000))
    False

    Any attempt to invoke this function with an argument that does not
    have the expected types (or does not fall within the supported range)
    raises an exception.

    >>> rabinmiller('abc')
    Traceback (most recent call last):
      ...
    TypeError: number must be an integer
    >>> rabinmiller(-123)
    Traceback (most recent call last):
      ...
    ValueError: number must be a nonnegative integer
    >>> rabinmiller(123, 'abc')
    Traceback (most recent call last):
      ...
    TypeError: number of rounds must be an integer
    >>> rabinmiller(123, 0)
    Traceback (most recent call last):
      ...
    ValueError: number of rounds must be a positive integer
    """
    if not isinstance(number, int):
        raise TypeError('number must be an integer')

    if number < 0:
        raise ValueError('number must be a nonnegative integer')

    if not isinstance(rounds, int):
        raise TypeError('number of rounds must be an integer')

    if rounds < 1:
        raise ValueError('number of rounds must be a positive integer')

    if number in (0, 1):
        return False

    for prime in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if number == prime:
            return True
        if number % prime == 0:
            return False

    exponent = 0
    odd = number - 1
    while odd % 2 == 0:
        odd >>= 1
        exponent += 1

    for i in range(rounds):
        a = 2 + secrets.randbelow(number - 2)
        if pow(a, odd, number) == 1:
            continue
        composite = True
        for i in range(exponent):
            if pow(a, (2 ** i) * odd, number) == number - 1:
                composite = False
                break
        if composite:
            return False

    return True

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
