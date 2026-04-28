from fractions import Fraction
from pathlib import Path

from research.four_distance.fiber_secant_search import (
    A_of_u,
    B_of_u_delta,
    C_of_u_delta,
    D_of_u_delta,
    DELTA_17,
    DELTA_730,
    U_17,
    U_730,
    fiber_point_status,
    in_S,
    point_from_u_delta,
    slope_defect,
)


def test_delta_730_u0_seed_values():
    A = A_of_u(U_730)
    B = B_of_u_delta(U_730, DELTA_730)
    C = C_of_u_delta(U_730, DELTA_730)
    D = D_of_u_delta(U_730, DELTA_730)
    assert A == Fraction(15, 8)
    assert B == Fraction(87, 416)
    assert C == Fraction(451, 780)
    assert D == Fraction(451, 87)
    assert slope_defect(B) == 1
    assert slope_defect(C) == 1
    assert slope_defect(D) == 730
    assert point_from_u_delta(U_730, DELTA_730) == (Fraction(416, 867), Fraction(260, 289))


def test_delta_17_seed_values():
    A = A_of_u(U_17)
    B = B_of_u_delta(U_17, DELTA_17)
    C = C_of_u_delta(U_17, DELTA_17)
    D = D_of_u_delta(U_17, DELTA_17)
    assert A == Fraction(8, 15)
    assert B == Fraction(28, 45)
    assert C == Fraction(7, 24)
    assert D == Fraction(1, 4)
    assert slope_defect(B) == 1
    assert slope_defect(C) == 1
    assert slope_defect(D) == 17
    assert point_from_u_delta(U_17, DELTA_17) == (Fraction(45, 52), Fraction(6, 13))


def test_d_fiber_delta_730_does_not_accept_u0():
    assert fiber_point_status("B", U_730, DELTA_730)
    assert fiber_point_status("C", U_730, DELTA_730)
    assert not fiber_point_status("D", U_730, DELTA_730)


def test_in_s_and_slope_defect_exact():
    assert in_S(Fraction(87, 416))
    assert slope_defect(Fraction(87, 416)) == 1
    assert not in_S(Fraction(451, 87))
    assert slope_defect(Fraction(451, 87)) == 730


def test_no_float_or_math_sqrt_for_exact_squarehood():
    source = Path("research/four_distance/fiber_secant_search.py").read_text(encoding="utf-8")
    assert "math.sqrt" not in source
    assert "float(" not in source
