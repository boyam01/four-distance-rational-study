from fractions import Fraction
from pathlib import Path

from research.four_distance.reverse_closure_search import (
    generate_S,
    nondegenerate,
    rational_square,
    reverse_candidate_from_AD,
)
from research.four_distance.slope_tools import in_S, verify_seed


def test_known_three_distance_seeds_not_generated_when_D_not_in_S():
    slopes = set(generate_S(1000))
    seed_17 = verify_seed(52, 45, 24).slopes
    seed_730 = verify_seed(867, 416, 780).slopes

    assert seed_17.A in slopes
    assert seed_17.D not in slopes
    assert seed_730.A in slopes
    assert seed_730.D not in slopes


def test_degenerate_fake_family_filtered():
    assert reverse_candidate_from_AD(Fraction(1, 1), Fraction(3, 4)) is None
    assert reverse_candidate_from_AD(Fraction(0, 1), Fraction(3, 4)) is None
    assert reverse_candidate_from_AD(Fraction(5, 3), Fraction(1, 1)) is None
    assert nondegenerate(Fraction(5, 3), Fraction(3, 4), Fraction(0), Fraction(0)) is False


def test_reverse_candidates_have_exact_love_relation():
    slopes = generate_S(1000)
    found = []
    for A in slopes:
        for D in slopes:
            candidate = reverse_candidate_from_AD(A, D)
            if candidate is not None:
                found.append(candidate)
                assert candidate.love_relation_ok is True
                assert candidate.A * candidate.C == candidate.B * candidate.D == candidate.A + candidate.B - 1
                assert in_S(candidate.B)
                assert in_S(candidate.C)
    assert isinstance(found, list)


def test_rational_square_and_no_float_square_checks():
    assert rational_square(Fraction(49, 16))
    assert not rational_square(Fraction(50, 16))

    source = Path("research/four_distance/reverse_closure_search.py").read_text(encoding="utf-8")
    assert "math.sqrt" not in source
    assert "float(" not in source
