#!/usr/bin/env python3
"""Modular square sieve and small-defect checks for fiber search output."""

from __future__ import annotations

import argparse
import math
from functools import lru_cache
from fractions import Fraction
from typing import Optional

if __package__ in (None, ""):
    import os
    import sys
    from pathlib import Path

    sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[2]))
    from research.four_distance.slope_tools import is_square
else:
    from .slope_tools import is_square


def prime_list(limit: int) -> list[int]:
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    return [p for p in range(2, limit + 1) if sieve[p]]


@lru_cache(maxsize=None)
def quadratic_residues_mod(p: int) -> frozenset[int]:
    return frozenset((x * x) % p for x in range(p))


def is_square_mod_sieve(n: int, primes: list[int]) -> bool:
    """Return False if modular residues prove n is not a square."""
    if n < 0:
        return False
    for p in primes:
        if p <= 2:
            continue
        if n % p not in quadratic_residues_mod(p):
            return False
    return True


def slope_in_S_fast(alpha: Fraction, primes: list[int]) -> tuple[bool, str]:
    """Check alpha in S with modular rejection before exact isqrt."""
    a = alpha.numerator
    b = alpha.denominator
    for p in primes:
        if p <= 2:
            continue
        residue = ((a % p) * (a % p) + (b % p) * (b % p)) % p
        if residue not in quadratic_residues_mod(p):
            return False, f"failed_mod_{p}"
    n = a * a + b * b
    if is_square(n):
        return True, "exact_square"
    return False, "exact_not_square_after_sieve"


def squarefree_candidates_below(limit: int) -> list[int]:
    output: list[int] = []
    for n in range(2, limit + 1):
        squarefree = True
        for d in range(2, math.isqrt(n) + 1):
            square = d * d
            if n % square == 0:
                squarefree = False
                break
        if squarefree:
            output.append(n)
    return output


@lru_cache(maxsize=None)
def _squarefree_candidates_tuple(limit: int) -> tuple[int, ...]:
    return tuple(squarefree_candidates_below(limit))


def defect_below_limit(n: int, limit: int = 729) -> Optional[int]:
    """Return a squarefree k <= limit with n = k*square, if one exists."""
    if n <= 0:
        return None
    for k in _squarefree_candidates_tuple(limit):
        if n % k == 0 and is_square(n // k):
            return k
    return None


def slope_norm(alpha: Fraction) -> int:
    return alpha.numerator * alpha.numerator + alpha.denominator * alpha.denominator


def _self_test() -> None:
    primes = prime_list(200)
    assert slope_in_S_fast(Fraction(3, 4), primes) == (True, "exact_square")
    ok, reason = slope_in_S_fast(Fraction(1, 4), primes)
    assert not ok and reason.startswith("failed_mod_")
    assert is_square_mod_sieve(25, primes)
    assert not is_square_mod_sieve(26, primes)
    assert defect_below_limit(17 * 7 * 7, 729) == 17
    assert defect_below_limit(730 * 17 * 17, 729) is None
    assert defect_below_limit(729, 729) is None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--sieve-primes", type=int, default=2000)
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        print("modular_sieve_verifier self-test passed")
        return
    primes = prime_list(args.sieve_primes)
    print(f"loaded {len(primes)} primes <= {args.sieve_primes}")


if __name__ == "__main__":
    main()
