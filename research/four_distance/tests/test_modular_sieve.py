from fractions import Fraction
from pathlib import Path

from research.four_distance.modular_sieve_verifier import (
    defect_below_limit,
    is_square_mod_sieve,
    prime_list,
    slope_in_S_fast,
)


def test_modular_sieve_known_square_and_nonsquare():
    primes = prime_list(200)
    assert is_square_mod_sieve(25, primes)
    assert not is_square_mod_sieve(26, primes)
    assert slope_in_S_fast(Fraction(3, 4), primes) == (True, "exact_square")
    ok, reason = slope_in_S_fast(Fraction(1, 4), primes)
    assert ok is False
    assert reason.startswith("failed_mod_")


def test_defect_below_limit():
    assert defect_below_limit(17 * 7 * 7, 729) == 17
    assert defect_below_limit(730 * 17 * 17, 729) is None
    assert defect_below_limit(729, 729) is None


def test_modular_sieve_no_float_or_math_sqrt_exact_tests():
    source = Path("research/four_distance/modular_sieve_verifier.py").read_text(encoding="utf-8")
    assert "math.sqrt" not in source
    assert "float(" not in source
