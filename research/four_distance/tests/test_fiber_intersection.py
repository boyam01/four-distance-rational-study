from fractions import Fraction
from pathlib import Path

from research.four_distance.fiber_intersection_search import load_u_sets


def test_current_fiber_intersections_contain_known_chain():
    path = Path("research/four_distance/data/sage_fiber_points.csv")
    assert path.exists()
    sets = load_u_sets(path, Fraction(289, 260))
    U_B = set(sets["B"])
    U_C = set(sets["C"])
    U_D = set(sets["D"])
    assert U_B & U_C == {Fraction(3, 5)}
    assert U_C & U_D == {Fraction(15, 26)}
    assert U_B & U_D == set()
    assert U_B & U_C & U_D == set()


def test_intersection_no_float_or_math_sqrt_exact_tests():
    source = Path("research/four_distance/fiber_intersection_search.py").read_text(encoding="utf-8")
    assert "math.sqrt" not in source
    assert "float(" not in source
