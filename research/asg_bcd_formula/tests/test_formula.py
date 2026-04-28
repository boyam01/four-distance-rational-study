from fractions import Fraction
from pathlib import Path

from research.asg_bcd_formula import (
    bcd_from_u_delta,
    classify_defects,
    forward_closure_from_A_C,
    in_pythagorean_slope_set,
    is_square,
    reverse_closure_from_A_D,
    slope_defect,
    squarefree_part,
)


def test_exact_square_and_defect_helpers():
    assert is_square(0)
    assert is_square(2601)
    assert not is_square(833)
    assert squarefree_part(833) == 17
    assert squarefree_part(210970) == 730
    assert slope_defect(Fraction(451, 87)) == 730
    assert slope_defect(Fraction(1, 4)) == 17


def test_pythagorean_slope_membership():
    assert in_pythagorean_slope_set(Fraction(15, 8))
    assert in_pythagorean_slope_set(Fraction(87, 416))
    assert in_pythagorean_slope_set(Fraction(451, 780))
    assert not in_pythagorean_slope_set(Fraction(451, 87))


def test_delta_289_260_seed_730():
    point = bcd_from_u_delta(Fraction(3, 5), Fraction(289, 260))
    assert point.A == Fraction(15, 8)
    assert point.B == Fraction(87, 416)
    assert point.C == Fraction(451, 780)
    assert point.D == Fraction(451, 87)
    assert point.defects == (1, 1, 730)
    assert point.two_good_one_bad
    assert point.remaining_defect == 730
    assert (point.x, point.y) == (Fraction(416, 867), Fraction(260, 289))
    assert point.love_relation_ok
    assert point.point_in_unit
    assert point.as_dict()["runtime_effect"] == "none"


def test_delta_289_260_symmetry_partner():
    point = bcd_from_u_delta(Fraction(15, 26), Fraction(289, 260))
    assert point.A == Fraction(780, 451)
    assert point.B == Fraction(87, 451)
    assert point.C == Fraction(8, 15)
    assert point.D == Fraction(416, 87)
    assert point.defects == (730, 1, 1)
    assert point.two_good_one_bad
    assert point.remaining_defect == 730
    assert (point.x, point.y) == (Fraction(451, 867), Fraction(260, 289))
    assert point.love_relation_ok
    assert point.point_in_unit


def test_delta_13_6_defect_17_seed():
    point = bcd_from_u_delta(Fraction(1, 4), Fraction(13, 6))
    assert point.A == Fraction(8, 15)
    assert point.B == Fraction(28, 45)
    assert point.C == Fraction(7, 24)
    assert point.D == Fraction(1, 4)
    assert point.defects == (1, 1, 17)
    assert point.remaining_defect == 17
    assert (point.x, point.y) == (Fraction(45, 52), Fraction(6, 13))
    assert point.love_relation_ok


def test_forward_and_reverse_closure_exact():
    A = Fraction(15, 8)
    C = Fraction(451, 780)
    B, D = forward_closure_from_A_C(A, C)
    assert B == Fraction(87, 416)
    assert D == Fraction(451, 87)
    reverse_B, reverse_C = reverse_closure_from_A_D(A, D)
    assert reverse_B == B
    assert reverse_C == C


def test_defect_classifier():
    assert classify_defects((1, 1, 1)) == ("true_candidate", None)
    assert classify_defects((1, 1, 730)) == ("two_good_one_bad", 730)
    assert classify_defects((730, 1, 1)) == ("two_good_one_bad", 730)
    assert classify_defects((1, 730, 1)) == ("two_good_one_bad", 730)
    assert classify_defects((3301, 1481, 557)) == ("zero_good", None)


def test_no_float_squarehood():
    source = Path("research/asg_bcd_formula/formula.py").read_text()
    assert "math.sqrt" not in source
    assert "float(" not in source
    assert "isqrt" in source
