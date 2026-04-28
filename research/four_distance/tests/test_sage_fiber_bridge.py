from fractions import Fraction
from pathlib import Path

from research.four_distance.sage_fiber_bridge import (
    A_of_u,
    B_of_u_delta,
    C_of_u_delta,
    D_of_u_delta,
    DELTA_17,
    DELTA_730,
    U_17,
    U_730,
    point_from_u_delta,
    slope_defect,
    two_good_one_bad,
    verify_point_row,
)


def test_bridge_delta_730_u0():
    A = A_of_u(U_730)
    B = B_of_u_delta(U_730, DELTA_730)
    C = C_of_u_delta(U_730, DELTA_730)
    D = D_of_u_delta(U_730, DELTA_730)
    assert A == Fraction(15, 8)
    assert B == Fraction(87, 416)
    assert C == Fraction(451, 780)
    assert D == Fraction(451, 87)
    assert (slope_defect(B), slope_defect(C), slope_defect(D)) == (1, 1, 730)
    assert point_from_u_delta(U_730, DELTA_730) == (Fraction(416, 867), Fraction(260, 289))


def test_delta_730_d_fiber_discovered_basepoint():
    u = Fraction(15, 26)
    w = Fraction(2125, 26)
    value = 2 * (
        8450 * u**4
        + 37570 * u**3
        + 25281 * u**2
        - 37570 * u
        + 8450
    )
    assert value == w * w


def test_bridge_delta_730_u_15_26():
    u = Fraction(15, 26)
    A = A_of_u(u)
    B = B_of_u_delta(u, DELTA_730)
    C = C_of_u_delta(u, DELTA_730)
    D = D_of_u_delta(u, DELTA_730)
    assert A == Fraction(780, 451)
    assert B == Fraction(87, 451)
    assert C == Fraction(8, 15)
    assert D == Fraction(416, 87)
    assert (slope_defect(B), slope_defect(C), slope_defect(D)) == (730, 1, 1)
    assert point_from_u_delta(u, DELTA_730) == (Fraction(451, 867), Fraction(260, 289))


def test_bridge_delta_17_seed_defects():
    B = B_of_u_delta(U_17, DELTA_17)
    C = C_of_u_delta(U_17, DELTA_17)
    D = D_of_u_delta(U_17, DELTA_17)
    defects = (slope_defect(B), slope_defect(C), slope_defect(D))
    assert sorted(defects) == [1, 1, 17]


def test_two_good_one_bad_classifier():
    assert two_good_one_bad((1, 1, 730)) == (True, 730)
    assert two_good_one_bad((730, 1, 1)) == (True, 730)
    assert two_good_one_bad((3301, 1481, 557)) == (False, None)
    assert two_good_one_bad((1, 730, 1)) == (True, 730)
    assert two_good_one_bad((1, 1, 1)) == (False, None)


def test_verify_point_row_known_730():
    row = {
        "delta": "289/260",
        "fiber": "B",
        "curve_label": "B_fiber",
        "u": "3/5",
        "W": "85",
        "source": "known_basepoint",
    }
    verified = verify_point_row(row)
    assert verified is not None
    assert verified["defect_B"] == 1
    assert verified["defect_C"] == 1
    assert verified["defect_D"] == 730
    assert verified["two_good_one_bad"] is True
    assert verified["remaining_defect"] == 730


def test_sage_bridge_no_float_or_math_sqrt_exact_tests():
    source = Path("research/four_distance/sage_fiber_bridge.py").read_text(encoding="utf-8")
    sage_source = Path("research/four_distance/sage_fiber_rank.sage").read_text(encoding="utf-8")
    assert "math.sqrt" not in source
    assert "math.sqrt" not in sage_source
    assert "float(" not in source
    assert "float(" not in sage_source
