from fractions import Fraction
from pathlib import Path

from research.four_distance.reverse_closure_search import generate_S
from research.four_distance.reverse_nearmiss import (
    build_raw_row,
    love_relation_ok,
    reverse_formula,
    slope_defect,
)
from research.four_distance.slope_tools import in_S


def test_reciprocal_fake_family_contains_three_fourths():
    A = Fraction(3, 4)
    D = Fraction(4, 3)
    B, C = reverse_formula(A, D)
    raw = build_raw_row(A, D, B, C)
    assert B == Fraction(-3, 4)
    assert C == Fraction(-4, 3)
    assert A + B == 0
    assert raw["reciprocal_fake"] is True
    assert raw["degenerate_infinity"] is True
    assert raw["nondegenerate"] is False


def test_slope_defects():
    assert slope_defect(Fraction(1, 4)) == 17
    assert slope_defect(Fraction(451, 87)) == 730
    assert in_S(Fraction(3, 4))
    assert slope_defect(Fraction(3, 4)) == 1


def test_love_relation_exact_for_raw_candidates():
    slopes = generate_S(100)
    raw_count = 0
    for A in slopes:
        for D in slopes:
            if A == 0 or D == 1:
                continue
            B, C = reverse_formula(A, D)
            if in_S(B) and in_S(C):
                raw_count += 1
                assert love_relation_ok(A, D, B, C)
    assert raw_count > 0


def test_reverse_nearmiss_no_float_square_checks():
    source = Path("research/four_distance/reverse_nearmiss.py").read_text(encoding="utf-8")
    assert "math.sqrt" not in source
    assert "float(" not in source
